"""State Definition and Data Structures - Biomedical Research Agent"""

import operator
from typing import Annotated, Optional, List, Dict, Any
from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState  
from pydantic import BaseModel, Field
from typing_extensions import TypedDict



class QueryAnalysis(BaseModel):
    """Query analysis result"""
    
    query_type: str = Field(
        description="Query type: knowledge retrieval, mechanistic investigation, comparative analysis, etc."
    )
    main_concepts: List[str] = Field(
        description="List of key biological concepts"
    )
    sub_questions: List[str] = Field(
        description="List of decomposed sub-questions"
    )


def merge_dicts(left: Dict[str, Dict[str, Any]], right: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {**left, **right}


class AnswerCritique(BaseModel):
    """Answer quality assessment result"""
    
    is_sufficient: bool = Field(
        description="Whether the answer sufficiently addresses the question"
    )
    reasoning: str = Field(
        description="Detailed reasoning for the assessment"
    )
    missing_aspects: List[str] = Field(
        default_factory=list,
        description="List of missing aspects or gaps in the answer"
    )
    new_sub_questions: List[str] = Field(
        default_factory=list,
        description="New sub-questions to address the gaps (only if is_sufficient is False)"
    )


class State(TypedDict):
    """Biomedical research workflow state"""
    config: Any
    messages: Annotated[list[MessageLikeRepresentation], operator.add]

    query_type: Optional[str]

    original_query: str
    query: str  # English query
    query_language: str

    query_analysis: Optional[QueryAnalysis]

    sub_questions: Optional[List[str]]  # For parallel processing
    sub_answers: Annotated[List[str], operator.add]  # To accumulate sub-answers
    all_tool_references: Annotated[Dict[str, Dict[str, Any]], merge_dicts]  # Accumulate all tool references

    solved_sub_qas: Optional[Dict[str, str]]  # Map of sub-question to answer
    critique_result: Optional[AnswerCritique]
    max_critique_iterations: int
    current_iteration: int

    query_type: Optional[str]
    final_answer: str

    processing_time: Optional[float]


class SubQuestionState(TypedDict):
    """Biomedical sub graph workflow state"""
    messages: list[MessageLikeRepresentation]

    id: str
    
    sub_question: Optional[str]

    tool_results: Dict[str, Dict[str, Any]]
    tool_references: Dict[str, Dict[str, Any]]

    sub_answers: Annotated[List[str], operator.add]
    all_tool_references: Annotated[Dict[str, Dict[str, Any]], merge_dicts]


