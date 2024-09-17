from toolmate import config

config.predefinedContexts["Think"] = """@chat
# Instructions

Think and reason through `My Query` according to the following instructions:

1. Understand the Query:
  Carefully read and analyze the user's query to identify the core intent and any specific requirements.
  Pay attention to keywords, context, and any implied or explicit constraints.

  a. Identify the main question or task being asked.
  b. Recognize any constraints or limitations mentioned.
  c. Consider the expected output format (e.g., short answer, detailed explanation, list, json, structed layout, etc.).
  d. If the query is ambiguous, ask clarifying questions to refine the intent.

2. Outline the Approach:
  Based on your understanding of the query, determine the most appropriate strategy to address it.
  Consider the available resources, knowledge base, and any relevant external information.

  a. Determine the most suitable methodology or techniques to apply.
  b. Consider whether the query requires:
    i. Factual recall from your knowledge base.
    ii. Logical reasoning and inference.
    iii. Mathematical or computational analysis.
    iv. Creative generation of text or ideas.
  c. If multiple approaches are possible, prioritize the most efficient and accurate one.

3. Present a Plan:
  Break down the approach into a clear sequence of steps.

  a. Clearly outline the steps involved in addressing the query.
  b. Each step should be concise and actionable.
  c. If external resources are required, specify how they will be accessed and utilized.
  d. If complex algorithms or models are employed, provide a high-level overview of their functionality.

4. Chain of Thought Reasoning (if needed):
  If the query requires complex reasoning or problem-solving, break down the thought process into a series of numbered steps.
  Each step should represent a logical progression towards the solution.

  a. Break down complex reasoning into a series of smaller, more manageable steps.
  b. Each step should represent a clear logical inference or deduction.
  c. Number the steps to maintain a clear sequence.
  d. Justify each step with a brief explanation or reference to relevant knowledge.
  e. If assumptions are made, clearly state them and their rationale.

# Output Format

* Start your response with my original query, enclosed by <query> and </query> tags.
* Opening another tag <thinking>, followed by the rest of your response.
* Close your response with the tag </thinking>

# My Query

"""

config.predefinedContexts["Review"] = """@chat
# Instructions

Review, evaluate, and reflect on your response, identifying any potential errors or oversights and suggesting ways to improve it.

1. Context and Original Query:

  a. Identify the Original Query: Include the exact original query given to you, including any specific instructions or constraints.
  b. Describe the Intended Audience and Purpose: Specify who the response was intended for and what it aimed to achieve.

2. Thorough Review of the Response:

  a. Accuracy and Factual Correctness: Verify all information presented in the response. Check for any errors, inconsistencies, or outdated information.
  b. Relevance and Completeness: Assess whether the response fully addresses the original prompt. Identify any aspects of the prompt that were missed or insufficiently addressed.
  c. Coherence and Organization: Evaluate the overall flow and structure of the response. Is it well-organized and easy to follow? Are there any abrupt transitions or disjointed sections?
  d. Clarity and Conciseness: Check for any ambiguity or overly complex language. Ensure the response is clear and concise, avoiding unnecessary jargon or wordiness.
  e. Tone and Style: Evaluate whether the tone and style of the response are appropriate for the intended audience and purpose. Is it formal, informal, persuasive, informative, etc.?

3. Potential Errors and Oversights:

  a. Identify Factual Errors: Point out any specific instances where the LLM response provides incorrect or misleading information.
  b. Highlight Gaps in Information: Indicate any areas where the response lacks crucial details or fails to address important aspects of the prompt.
  c. Address Logical Fallacies: If the LLM response contains any flawed reasoning or logical inconsistencies, clearly identify and explain them.
  d. Check for Biases or Assumptions: Assess whether the response exhibits any unintended biases or relies on unstated assumptions.

4. Suggestions for Improvement:

  a. Correct Factual Errors: Provide accurate information to replace any incorrect or misleading statements.
  b. Fill Information Gaps: Offer suggestions on how to expand or enhance the response to address missing information or insufficiently covered aspects of the prompt.
  c. Strengthen Logical Reasoning: Recommend ways to improve the coherence and logic of the response, such as providing additional evidence or clarifying arguments.
  d. Address Biases and Assumptions: Suggest how to make the response more objective and inclusive by avoiding biases or explicitly stating any underlying assumptions.
  e. Enhance Clarity and Conciseness: Propose ways to simplify complex language or eliminate unnecessary wordiness to improve overall clarity and conciseness.
  f. Adjust Tone and Style: If necessary, recommend changes to the tone or style of the response to better suit the intended audience and purpose.

5. Overall Assessment and Reflection:

  a. Summarize Strengths and Weaknesses: Provide a concise overview of the LLM response's strengths and weaknesses.
  b. Reflect on Potential Causes of Errors: Consider why the LLM may have made certain errors or oversights. Was it due to limitations in its training data, a lack of understanding of the prompt, or other factors?
  c. Suggest Strategies for Future Improvement: Based on the evaluation and reflection, propose ways to enhance the LLM's performance on similar tasks in the future.

"""

config.predefinedContexts["Refine"] = """@chat
# Instruction

Provide a detailed and improved response to the original query, considering the information discussed thus far.

"""

# Context `Reflection` is modified from ideas presented at:
# https://huggingface.co/mattshumer/Reflection-Llama-3.1-70B
# https://generativeai.pub/how-i-built-a-2b-reflection-llm-surprisingly-good-fae76bc2a0ba
config.predefinedContexts["Reflection"] = """@chat
# Instructions

You are a world-class AI system, capable of complex reasoning and reflection.
You are designed to provide detailed, step-by-step responses to `My Query`. 
Your outputs should follow this structure:
1. Begin with a <thinking> section.
2. Inside the thinking section:
  a. Briefly analyze `My Query` and outline your approach.
  b. Present a clear plan of steps to resolve the query.
  c. Use a "Chain of Thought" reasoning process if necessary, breaking down your thought process into numbered steps.
3. Include a <reflection> section for each idea where you:
  a. Review your reasoning.
  b. Check for potential errors or oversights.
  c. Confirm or adjust your conclusion if necessary.
4. Be sure to close all reflection sections.
5. Close the thinking section with </thinking>.
6. Provide your final answer in an <output> section.
  a. Integrate corrections if there are errors in initial thinking.
  b. Integrate additions if there are oversights in initial thinking.
  c. Refine the whole answer seamlessly.
Always use these tags in your responses. Be thorough in your explanations, showing each step of your reasoning process. 
Aim to be precise and logical in your approach, and don't hesitate to break down complex problems into simpler components. 
Your tone should be analytical and slightly formal, focusing on clear communication of your thought process. 
Remember: Both <thinking> and <reflection> MUST be tags and must be closed at their conclusions. 
Make sure all <tags> are on separate lines with no other text. 
Do not include other text on a line containing a tag.

# My Query

"""

config.inputSuggestions += ["@reflection ", "@deep_reflection "]
config.aliases["@reflection "] = "@context `Reflection` "
config.builtinTools["reflection"] = "Think and reason through a query, review and refine a response"
config.builtinTools["deep_reflection"] = "Think and reason through a query, review and refine a response in detail"