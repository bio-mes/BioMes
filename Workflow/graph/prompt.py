BIOMEDICAL_RESEARCH_SYSTEM_PROMPT = """# Role
You are a professional biomedical research assistant with deep domain expertise."""

TRANSLATION_PROMPT = """
Please translate the given text to target language. 

# Requirements:
1. Maintain accuracy of biomedical terminology
2. Return directly if original text is already in target language
3. Preserve original format and structure
4. Use standard translations for technical terms

# Target language:
{target_language}

# Given text:
{text}
"""


QUERY_ANALYSIS_PROMPT = """
# Role
You are a professional biomedical research assistant with deep domain expertise.

# Task
Analyze the user's question systematically and return a JSON object that precisely captures its intent and content.

# Output JSON Schema
{
    "query_type": "one query type, e.g., knowledge retrieval, mechanistic investigation, comparative analysis, etc",
    "main_concepts": ["list of key biological concepts, e.g., specific proteins, diseases, pathways"],
    "sub_questions": ["List of non-overlapping, concrete sub-questions decomposed from input question. Maximum 5 sub-questions."]
}

IMPORTANT: Return ONLY a valid JSON object, WITHOUT markdown code blocks or backticks.
"""


TOOL_USAGE_PROMPT = """
Based on the following question, please use appropriate tools to collect relevant information:

# Question
{query}

# Tools
You have access to the following tools:
{tool_descriptions}
Note: You may call multiple tools and call one tool multiple times in a turn.

Start collecting information:
"""

KNOWLEDGE_SYNTHESIS_PROMPT = """
Based on the following question and tool results, please integrate useful information to answer the question:

# Question
{query}

# Tool Results
{tool_results}

# Requirements
1. Analyze the relevance and reliability of information
2. Integrate information from different sources
3. Identify connections and contradictions between information
4. Provide evidence-based comprehensive answers
5. Mark the index of the references at the citation points, such as `[Aa1]`. If there are multiple citations, use multiple `[id]`, such as `[Aa1][Ab3]`.`. There is no need to list the references at the end of the answer.
"""


CRITIQUE_PROMPT = """
# Task
Evaluate whether the answer sufficiently and effectively addresses the given question.

# Question
{query}

# Answer
{answer}

# Evaluation Criteria
1. **Completeness**: Does the answer address all aspects of the question?
2. **Accuracy**: Is the information scientifically accurate and properly supported?
3. **Relevance**: Does the answer stay focused on the question?
4. **Depth**: Is the level of detail appropriate for the question?

# Output Requirements
Return a JSON object with the following structure:
{{
    "is_sufficient": true/false,
    "reasoning": "Detailed explanation of why the answer is or isn't sufficient",
    "missing_aspects": ["list of missing information or gaps"],
    "new_sub_questions": ["specific questions to address the gaps (only if is_sufficient is False)"]
}}

If the answer is insufficient, generate 1-3 specific sub-questions that would help fill the gaps.

IMPORTANT: Return ONLY a valid JSON object, WITHOUT markdown code blocks or backticks.
"""


FINAL_ANSWER_PROMPT_GENERAL = """Please answer the question based on the sub-questions and answers:

# Question: 
{query}

# Sub-questions and Answers:
{sub_qas}

# Note:
Mark the index of the references at the citation points, such as `[Aa1]`. If there are multiple citations, use multiple `[id]`, such as `[Aa1][Ab3]`.`. There is no need to list the references at the end of the answer.
"""

PROMPT_FINAL_ANSWER_MCQ = """Based on the sub-questions and answers, organize the final answer to the original question following the given format.

# Question: 
{query}

# Sub-questions and Answers:
{sub_qas}

# Output Format
Answer: [Options]
Reason: [Explanations]

## Example
Answer: AC
Reason: 
1. A is correct because... 
2. B is wrong because...
"""

PROMPT_FINAL_ANSWER_QA = """Based on the sub-questions and answers, answer the original question concisely yet comprehensively.

# Original Question: 
{query}

# Sub-questions and Answers:
{sub_qas}

# Output Format
List every distinct point as a numbered bullet (1., 2., 3., …).
Separate numbered bullet points with `\n`.
Each bullet is a single, concise sentence that directly answers the question and is unique among the list.
Limit your answer to no more than 5 bullet points.
Do not include any extraneous text, headers, or commentary outside this structure.
"""

PROMPT_FINAL_ANSWER_H = """# Role
You are a professional biomedical research assistant with deep domain expertise.

# Task
Based on the sub-questions and answers, answer the original question concisely yet comprehensively.
IMPORTANT: The answer to the question DOES NOT exist in the existing data (literature, databases, etc.), you need to conduct logical analysis based on existing knowledge, and infer the answer to the question.
You need to deeply reason about the possible influencing mechanisms rather than generalize with existing knowledge.

# Original Question: 
{query}

# Sub-questions and Answers:
{sub_qas}

# Output Format
List every distinct point as a numbered bullet (1., 2., 3., …).
Separate numbered bullet points with `\n`.
Each bullet is a single, concise sentence that directly answers the question and is unique among the list.
Limit your answer to no more than 5 bullet points.
Do not include any extraneous text, headers, or commentary outside this structure.
"""


