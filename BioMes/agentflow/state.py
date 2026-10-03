"""State Definition and Data Structures - Biomedical Research Agent"""

import operator
from typing import Annotated, Optional, List, Dict, Any, Literal
from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState  
from pydantic import BaseModel, Field
from typing_extensions import TypedDict



class QueryAnalysis(BaseModel):
    """Query analysis result"""
    sub_questions: List[str] = Field(
        description="List of sub-questions to address the main question"
    )


Experts = Literal[
    "MolecularBiochemistryExpert", 
    "StructuralBiophysicsExpert",
    "CellBiologyExpert",
    "GeneticsGenomicsExpert",
    "NeurobiologyExpert",
    "PhysiologyExpert",
    "PathologyDiseaseBiologyExpert",
    "ChemicalPharmacologyExpert",
    # "ExperimentalDesignExpert"
]

class ExpertSelection(BaseModel):
    """Expert selection result"""
    
    selected_experts: List[Experts] = Field(
        description="List of selected expert names."
    )

class DiscussionSynthesis(BaseModel):
    """Discussion synthesis result"""
    
    consensus: Optional[str] = Field(
        description="Summary of consensus/agreement in the discussion. None if no consensus."
    )
    divergence: Optional[str] = Field(
        description="Summary of divergence/disagreement in the discussion. None if no divergence."
    )
    others: Optional[str] = Field(
        description="Summary of other viewpoints apart from consensus and divergence in the discussion. None if no others."
    )

class AnswerCritique(BaseModel):
    """Answer quality assessment result"""
    
    is_sufficient: bool = Field(
        description="Whether the answer sufficiently addresses the question"
    )
    reasoning: str = Field(
        description="Detailed reasoning for the assessment"
    )
    missing_aspects: Optional[str] = Field(
        description="Missing aspects or gaps in the answer"
    )
    new_sub_questions: Optional[str] = Field(
        description="New sub-questions to address the gaps (only if is_sufficient is False)"
    )

def replace(a, b):
    return b

def merge_dicts(left: Dict, right: Dict) -> Dict:
    return {**left, **right}

class State(TypedDict):
    """Biomedical research workflow state"""
    config: Any
    messages: Annotated[list[MessageLikeRepresentation], operator.add]

    query_type: Optional[str]

    original_query: str
    query: str   # English query
    query_language: str

    query_analysis: Optional[QueryAnalysis]
    query4expert: Annotated[str, replace]
    selected_experts: Optional[List[str]]

    tool_references: Annotated[Dict[str, Dict[str, Any]], merge_dicts]

    expert_messages: Annotated[Dict[str, list[MessageLikeRepresentation]], merge_dicts]

    discussion_synthesis: Optional[DiscussionSynthesis]

    critique_result: Optional[AnswerCritique]
    max_critique_iterations: int
    current_iteration: int

    final_answer: str


class ExpertState(TypedDict):
    query4expert: str
    local_messages: Annotated[list[MessageLikeRepresentation], operator.add]
    expert_messages: Annotated[Dict[str, list[MessageLikeRepresentation]], merge_dicts]
    tool_references: Annotated[Dict[str, Dict[str, Any]], merge_dicts]
    expert_iteration: int = 0



