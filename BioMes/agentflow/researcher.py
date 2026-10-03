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

from .tool import initialize_tools, get_all_tools
from .state import *
from .prompt import *
from .expert import *

# Initialize logger
logger = logging.getLogger(__name__)


class BiologicalResearcher:
    def __init__(self, config):
        self.config = config
        self.max_retries = config.get("max_retries", 3)
        if "model_provider" in config["llm"] and config["llm"]["model_provider"].lower() == "zhipuai":
            self.llm = ChatZhipuAI(**config["llm"])
        else:
            self.llm = init_chat_model(**config["llm"])
        # self.llm = init_chat_model(**config["llm"])
        self.sem = asyncio.Semaphore(config["max_concurrency"])
        self.outer_sem = asyncio.Semaphore(1 + config["max_concurrency"] // 3)
        self.graph = self._build_graph()
        initialize_tools(config)

    def _build_graph(self):
        graph = StateGraph(State)

        experts = get_experts(self.llm, self.sem)

        graph.add_node("translate_query", self.translate_query)
        # graph.add_node("analyst", self.analyst)
        graph.add_node("coordinator", self.coordinator)
        for expert_name, expert_complied in experts.items():
            graph.add_node(expert_name, expert_complied)
        graph.add_node("synthesizer", self.synthesizer)
        graph.add_node("answerer", self.answerer)
        graph.add_node("critic", self.critic)
        graph.add_node("translate_answer", self.translate_answer)

        graph.add_edge(START, "translate_query")
        # graph.add_edge("translate_query", "analyst")
        # graph.add_edge("analyst", "coordinator")
        graph.add_edge("translate_query", "coordinator")
        graph.add_conditional_edges(
            "coordinator", 
            self.route_to_experts, 
        )
        for expert_name in experts.keys():
            graph.add_edge(expert_name, "synthesizer")
        graph.add_edge("synthesizer", "answerer")
        graph.add_edge("answerer", "critic")
        graph.add_conditional_edges(
            "critic",
            self.should_continue_research,
            {
                "back": "coordinator",
                "next": "translate_answer"
            }
        )
        graph.add_edge("translate_answer", END)
        
        return graph.compile()

    def get_initial_state(self, query: str) -> State:
        if self.config["query_type"] == "H":
            query = f"Below is a scientific hypothesis question that requires deep reasoning and analysis. The answer to the question DOES NOT exist in the existing data (literature, databases, etc.), you need to conduct logical analysis based on existing knowledge, and infer the answer to the question. You need to deeply reason about the possible influencing mechanisms rather than generalize with existing knowledge.\nQuestion: {query}"
        elif self.config["query_type"] == "MCQ":
            query = f'Multi-choice question (There is more than one correct answer): {query}'

        return State(
            messages=[],
            query_type=self.config["query_type"],
            original_query=query,
            query=query,
            query4expert=query,
            # query_language="Chinese" if any('\u4e00' <= c <= '\u9fff' for c in query) else "English",
            query_language="English",
            expert_messages={},
            sub_questions=[],
            sub_answers=[],
            solved_sub_qas=None,
            final_answer="",
            current_iteration=0,
            max_critique_iterations=self.config["max_critique_iterations"],
        )

    async def research(self, query: str, return_conversation: bool = False) -> Dict[str, Any]:
        async with self.outer_sem:
            # return await self._research(query, return_conversation)
            try:
                return await asyncio.wait_for(
                    self._research(query, return_conversation),
                    timeout=1800
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

    async def _research(self, query: str, return_conversation: bool = False) -> Dict[str, Any]:
        initial_state = self.get_initial_state(query)

        # try:
        final_state = await self.graph.ainvoke(initial_state, {"recursion_limit": 50})
        # except Exception as e:
        #     logger.error(f"Error during research: {e}")
        #     final_state = initial_state

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

    async def translate_query(self, state: State) -> Dict[str, Any]:
        """Translation step for Chinese queries"""
        # If query is in English, skip translation
        if state["query_language"] == "English":
            return {}
        
        # Translate Chinese query to English
        logger.info("🔄 Translating Chinese query to English...")
        messages = [
            SystemMessage(content=BIOMEDICAL_RESEARCH_SYSTEM_PROMPT),
            HumanMessage(content=TRANSLATION_PROMPT.format(target_language="English", text=state["original_query"]))
        ]

        llm = self.llm.with_retry(stop_after_attempt=self.max_retries)

        async with self.sem:
            response = await llm.ainvoke(messages)
        
        translated_query = response.content.strip()

        messages.append(response)

        return {
            "query": translated_query,
            "query4expert": translated_query,
            "messages": messages
        }

    async def analyst(self, state: State) -> Dict[str, Any]:
        logger.info("Analyst: Analyzing input query...")
        
        query = state["query"]

        messages = [
            SystemMessage(content=QUERY_ANALYSIS_PROMPT),
            HumanMessage(content=query)
        ]

        if self.config.get("structured_output_method"):
            llm_with_structure = self.llm.with_structured_output(QueryAnalysis, method=self.config["structured_output_method"]).with_retry(stop_after_attempt=self.max_retries)
        else:
            llm_with_structure = self.llm.with_structured_output(QueryAnalysis).with_retry(stop_after_attempt=self.max_retries)

        query_analysis = await llm_with_structure.ainvoke(messages)

        messages.append(AIMessage(content=str(query_analysis)))
        query4expert = f'{query}\n{str(query_analysis)}'
        
        return {
            "query_analysis": query_analysis,
            "query4expert": query4expert,
            "messages": messages
        }

    async def coordinator(self, state: State) -> Dict[str, Any]:
        logger.info("Coordinator: Select experts...")

        messages = [
            SystemMessage(content=EXPERT_SELECTION_PROMPT),
            HumanMessage(content=state["query4expert"])
        ]

        if self.config.get("structured_output_method"):
            llm_with_structure = self.llm.with_structured_output(ExpertSelection, method=self.config["structured_output_method"]).with_retry(stop_after_attempt=self.max_retries)
        else:
            llm_with_structure = self.llm.with_structured_output(ExpertSelection).with_retry(stop_after_attempt=self.max_retries)

        selected_experts = await llm_with_structure.ainvoke(messages)

        if selected_experts is None:
            logger.warning("ExpertSelection is None, defaulting to GeneralExpert")
            selected_experts = ExpertSelection(selected_experts=["GeneralExpert"])

        messages.append(AIMessage(content=str(selected_experts)))
        
        return {
            "selected_experts": selected_experts.selected_experts,
            "messages": messages
        }

    def route_to_experts(self, state: State) -> List[str]:
        """Decide which experts to invoke based on query analysis"""
        return state["selected_experts"]

    async def synthesizer(self, state: State) -> Dict[str, Any]:
        logger.info("Synthesizer: Analyzing discussion content...")

        query = state["query"]
        discussion = "\n\n".join([
            f'[{expert}]\n{state["expert_messages"][expert][-1].content}'
            for expert in state["selected_experts"]
        ])

        messages = [
            SystemMessage(content=BIOMEDICAL_RESEARCH_SYSTEM_PROMPT),
            HumanMessage(content=SYNTHESIS_PROMPT.format(
                query=query,
                discussion=discussion
            ))
        ]

        if self.config.get("structured_output_method"):
            llm_with_structure = self.llm.with_structured_output(DiscussionSynthesis, method=self.config["structured_output_method"]).with_retry(stop_after_attempt=self.max_retries)
        else:
            llm_with_structure = self.llm.with_structured_output(DiscussionSynthesis).with_retry(stop_after_attempt=self.max_retries)

        async with self.sem:
            discussion_synthesis = await llm_with_structure.ainvoke(messages)
        
        messages.append(AIMessage(content=str(discussion_synthesis)))
        
        return {
            "messages": messages,
            "discussion_synthesis": discussion_synthesis,
        }

    async def answerer(self, state: State) -> Dict[str, Any]:
        logger.info("Answerer: Organizing final answer...")

        if state["query_type"] == "MCQ":
            FINAL_ANSWER_PROMPT = PROMPT_FINAL_ANSWER_MCQ
        elif state["query_type"] == "QA":
            FINAL_ANSWER_PROMPT = PROMPT_FINAL_ANSWER_QA
        elif state["query_type"] == "H":
            FINAL_ANSWER_PROMPT = PROMPT_FINAL_ANSWER_H
        elif state["query_type"] == "SCQ":
            FINAL_ANSWER_PROMPT = PROMPT_FINAL_ANSWER_SCQ
        elif state["query_type"] == "L":
            FINAL_ANSWER_PROMPT = PROMPT_FINAL_ANSWER_L
        else:
            FINAL_ANSWER_PROMPT = PROMPT_FINAL_ANSWER_GENERAL

        messages = [
            SystemMessage(content=FINAL_ANSWER_PROMPT),
            HumanMessage(content=(
                f'# Question\n{state["query"]}\n\n'
                f'# Discussion\n\n'
                f'## Consensus:\n{state["discussion_synthesis"].consensus}\n\n'
                f'## Divergence:\n{state["discussion_synthesis"].divergence}\n\n'
                f'## Others:\n{state["discussion_synthesis"].others}'
            ))
        ]

        llm = self.llm.with_retry(stop_after_attempt=self.max_retries)

        async with self.sem:
            response = await llm.ainvoke(messages)
        
        messages.append(response)
        
        return {
            "messages": messages,
            "final_answer": response.content.strip()
        }

    async def critic(self, state: State) -> Dict[str, Any]:
        logger.info("Critic: Critiquing answer...")

        current_iteration = state["current_iteration"] + 1
        # Check if we've exceeded max iterations
        if current_iteration > state["max_critique_iterations"]:
            return {"current_iteration": current_iteration}

        query = state["query"]
        answer = state["final_answer"]

        messages = [
            SystemMessage(content=BIOMEDICAL_RESEARCH_SYSTEM_PROMPT),
            HumanMessage(content=CRITIQUE_PROMPT.format(
                query=query,
                answer=answer
            ))
        ]
        
        if self.config.get("structured_output_method"):
            llm_with_structure = self.llm.with_structured_output(AnswerCritique, method=self.config["structured_output_method"]).with_retry(stop_after_attempt=self.max_retries)
        else:
            llm_with_structure = self.llm.with_structured_output(AnswerCritique).with_retry(stop_after_attempt=self.max_retries)

        critique_result = await llm_with_structure.ainvoke(messages)

        messages.append(AIMessage(content=str(critique_result)))

        if critique_result is None:
            critique_result = AnswerCritique(is_sufficient=True, reasoning="", missing_aspects=None, new_sub_questions=None)
        
        if not critique_result.is_sufficient and critique_result.new_sub_questions:
            query4expert = (
                f'{state["query4expert"]}\n'
                f'# Expert Discussion Results:\n'
                f'## Consensus:\n{state["discussion_synthesis"].consensus}\n'
                f'## Divergence:\n{state["discussion_synthesis"].divergence}\n'
                f'## Others:\n{state["discussion_synthesis"].others}\n'
                f'# Additional Sub-questions to Address:\n{critique_result.new_sub_questions}'
            )
        else:
            query4expert = state["query4expert"]

        return {
            "current_iteration": current_iteration,
            "messages": messages,
            "critique_result": critique_result,
            "query4expert": query4expert,
        }

    def should_continue_research(self, state: State) -> str:
        """Determine whether to continue research or end based on critique"""
        
        # Check if we've exceeded max iterations
        if state["current_iteration"] > state["max_critique_iterations"]:
            logger.info(f'⏹️ Max iterations ({state["max_critique_iterations"]}) reached, ending research')
            return "next"

        if not state["critique_result"].is_sufficient and state["critique_result"].new_sub_questions:
            logger.info(f"🔄 Continuing research (iteration {state['current_iteration']}/{state['max_critique_iterations']})...")
            return "back"
        
        return "next"

    async def translate_answer(self, state: State) -> Dict[str, Any]:
        """Translation final report to Chinese if needed"""
        # If query is in English, skip translation
        if state["query_language"] == "English":
            return {}
        
        # Translate Chinese query to English
        logger.info("🔄 Translating final answer...")
        
        messages = [
            SystemMessage(content=BIOMEDICAL_RESEARCH_SYSTEM_PROMPT),
            HumanMessage(content=TRANSLATION_PROMPT.format(target_language=state["query_language"], text=state["final_answer"]))
        ]

        llm = self.llm.with_retry(stop_after_attempt=self.max_retries)

        async with self.sem:
            response = await llm.ainvoke(messages)
        
        translated_answer = response.content.strip()

        messages.append(response)

        return {
            "messages": messages,
            "final_answer": translated_answer
        }

