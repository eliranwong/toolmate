from freegenius import config
from guidance import models, select

# test guidance streaming feature
# https://guidance.readthedocs.io/en/latest/example_notebooks/tutorials/intro_to_guidance.html#Streaming

tool = False

user_input = "What time is it now?"

lm = models.LlamaCpp(config.llamacppMainModel_model_path, echo = False)

lm += f"""Analyze the following input and decide if a tool a tool is necessary for resolution:
<input>Me: {user_input}</input>

Analysis: First, determine whether the given input contains a question or not.
You: The input does {select(["contain", "not contain"], name="question")} a question.
"""

if "?" in user_input or lm.get("question") == "contain":
    lm += f"""Analysis: Next, determine whether you have adequate or inadequate knowledge to answer the question without an additional tool.
You: I have {select(["adequate", "inadequate"], name="knowledge")} knowledge to answer the question.
"""
    if lm.get("knowledge") == "inadequate":
        tool = True
    else:
        lm += f"""Analysis: Next, determine whether real-time information is necessary or optional for you to accurately answer the question.
You: Real-time information is {select(["necessary", "optional"], name="realtime")}.
"""
        if lm.get("realtime") == "necessary":
            tool = True
        else:
            lm += f"""Analysis: Next, determine whether you need access to my device to retrieve information for answering the question.
You: I do {select(["need", "not need"], name="access")} access to your device.
"""
            if lm.get("access") == "need":
                tool = True
else:
    print("The input does not contain a question")
    ...

lm += f"""Decision: Tool may {"" if tool else "not "}be required."""

print(str(lm))


