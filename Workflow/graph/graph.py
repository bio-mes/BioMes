import asyncio
import logging
import json
from typing import Literal, Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from langchain.chat_models import init_chat_model
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage
)
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from .state import (
    State,
    SubQuestionState,
    QueryAnalysis,
    AnswerCritique
)
from .prompt import *

import sys
sys.path.append("../BioMes/agentflow")
from tool import initialize_tools, get_all_tools


# Initialize logger
logger = logging.getLogger(__name__)


class BiologicalResearcher:
    def __init__(self, config):
        self.config = config
        self.max_retries = config.get("max_retries", 3)
        if config["llm"]["model_provider"].lower() == "zhipuai":
            self.llm = ChatZhipuAI(**config["llm"])
        else:
            self.llm = init_chat_model(**config["llm"])
        self.sem = asyncio.Semaphore(config["max_concurrency"])
        self.outer_sem = asyncio.Semaphore(1 + config["max_concurrency"] // 3)
        self.graph = self._build_graph()
        initialize_tools(config)

    def _build_graph(self):
        # Sub-graph for answering a single sub-question
        sub_graph = StateGraph(SubQuestionState)
        sub_graph.add_node("tool_agent", self.tool_agent)
        sub_graph.add_node("reasoner_agent", self.reasoner_agent)
        sub_graph.set_entry_point("tool_agent")
        sub_graph.add_edge("tool_agent", "reasoner_agent")
        sub_graph.set_finish_point("reasoner_agent")
        sub_graph = sub_graph.compile()

        graph = StateGraph(State)

        graph.add_node("answer_sub_question", sub_graph)
        graph.add_node("planner_agent", self.planner_agent)
        graph.add_node("critic_agent", self.critic_agent)
        graph.add_node("reporter_agent", self.reporter_agent)

        graph.add_edge(START, "planner_agent")
        graph.add_conditional_edges("planner_agent", self.parallel_answer, ["answer_sub_question"])
        graph.add_edge("answer_sub_question", "reporter_agent")
        graph.add_edge("reporter_agent", "critic_agent")
        graph.add_conditional_edges(
            "critic_agent",
            self.should_continue_research,
            {
                "back": "planner_agent",
                "next": END
            }
        )
        
        return graph.compile()

    def get_initial_state(self, query: str) -> State:
        return State(
            messages=[],
            query_type=self.config["query_type"],
            original_query=query,
            query=query,
            query_analysis=None,
            sub_questions=[],
            sub_answers=[],
            solved_sub_qas=None,
            final_answer=None,
            current_iteration=0,
            max_critique_iterations=self.config["max_critique_iterations"],
        )

    async def research(self, query: str, return_conversation: bool = False):
        async with self.outer_sem:
            # return await self._research(query, return_conversation)
            try:
                return await asyncio.wait_for(
                    self._research(query, return_conversation),
                    timeout=1200
                )
            except asyncio.TimeoutError:
                print(f"\n⚠️ Timeout processing query: {query[:30]}...")
                if return_conversation:
                    return ("Error: Timeout", "")
                else:
                    return "Error: Timeout"
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                # raise e
                if return_conversation:
                    return (f'Error: {str(e)}', "")
                else:
                    return f'Error: {str(e)}'

    async def _research(self, query: str, return_conversation: bool = False):
        # Initialize state
        initial_state = self.get_initial_state(query)

        final_state = await self.graph.ainvoke(initial_state, {"recursion_limit": 50})

        final_answer = final_state["final_answer"]

        if return_conversation:
            conversation = self._format_conversation(final_state["messages"])  # Skip initial system and human messages
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

    async def planner_agent(self, state: State) -> Dict[str, Any]:
        logger.info("🔍 Planner Agent: Analyzing input query...")
        
        query = state["query"]

        if state["query_type"] == "H":
            query = f"Below is a scientific hypothesis question that requires deep reasoning and analysis. The answer to the question DOES NOT exist in the existing data (literature, databases, etc.), you need to conduct logical analysis based on existing knowledge, and infer the answer to the question. You need to deeply reason about the possible influencing mechanisms rather than generalize with existing knowledge.\nQuestion: {query}"
        elif state["query_type"] == "MCQ":
            query = f'Multi-choice question (There is more than one correct answer): {query}'

        if self.config.get("structured_output_method"):
            llm_with_structure = self.llm.with_structured_output(QueryAnalysis, method=self.config["structured_output_method"]).with_retry(stop_after_attempt=self.max_retries)
        else:
            llm_with_structure = self.llm.with_structured_output(QueryAnalysis).with_retry(stop_after_attempt=self.max_retries)

        messages = [
            SystemMessage(content=QUERY_ANALYSIS_PROMPT),
            HumanMessage(content=query)
        ]

        async with self.sem:
            analysis_result = await llm_with_structure.ainvoke(messages)

        sub_questions = [f"{query}\nQuery type: {analysis_result.query_type}\nMain concepts: {', '.join(analysis_result.main_concepts)}"]
        sub_questions.extend(analysis_result.sub_questions)

        messages.append(
            AIMessage(content=f"type={analysis_result.query_type}, main concepts={analysis_result.main_concepts}, sub_questions={analysis_result.sub_questions}")
        )
        
        return {
            "messages": messages,
            "query_analysis": analysis_result,
            "sub_questions": sub_questions
        }
    
    def parallel_answer(self, state: State):
        """Create Send objects to distribute sub-questions for parallel processing"""            
        return [Send("answer_sub_question", {"id": chr(ord('A') + i), "sub_question": sq}) for i, sq in enumerate(state["sub_questions"])]

    async def tool_agent(self, state: SubQuestionState) -> Dict[str, Any]:
        query = state["sub_question"]
        if not query:
            return state

        logger.info(f"❔ Answering sub-question: {query}")
        logger.info("  📚 Tool Agent: Processing sub-question...")

        tools = get_all_tools()
        model_with_tools = self.llm.bind_tools(tools.values()).with_retry(stop_after_attempt=self.max_retries)

        tool_descriptions = "\n".join([f"- {name}: {tool.description}" for name, tool in tools.items()])
        
        messages = [
            SystemMessage(content=BIOMEDICAL_RESEARCH_SYSTEM_PROMPT),
            HumanMessage(content=TOOL_USAGE_PROMPT.format(query=query, tool_descriptions=tool_descriptions))
        ]

        async with self.sem:
            response = await model_with_tools.ainvoke(messages)
        
        state_tool_results = defaultdict(dict)
        state_tool_references = dict()
        if response.tool_calls:
            messages.append(response)
            
            tool_call_ids = []
            tool_names = []
            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool = tools.get(tool_name)
                if tool:
                    tool_result = await tool.ainvoke(tool_args)
                    tool_call_ids.append(tool_call["id"])
                    tool_names.append(tool_name)
                    tool_results.append(tool_result)
            # tool_results = await asyncio.gather(*tool_results)

            for j, (tool_call_id, tool_name, tool_result) in enumerate(zip(tool_call_ids, tool_names, tool_results)):
                tool_content = {}
                tool_references = {}
                if not isinstance(tool_result, list):
                    tool_result = [tool_result]
                for k, res in enumerate(tool_result):
                    tool_ref_id = f'{state["id"]}{chr(ord("a")+j)}{k}'
                    if 'content' in res:
                        tool_content[tool_ref_id] = res['content']
                        tool_references[tool_ref_id] = res['reference']
                    else:
                        tool_content[tool_ref_id] = res
                        tool_references[tool_ref_id] = {"text": str(res)[:100] + '...' if len(str(res)) > 100 else str(res), "link": ""}

                state_tool_results[tool_name].update(tool_content)
                state_tool_references.update(tool_references)
                messages.append(ToolMessage(tool_call_id=tool_call_id, name=tool_name, content=tool_result))

        return {
            "messages": messages,
            "tool_results": state_tool_results,
            "tool_references": state_tool_references
        }

    async def reasoner_agent(self, state: SubQuestionState) -> Dict[str, Any]:
        logger.info("  🧠 Reasoner Agent: Synthesizing analysis...")
        
        query = state["sub_question"]

        if "tool_results" in state and len(state["tool_results"]) != 0:
            tool_results = state["tool_results"]
            tool_results_text = "\n".join([f"## {name}\n{json.dumps(tool_result, ensure_ascii=False)}" for name, tool_result in tool_results.items()])
        else:
            tool_results_text = "No tool results."

        messages = [
            SystemMessage(content=BIOMEDICAL_RESEARCH_SYSTEM_PROMPT),
            HumanMessage(content=KNOWLEDGE_SYNTHESIS_PROMPT.format(
                query=query, 
                tool_results=tool_results_text
            ))
        ]

        llm = self.llm.with_retry(stop_after_attempt=self.max_retries)

        async with self.sem:
            synthesis_response = await llm.ainvoke(messages)

        return {
            "all_tool_references": state["tool_references"],
            "sub_answers": [synthesis_response.content],
            "messages": [synthesis_response]
        }

    async def reporter_agent(self, state: State) -> Dict[str, Any]:
        logger.info("📝 Reporter Agent: Organizing final answer...")

        query = state["query"]
        solved_sub_qas = dict(zip(state["sub_questions"], state["sub_answers"]))
        if state["solved_sub_qas"] is not None:
            solved_sub_qas = {**state["solved_sub_qas"], **solved_sub_qas}
        
        sub_qas = "\n\n".join([f"## Question\n{q}\n## Answer\n{a}" for q, a in solved_sub_qas.items()])

        if state["query_type"] == "MCQ":
            FINAL_ANSWER_PROMPT = PROMPT_FINAL_ANSWER_MCQ
        elif state["query_type"] == "QA":
            FINAL_ANSWER_PROMPT = PROMPT_FINAL_ANSWER_QA
        elif state["query_type"] == "H":
            FINAL_ANSWER_PROMPT = PROMPT_FINAL_ANSWER_H
        else:
            FINAL_ANSWER_PROMPT = FINAL_ANSWER_PROMPT_GENERAL

        messages = [
            SystemMessage(content=BIOMEDICAL_RESEARCH_SYSTEM_PROMPT),
            HumanMessage(content=FINAL_ANSWER_PROMPT.format(
                query=query,
                sub_qas=sub_qas
            ))
        ]

        llm = self.llm.with_retry(stop_after_attempt=self.max_retries)

        async with self.sem:
            report_response = await llm.ainvoke(messages)
        
        messages.append(report_response)

        return {
            "messages": messages,
            "final_answer": report_response.content,
            "solved_sub_qas": solved_sub_qas
        }

    async def critic_agent(self, state: State) -> Dict[str, Any]:
        logger.info("🔍 Critic Agent: Critiquing answer...")

        current_iteration = state["current_iteration"] + 1
        # Check if we've exceeded max iterations
        if current_iteration > state["max_critique_iterations"]:
            return {"current_iteration": current_iteration}

        query = state["query"]
        answer = state["final_answer"]
        
        if self.config.get("structured_output_method"):
            llm_with_structure = self.llm.with_structured_output(AnswerCritique, method=self.config["structured_output_method"]).with_retry(stop_after_attempt=self.max_retries)
        else:
            llm_with_structure = self.llm.with_structured_output(AnswerCritique).with_retry(stop_after_attempt=self.max_retries)

        messages = [
            SystemMessage(content=BIOMEDICAL_RESEARCH_SYSTEM_PROMPT),
            HumanMessage(content=CRITIQUE_PROMPT.format(
                query=query,
                answer=answer
            ))
        ]

        async with self.sem:
            critique_result = await llm_with_structure.ainvoke(messages)

        # Log critique result
        if critique_result.is_sufficient:
            logger.info(f"  ✅ Answer is sufficient: {critique_result.reasoning}")
        else:
            logger.info(f"  ⚠️ Answer is insufficient: {critique_result.reasoning}")
            logger.info(f"  📝 Missing aspects: {critique_result.missing_aspects}")
            if critique_result.new_sub_questions:
                logger.info(f"  🔄 New sub-questions generated: {critique_result.new_sub_questions}")

        # Update state with critique message
        messages.append(
            AIMessage(content=f"Critique completed: sufficient={critique_result.is_sufficient}, reasoning={critique_result.reasoning}")
        )
        return {
            "current_iteration": current_iteration,
            "messages": messages,
            "critique_result": critique_result
        }

    def should_continue_research(self, state: State) -> str:
        """Determine whether to continue research or end based on critique"""
        # Check if we've exceeded max iterations
        if state["current_iteration"] > state["max_critique_iterations"]:
            logger.info(f'⏹️ Max iterations ({state["max_critique_iterations"]}) reached, ending research')
            return "next"
        
        # Check critique result
        critique_result = state["critique_result"]
        
        if critique_result.is_sufficient:
            return "next"
        elif critique_result.new_sub_questions:
            num_sub_questions = len(state["solved_sub_qas"])
            state["sub_questions"] = critique_result.new_sub_questions
            logger.info(f"🔄 Continuing research (iteration {state['current_iteration']}/{state['max_critique_iterations']})...")
            # return "back"
            return [Send("answer_sub_question", {"id": chr(ord('A') + i + num_sub_questions), "sub_question": sq}) for i, sq in enumerate(state["sub_questions"])]
        
        return "next"
