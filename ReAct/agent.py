import asyncio
import logging
import json
import re
from typing import Literal, Optional, Dict, Any, List, Tuple
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
    messages: Annotated[list, add_messages]
    current_iteration: int = 0


class Agent:
    def __init__(self, config):
        self.config = config
        self.max_retries = config.get("max_retries", 3)
        self.graph = self._build_graph()
        self.llm = init_chat_model(**config["llm"])
        self.sem = asyncio.Semaphore(config["max_concurrency"])
        initialize_tools(config)

    def _build_graph(self):
        graph = StateGraph(State)
        graph.add_node("think", self.think)
        graph.add_node("act", self.act)
        graph.add_node("answer", self.answer)

        graph.add_edge(START, "think")
        graph.add_conditional_edges(
            "think",
            self.should_continue,
            {
                "continue": "act",
                "end": END,
            },
        )
        graph.add_conditional_edges(
            "act",
            self.should_answer,
            {
                "continue": "think",
                "end": "answer",
            },
        )
        graph.add_edge("answer", END)

        return graph.compile()

    async def run(self, query: str, return_conversation: bool = False):
        if self.config["query_type"] == "MCQ":
            system_prompt = PROMPT_REACT_MCQ
        elif self.config["query_type"] == "QA":
            system_prompt = PROMPT_REACT_QA
        elif self.config["query_type"] == "H":
            system_prompt = PROMPT_REACT_H
        elif self.config["query_type"] == "SCQ":
            system_prompt = PROMPT_REACT_SCQ
        elif self.config["query_type"] == "LE":
            system_prompt = PROMPT_REACT_LE
        else:
            raise ValueError(f"Unsupported query type: {self.config['query_type']}")

        initial_state = State(
            messages=[
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ],
            current_iteration=0
        )

        try:
            final_state = await self.graph.ainvoke(initial_state, {"recursion_limit": 50})
            messages = final_state["messages"]
            final_answer = messages[-1].content
            match = re.search(r'<answer>(.*?)</answer>', final_answer, re.DOTALL)
            if match:
                final_answer = match.group(1).strip()
        except Exception as e:
            logger.error(f"Error during Agent run: {e}")
            final_answer = f'Error: {e}'
            messages = []

        if return_conversation:
            conversation = self._format_conversation(messages)  # Skip initial system and human messages
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

    async def think(self, state: State) -> Dict[str, Any]:
        """Think step: call the model to decide the next action."""
        logger.info("🧠 Thinking...")
        tools = get_all_tools()
        model_with_tools = self.llm.bind_tools(tools.values()).with_retry(stop_after_attempt=self.max_retries)

        async with self.sem:
            try:
                response = await model_with_tools.ainvoke(state["messages"])
            except Exception as e:
                logger.error(f"Error during think step: {e}")
                response = AIMessage(content=f"Error: {e}")
        
        return {
            "messages": [response],
            "current_iteration": state["current_iteration"] + 1
        }

    def should_continue(self, state: State) -> str:
        """Determine whether to continue the ReAct loop or end."""
        if state["messages"][-1].tool_calls:
            return "continue"
        else:
            return "end"

    async def act(self, state: State) -> Dict[str, Any]:
        """Action step: execute tool calls and return results."""
        logger.info("🎬 Taking action...")
        last_message = state["messages"][-1]
        tool_calls = last_message.tool_calls
        
        tools = get_all_tools()
        
        tool_messages = []
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
            if isinstance(result, list):
                result = [result.get("content", str(result)) if isinstance(result, dict) else str(result) for result in result]
            if isinstance(result, dict) and 'content' in result:
                result = result['content']
            
            logger.info(f"  - Tool {tool_name} result length: {len(str(result))}")
            tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
        
        return {"messages": tool_messages}

    def should_answer(self, state: State) -> str:
        if state["current_iteration"] > 10:
            return "end"
        else:
            return "continue"

    async def answer(self, state: State) -> Dict[str, Any]:
        state["messages"].append(HumanMessage(
            content="Now let's reason and answer the original question.")
        )

        llm = self.llm.with_retry(stop_after_attempt=self.max_retries)

        async with self.sem:
            try:
                response = await llm.ainvoke(state["messages"])
            except Exception as e:
                logger.error(f"Error during answer step: {e}")
                response = AIMessage(content=f"Error: {e}")

        return {"messages": [response]}