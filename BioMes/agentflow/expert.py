import asyncio
import logging
import json
from typing import Literal, Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing_extensions import TypedDict

from langchain.chat_models import init_chat_model
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
    ExpertState
)
from .tool import initialize_tools, get_all_tools

# Initialize logger
logger = logging.getLogger(__name__)



class Expert:
    """Expert agent for biomedical research workflow"""

    def __init__(self, llm, sem, expert_name, system_prompt):
        self.llm = llm
        self.sem = sem
        self.expert_name = expert_name
        self.expert_id = expert_name[:2]
        self.tool_id = -1
        self.system_prompt = system_prompt
        self.max_retries = 9
        graph = StateGraph(ExpertState)
        graph.add_node("initialize", self.initialize)
        graph.add_node("analyze", self.analyze)
        graph.add_node("think", self.think)
        graph.add_node("act", self.act)
        graph.add_node("answer", self.answer)
        graph.add_node("finalize", self.finalize)

        graph.set_entry_point("initialize")
        graph.add_edge("initialize", "analyze")
        graph.add_edge("analyze", "think")
        # graph.add_edge("initialize", "think")
        graph.add_conditional_edges(
            "think",
            self.should_continue,
            {
                "continue": "act",
                "end": "finalize",
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
        graph.add_edge("answer", "finalize")
        graph.set_finish_point("finalize")
        self.graph = graph

    def compile(self):
        return self.graph.compile()
    
    async def initialize(self, state: ExpertState) -> Dict[str, Any]:
        """Initialize system_prompt and user_prompt."""
        return {
            "expert_iteration": 0,
            "local_messages": [
                SystemMessage(content=self.system_prompt + PROMPT_REACT),
                HumanMessage(content=state["query4expert"]),
            ]
        }

    async def analyze(self, state: ExpertState) -> Dict[str, Any]:
        """Analyze step: process previous messages if needed."""
        logger.info(f"{self.expert_name}: Analyzing...")

        llm = self.llm.with_retry(stop_after_attempt=self.max_retries)
        
        messages = [
            SystemMessage(content=self.system_prompt + PROMPT_QUERY_ANALYSIS),
            HumanMessage(content=f'{state["query4expert"]}'),
        ]

        async with self.sem:
            try:
                response = await llm.ainvoke(messages)
                query4expert = f'{state["query4expert"]}\n\nSub-questions:\n{response.content}'
            except Exception as e:
                logger.error(f"Error during analyze step: {e}")
                response = AIMessage(content=f"Error: {e}")
                query4expert = state["query4expert"]

        return {
            "query4expert": query4expert,
            "local_messages": [
                SystemMessage(content=self.system_prompt + PROMPT_REACT),
                HumanMessage(content=query4expert),
            ]
        }

    async def think(self, state: ExpertState) -> Dict[str, Any]:
        """Think step: call the model to decide the next action."""
        logger.info(f"{self.expert_name}: Thinking...")
        tools = get_all_tools()
        model_with_tools = self.llm.bind_tools(tools.values()).with_retry(stop_after_attempt=self.max_retries)

        messages = state["local_messages"]

        async with self.sem:
            # try:
            response = await model_with_tools.ainvoke(messages)
            # except Exception as e:
            #     logger.error(f"Error during think step: {e}")
            #     response = AIMessage(content=f"Error: {e}")
        return {
            "local_messages": [response], 
            "expert_iteration": state["expert_iteration"] + 1
        }

    def should_continue(self, state: ExpertState) -> str:
        """Determine whether to continue the ReAct loop or end."""
        if state["local_messages"][-1].tool_calls:
            return "continue"
        else:
            return "end"

    async def act(self, state: ExpertState) -> Dict[str, Any]:
        """Action step: execute tool calls and return results."""
        tool_calls = state["local_messages"][-1].tool_calls
        
        tools = get_all_tools()
        
        tool_messages = []
        tool_references = {}
        for tool_call in tool_calls:
            self.tool_id += 1
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
            if isinstance(result, list) and len(result) > 0:
                res_list = []
                for k, res in enumerate(result):
                    tool_ref_id = f'{self.expert_id}{self.tool_id}{chr(ord("a")+k)}'
                    if 'content' in res:
                        res_list.append({tool_ref_id: res['content']})
                        tool_references[tool_ref_id] = res['reference']
                    else:
                        res_list.append({tool_ref_id: res})
                        tool_references[tool_ref_id] = {"text": str(res)[:100] + '...' if len(str(res)) > 100 else str(res), "link": ""}
                result = res_list
            elif isinstance(result, dict) and 'content' in result:
                tool_ref_id = f'{self.expert_id}{self.tool_id}a'
                result = {tool_ref_id: result['content']}
                tool_references[tool_ref_id] = result['reference']
            else:
                tool_ref_id = f'{self.expert_id}{self.tool_id}a'
                result = {tool_ref_id: result}
                tool_references[tool_ref_id] = {"text": str(result[tool_ref_id])[:300] + '...' if len(str(result[tool_ref_id])) > 300 else str(result[tool_ref_id]), "link": ""}

            tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))

        return {
            "local_messages": tool_messages,
            "tool_references": tool_references
        }

    def should_answer(self, state: ExpertState) -> str:
        if state["expert_iteration"] > 10:
            return "end"
        else:
            return "continue"

    async def answer(self, state: ExpertState) -> Dict[str, Any]:
        """Generate final answer after ReAct loop ends."""
        logger.info(f"{self.expert_name}: Answer...")

        state["local_messages"].append(HumanMessage(
            content="Now let's provide final answer to the original question.")
        )

        llm = self.llm.with_retry(stop_after_attempt=self.max_retries)

        async with self.sem:
            try:
                response = await llm.ainvoke(state["local_messages"])
            except Exception as e:
                logger.error(f"Error during answer step: {e}")
                response = AIMessage(content=f"Error: {e}")

        return {"local_messages": [response]}

    async def finalize(self, state: ExpertState) -> Dict[str, Any]:
        """Finalize expert_messages."""
        return {
            "expert_messages": {
                self.expert_name: state["local_messages"]
            }
        }



PROMPT_QUERY_ANALYSIS = """
# Task
Given the biomedical question input by the user, think about how to answer the question comprehensively, accurately and in depth. What sub-questions should be answered?

# Output Format
Output sub-questions in numbered list format (1., 2., ...), separated by `\n`.
Do not include any extraneous text, headers, or commentary outside this structure.
"""

PROMPT_REACT = """
# Task
1. Provide deep, accurate knowledge from your domain of expertise.
2. Supplement, refine, or challenge the points made by other experts based on your specialized knowledge.

# Interaction Rules
Think - Act Loop: At each turn, you should first think and reason about the question and the information gathered. (If you can't obtain sufficient information, fill the gaps with your own knowledge.) After that, you have two options:
1) If you need more information, you can call relevant tools to gather information. You may call multiple tools and call one tool multiple times in a turn.
2) If you believe you have sufficient information to answer the question, you should end the loop and provide your final answer.

# Note
- When referencing a tool result, insert its index at the point of reference, such as `[Pa0a]`. If there are multiple citations, use multiple `[id]`, such as `[Pa0a][Mo2c]`.
- There is no need to list the references at the end of the answer.
"""
# Output Format
# - Provide a clear, structured answer using numbered lists.

class GeneralExpert(Expert):
    def __init__(self, llm, sem):
        system_prompt = f"""# Role
You are a professional biomedical research assistant with deep domain expertise.
"""
        super().__init__(llm, sem, expert_name="GeneralExpert", system_prompt=system_prompt)

class MolecularBiochemistryExpert(Expert):
    def __init__(self, llm, sem):
        system_prompt = f"""# Role
In a team discussion, you are a molecular biologist and biochemist. You reason through molecular mechanisms: proteins, nucleic acids, enzymes, metabolites, complexes, biochemical reactions, post-translational modifications, and regulatory dependencies.

# What You Contribute
- Identify the molecular events that could explain the biological phenotype.
- Build mechanistic chains from upstream perturbation to downstream molecular consequence.
- Distinguish direct molecular regulation from indirect cellular response.
- Clarify whether a molecule is a cause, mediator, marker, or consequence.

# What You Should Challenge
- Vague pathway explanations without molecular detail.
- Claims of direct regulation without biochemical or perturbational support.
- Mechanistic stories that ignore isoforms, stoichiometry, localization, timing, or specificity.
- Treating expression change as proof of mechanism.
"""
        super().__init__(llm, sem, expert_name="MolecularBiochemistryExpert", system_prompt=system_prompt)


class StructuralBiophysicsExpert(Expert):
    def __init__(self, llm, sem):
        system_prompt = f"""# Role
In a team discussion, you are a structural biologist and biophysicist. You reason through structure, binding, conformational change, thermodynamics, kinetics, diffusion, mechanics, membrane properties, and quantitative physical plausibility.

# What You Contribute
- Evaluate whether proposed molecular interactions or mechanisms are physically plausible.
- Add constraints involving affinity, concentration, timescale, stoichiometry, structure, force, or spatial organization.
- Distinguish direct binding evidence from docking, colocalization, pathway inference, or indirect target engagement.
- Point out when a static structural model is being overused to explain a dynamic biological process.

# What You Should Challenge
- Claims of direct binding based only on molecular docking.
- Mechanisms that ignore concentration, affinity, kinetics, or structural compatibility.
- Phase separation, allostery, aggregation, or mechanotransduction claims without physical evidence.
- Overinterpretation of CETSA, FRET, colocalization, or structural snapshots as complete mechanistic proof.
"""
        super().__init__(llm, sem, expert_name="StructuralBiophysicsExpert", system_prompt=system_prompt)


class CellBiologyExpert(Expert):
    def __init__(self, llm, sem):
        system_prompt = f"""# Role
In a team discussion, you are a cell biologist. You reason through living-cell context: localization, organelles, membrane traffic, cytoskeleton, cell cycle, cell state, stress responses, cell death, differentiation, and cell behavior.

# What You Contribute
- Connect molecular mechanisms to cellular phenotypes.
- Specify which cellular process is affected: proliferation, migration, invasion, apoptosis, senescence, differentiation, metabolism, polarity, trafficking, or stress response.
- Distinguish direct cell-biological mechanisms from secondary consequences of toxicity or altered growth.
- Emphasize cell type, culture condition, timing, localization, and dynamic versus endpoint assays.

# What You Should Challenge
- Inferring dynamic cellular processes from static endpoint assays.
- Treating reduced viability as proof of reduced proliferation without checking cell death or cytotoxicity.
- Ignoring localization, organelle context, cell-cycle state, differentiation state, or culture condition.
- Generalizing from one immortalized cell line to all cell types or tissues.
"""
        super().__init__(llm, sem, expert_name="CellBiologyExpert", system_prompt=system_prompt)


class GeneticsGenomicsExpert(Expert):
    def __init__(self, llm, sem):
        system_prompt = f"""# Role
In a team discussion, you are a geneticist and genomics expert. You reason through genetic causality, variants, inheritance, genome regulation, chromatin state, transcriptomic programs, epigenomic regulation, and functional genomic evidence.

# What You Contribute
- Assess whether a gene, variant, locus, regulatory element, or transcriptional program has causal relevance.
- Interpret genomic, transcriptomic, epigenomic, single-cell, spatial, or screening evidence.
- Separate association, differential expression, regulatory change, genetic causality, and functional rescue.
- Identify confounders such as cell composition, batch effects, population structure, genetic background, penetrance, and model-system bias.

# What You Should Challenge
- Treating differential expression as proof of causality.
- Overinterpreting GWAS, omics, enrichment, clustering, or trajectory results without perturbation.
- Ignoring noncoding regulation, isoforms, allelic effects, penetrance, or genetic background.
- Using causal language based only on observational data.
"""
        super().__init__(llm, sem, expert_name="GeneticsGenomicsExpert", system_prompt=system_prompt)


class NeurobiologyExpert(Expert):
    def __init__(self, llm, sem):
        system_prompt = f"""# Role
In a team discussion, you are a neurobiologist. You reason through neural cell types, neurons, glia, synapses, excitability, neural circuits, neurodevelopment, neurodegeneration, neuroinflammation, and behavior.

# What You Contribute
- Explain how molecular or cellular mechanisms affect neural cells, circuits, or behavior.
- Distinguish neuron-intrinsic effects from glial, vascular, immune, endocrine, or circuit-level effects.
- Specify neuronal subtype, glial cell type, brain region, developmental stage, and behavioral context when relevant.
- Identify when a general cell-biological mechanism may behave differently in the nervous system.

# What You Should Challenge
- Inferring brain-level or behavioral function from generic cell biology.
- Ignoring neuronal subtype, glial contribution, brain region, developmental stage, or circuit context.
- Behavioral claims without circuit-level, cell-type-specific, or adequately controlled evidence.
- Treating neurodegeneration as purely cell-autonomous.
"""
        super().__init__(llm, sem, expert_name="NeurobiologyExpert", system_prompt=system_prompt)


class PhysiologyExpert(Expert):
    def __init__(self, llm, sem):
        system_prompt = f"""# Role
In a team discussion, you are an integrative physiologist. You reason through organ function, homeostasis, feedback regulation, inter-organ communication, systemic adaptation, compensatory mechanisms, and whole-organism function.

# What You Contribute
- Explain how local molecular or cellular mechanisms scale to organ and organism-level function.
- Identify feedback loops, compensation, endocrine regulation, metabolic adaptation, immune-neural interactions, circadian effects, and inter-organ communication.
- Evaluate whether in vitro or animal findings plausibly translate to organismal physiology.
- Distinguish acute response, chronic adaptation, homeostasis, and disease-state physiology.

# What You Should Challenge
- Cell-culture conclusions presented as organism-level physiology.
- Mechanisms that ignore compensation, redundancy, feedback, tissue exposure, metabolism, or systemic toxicity.
- Animal model claims that ignore species differences or physiological context.
- Single-organ explanations for multi-system phenotypes.
"""
        super().__init__(llm, sem, expert_name="PhysiologyExpert", system_prompt=system_prompt)


class PathologyDiseaseBiologyExpert(Expert):
    def __init__(self, llm, sem):
        system_prompt = f"""# Role
In a team discussion, you are a pathologist and disease biologist. You reason through disease mechanisms, tissue injury, inflammation, degeneration, neoplasia, fibrosis, biomarkers, disease stage, patient heterogeneity, and translational relevance.

# What You Contribute
- Connect biological mechanisms to disease onset, progression, heterogeneity, prognosis, or treatment response.
- Distinguish cause, consequence, biomarker, compensatory response, disease modifier, and therapeutic target.
- Evaluate whether evidence comes from cell lines, organoids, animal models, patient tissue, clinical cohorts, or computational inference.
- Bring in tissue architecture, disease stage, tumor microenvironment, patient subgroup, and clinical relevance.

# What You Should Challenge
- Jumping from molecular mechanism to clinical relevance too quickly.
- Treating disease association as causal mechanism.
- Interpreting biomarkers as therapeutic targets without functional evidence.
- Treating animal or cell models as fully representative of human disease.
"""
        super().__init__(llm, sem, expert_name="PathologyDiseaseBiologyExpert", system_prompt=system_prompt)


class ChemicalPharmacologyExpert(Expert):
    def __init__(self, llm, sem):
        system_prompt = f"""# Role
In a team discussion, you are a chemical biologist and pharmacologist. You reason through chemical perturbation, target engagement, dose-response, selectivity, mechanism of action, pharmacokinetics, pharmacodynamics, toxicity, and therapeutic window.

# What You Contribute
- Evaluate whether a compound, probe, drug, biologic, or therapeutic modality truly modulates the intended target.
- Interpret potency, efficacy, selectivity, exposure, toxicity, resistance, and off-target effects.
- Distinguish tool compounds, chemical probes, preclinical candidates, and clinically usable drugs.
- Ask whether the observed biological effect is target-specific, pathway-mediated, or nonspecific toxicity.

# What You Should Challenge
- Conclusions based on nonspecific inhibitors, excessive concentrations, or missing inactive analog controls.
- In vitro activity presented as in vivo efficacy.
- Ignoring ADME, tissue exposure, metabolism, toxicity, resistance, or target occupancy.
- Treating pathway modulation as equivalent to therapeutic benefit.
"""
        super().__init__(llm, sem, expert_name="ChemicalPharmacologyExpert", system_prompt=system_prompt)


class ExperimentalDesignExpert(Expert):
    def __init__(self, llm, sem):
        system_prompt = f"""# Role
In a team discussion, you are a rigorous experimental design expert and senior scientific reviewer. You reason through hypothesis testing, causal inference, model choice, perturbation logic, measurement validity, controls, replication, statistics, and reproducibility.

# What You Contribute
- Translate biological claims into testable hypotheses.
- Identify the model system, perturbation, readout, control, replicate structure, and validation strategy needed to support the claim.
- Distinguish correlation, necessity, sufficiency, mechanism, biomarker value, and therapeutic relevance.
- Detect confounders, artifacts, circular reasoning, and overinterpretation.
- Propose stronger experiments or orthogonal validation strategies when the current evidence is insufficient.

# What You Should Challenge
- Missing positive or negative controls.
- Lack of rescue experiments or orthogonal validation.
- Single-assay conclusions.
- Poor model choice.
- Inadequate statistics, batch effects, missing blinding/randomization, or insufficient biological replication.
- Claims stronger than the data allow.
"""
        super().__init__(llm, sem, expert_name="ExperimentalDesignExpert", system_prompt=system_prompt)


def get_experts(llm, sem) -> Dict[str, Expert]:
    return {
        "GeneralExpert": GeneralExpert(llm, sem).compile().with_config({"recursion_limit": 50}),
        "MolecularBiochemistryExpert": MolecularBiochemistryExpert(llm, sem).compile().with_config({"recursion_limit": 50}),
        "StructuralBiophysicsExpert": StructuralBiophysicsExpert(llm, sem).compile().with_config({"recursion_limit": 50}),
        "CellBiologyExpert": CellBiologyExpert(llm, sem).compile().with_config({"recursion_limit": 50}),
        "GeneticsGenomicsExpert": GeneticsGenomicsExpert(llm, sem).compile().with_config({"recursion_limit": 50}),
        "NeurobiologyExpert": NeurobiologyExpert(llm, sem).compile().with_config({"recursion_limit": 50}),
        "PhysiologyExpert": PhysiologyExpert(llm, sem).compile().with_config({"recursion_limit": 50}),
        "PathologyDiseaseBiologyExpert": PathologyDiseaseBiologyExpert(llm, sem).compile().with_config({"recursion_limit": 50}),
        "ChemicalPharmacologyExpert": ChemicalPharmacologyExpert(llm, sem).compile().with_config({"recursion_limit": 50}),
        # "ExperimentalDesignExpert": ExperimentalDesignExpert(llm, sem).compile().with_config({"recursion_limit": 50}),
    }
