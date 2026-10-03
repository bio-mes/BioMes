BIOMEDICAL_RESEARCH_SYSTEM_PROMPT = """# Role
You are a professional biomedical research assistant with deep domain expertise."""


TRANSLATION_PROMPT = """
Please translate the given text to target language. 

# Requirements:
1. Maintain accuracy of biomedical terminology
2. Return directly if original text is already in target language
3. Preserve original format and structure
4. Use standard translations for technical terms
5. Directly ouput the translated text without additional commentary

# Target language:
{target_language}

# Given text:
{text}
"""


QUERY_ANALYSIS_PROMPT = """# Role
You are a professional biomedical research assistant with deep domain expertise.

# Task
Given the biomedical question input by the user, think about how to answer the question comprehensively, accurately and in depth. What sub-questions should be answered? Output them in JSON format.
"""

QUERY_ANALYSIS_PROMPT_EXAMPLE = """
# Output JSON Format
{
    "sub_questions": [List of sub-questions to address the main question],
}
"""
QUERY_ANALYSIS_PROMPT += QUERY_ANALYSIS_PROMPT_EXAMPLE

EXPERT_SELECTION_PROMPT = """# Role
You are a professional biomedical research assistant with deep domain expertise.

# Task
Based on the user's query and its analysis, select the most relevant experts to address the query from the following list:
- MolecularExpert: Expert in molecular biology, proteins, genes, and cellular mechanisms.
- PathwayExpert: Expert in biological pathways, signaling cascades, and systems biology.
- OrganelleExpert: Expert in cellular organelles and their functions.
- DiseaseExpert: Expert in diseases, clinical implications, and therapeutic strategies.
- PharmacologyExpert: Expert in drug mechanisms, pharmacodynamics, and pharmacokinetics.
- MethodExpert: Expert in experimental techniques, protocols, and methodologies.
"""

EXPERT_SELECTION_PROMPT_EXAMPLE = """
# Output JSON Format
{
    "selected_experts": [List of selected expert names.]
}
"""
EXPERT_SELECTION_PROMPT += EXPERT_SELECTION_PROMPT_EXAMPLE


SYNTHESIS_PROMPT = """# Task
Based on the question and expert discussion, summarize the consensus, divergence and others among various viewpoints in the format of numbered bullet (1., 2., 3., ...).

# Note
Keep the reference marker at the citation points, such as `[Pa1a]`.

# Question
{query}

# Discussion
{discussion}
"""

SYNTHESIS_PROMPT_EXAMPLE = """
# Output JSON Format
{{
    "consensus": "Summary of consensus/agreement in the discussion. None if no consensus.",
    "divergence": "Summary of divergence/disagreement in the discussion. None if no divergence.",
    "others": "Summary of other viewpoints apart from consensus and divergence in the discussion. None if no others."
}}
"""
SYNTHESIS_PROMPT += SYNTHESIS_PROMPT_EXAMPLE

PROMPT_FINAL_ANSWER_GENERAL = """
# Role
You are a professional biomedical research assistant with deep domain expertise.

# Task
Based on the question and expert discussion, organize the final answer to the original question, and output in markdown format.
Note: Keep the reference marker at the citation points, such as `[Pa1a]`.
"""

PROMPT_FINAL_ANSWER_MCQ = """# Role
You are a professional biomedical research assistant with deep domain expertise.

# Task
Based on the question and expert discussion, organize the final answer to the original question following the given format.

# Answer Format
Answer: Options (Letters right next to each other, e.g., AC)
Reason: Explanations

## Example
Answer: AC
Reason: 
1. A is correct because... 
2. B is wrong because...
...
"""

PROMPT_FINAL_ANSWER_QA = """# Role
You are a professional biomedical research assistant with deep domain expertise.

# Task
Based on the question and expert discussion, organize the final answer to the original question following the given format.

# Answer Format
List every distinct point as a numbered bullet (1., 2., 3., ...).
Separate numbered bullet points with `\n`.
Each bullet is a single, concise sentence that directly answers the question and is unique among the list.
Limit your answer to no more than 5 bullet points.
Do not include any extraneous text, headers, or commentary outside this structure.
"""

PROMPT_FINAL_ANSWER_H = """# Role
You are a professional biomedical research assistant with deep domain expertise.

# Task
Based on the question and expert discussion, organize the final answer to the original question following the given format.
IMPORTANT: The answer to the question DOES NOT exist in the existing data (literature, databases, etc.), you need to conduct logical analysis based on existing knowledge, and infer the answer to the question.
You need to deeply reason about the possible influencing mechanisms rather than generalize with existing knowledge.

# Answer Format
List every distinct point as a numbered bullet (1., 2., 3., ...).
Separate numbered bullet points with `\n`.
Each bullet is a single, concise sentence that directly answers the question and is unique among the list.
Limit your answer to no more than 5 bullet points.
Do not include any extraneous text, headers, or commentary outside this structure.
"""

PROMPT_FINAL_ANSWER_SCQ = """# Role
You are a professional biomedical research assistant with deep domain expertise.

# Task
Based on the question and expert discussion, organize the final answer to the original question following the given format.

# Answer Format
Answer: [Option]
Reason: [Explanations]

## Example
Answer: A
Reason: 
1. A is correct because... 
2. B is wrong because...
...
"""

PROMPT_FINAL_ANSWER_L = """# Role
You are a professional biomedical research assistant with deep domain expertise.

# Task
Based on the question and expert discussion, organize the final answer to the original question following the given format.
IMPORTANT: The answer to the question may NOT exist in the existing data (literature, databases, etc.), you need to conduct logical analysis based on existing knowledge, and infer the answer to the question.
You need to deeply reason about the possible influencing mechanisms rather than generalize with existing knowledge.

# Answer Format
Likelihood: [0-100 scale, where 0 means very unlikely and 100 means very likely]
Reason: [Explanations in numbered bullet points]

## Example
Likelihood: 65
Reason:
1. Point one...
2. Point two...
...
"""


CRITIQUE_PROMPT = """# Task
Evaluate whether the answer sufficiently and effectively addresses the given question.

# Evaluation Criteria
1. **Completeness**: Does the answer address all aspects of the question?
2. **Accuracy**: Is the information scientifically accurate and properly supported?
3. **Relevance**: Does the answer stay focused on the question?
4. **Depth**: Is the level of detail appropriate for the question?

# Question
{query}

# Answer
{answer}
"""


CRITIQUE_PROMPT_EXAMPLE = """
# Output JSON Format
{{
    "is_sufficient": true/false,
    "reasoning": "Detailed reasoning for the assessment",
    "missing_aspects": "Missing aspects or gaps in the answer (None if is_sufficient is true)",
    "new_sub_questions": "New sub-questions to address the gaps (None if is_sufficient is true)"
}}
"""
CRITIQUE_PROMPT += CRITIQUE_PROMPT_EXAMPLE
