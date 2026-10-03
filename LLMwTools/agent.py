import asyncio
import logging
import json
import re
from typing import Literal, Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from langchain.chat_models import init_chat_model
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage
)
from langchain_core.runnables import RunnableConfig
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages

from prompt import *

import sys
sys.path.append("../BioMes/agentflow")
from tool import initialize_tools, get_all_tools


logger = logging.getLogger(__name__)


class State(TypedDict):
    query: str
    messages: Annotated[list, add_messages]
    tool_results: Optional[Dict[str, Any]]


class Agent:
    def __init__(self, config):
        self.config = config
        self.max_retries = config.get("max_retries", 3)
        self.llm = init_chat_model(**config["llm"])
        self.outer_sem = asyncio.Semaphore(config["max_concurrency"])
        self.graph = self._build_graph()
        initialize_tools(config)

    def _build_graph(self):
        graph = StateGraph(State)
        graph.add_node("think", self.think)
        graph.add_node("act", self.act)
        graph.add_node("answer", self.answer)

        graph.add_edge(START, "think")
        graph.add_edge("think", "act")
        graph.add_edge("act", "answer")
        graph.add_edge("answer", END)

        return graph.compile()

    async def run(self, query: str, return_conversation: bool = False):
        async with self.outer_sem:
            return await self._run(query, return_conversation)

    async def _run(self, query: str, return_conversation: bool = False):
        initial_state = State(
            query=query,
            messages=[
                SystemMessage(content=PROMPT_SYSTEM),
                HumanMessage(content=query)
            ]
        )

        final_state = await self.graph.ainvoke(initial_state)

        final_answer = final_state["messages"][-1].content

        if return_conversation:
            conversation = self._format_conversation(final_state["messages"])
            return final_answer, conversation
        else:
            return final_answer

    def _format_conversation(self, messages: List[Any]) -> str:
        formatted_messages = []
        for message in messages:
            role = getattr(message, "type", message.__class__.__name__).upper()
            content = message.content
            if isinstance(content, list):
                content = "\n".join(str(part["content"]) for part in content)
                formatted_messages.append(f"[{role}] {content}")
            else:
                formatted_messages.append(f"[{role}] {content}")

        return "\n\n".join(formatted_messages)

    async def think(self, state: State) -> State:
        """Think step: call the model to decide the next action."""
        logger.info("🧠 Thinking...")
        tools = get_all_tools()
        model_with_tools = self.llm.bind_tools(tools.values()).with_retry(stop_after_attempt=self.max_retries)

        response = await model_with_tools.ainvoke(state["messages"])

        return {"messages": [response]}

    async def act(self, state: State) -> State:
        """Action step: execute tool calls and return results."""
        logger.info("🎬 Taking action...")
        last_message = state["messages"][-1]
        tool_calls = last_message.tool_calls
        
        tools = get_all_tools()
        
        tool_messages = []
        tool_results = defaultdict(list)
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            logger.info(f"  - Calling tool: {tool_name}")
            tool = tools.get(tool_name)
            if not tool:
                result = f"Error: Tool '{tool_name}' not found."
            else:
                try:
                    result = await tool.ainvoke(tool_call["args"])
                except Exception as e:
                    result = f"Error executing tool {tool_name}: {e}"
            if 'content' in result:
                result = result['content']
            if isinstance(result, list):
                result = [result.get("content", str(result)) if isinstance(result, dict) else str(result) for result in result]
                tool_results[tool_name].extend(result)
            elif isinstance(result, dict) and 'content' in result:
                result = result['content']
                tool_results[tool_name].append(result)
            else:
                tool_results[tool_name].append(result)
            tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
        
        return {
            "messages": tool_messages,
            "tool_results": tool_results
        }
    
    async def answer(self, state: State) -> State:
        """Think step: call the model to decide the next action."""
        logger.info("🔑 Answer...")
        if self.config["query_type"] == "MCQ":
            system_prompt = PROMPT_ANSWER_MCQ
        elif self.config["query_type"] == "QA":
            system_prompt = PROMPT_ANSWER_QA
        elif self.config["query_type"] == "H":
            system_prompt = PROMPT_ANSWER_H
        elif self.config["query_type"] == "SCQ":
            system_prompt = PROMPT_ANSWER_SCQ

        user_prompt = f'# Information:\n{str(state["tool_results"])}\n\n# Question:\n{state["query"]}'

        messages=[
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        llm = self.llm.with_retry(stop_after_attempt=self.max_retries)

        try:
            response = await llm.ainvoke(messages)
        except Exception as e:
            response = AIMessage(content=f"Error: {e}")
        
        messages.append(response)

        return {"messages": messages}