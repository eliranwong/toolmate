"""
ToolMate AI Plugin - ask googleai

Ask ChatGPT for conversation only; no function calling

[TOOL_CALL]
"""


from toolmate import config
from toolmate.utils.call_googleai import CallGoogleAI

if config.googleaiApi_key:

    try:
        CallGoogleAI.checkCompletion()

        def ask_googleai(function_args):
            config.stopSpinning()
            if function_args:
                query = function_args.get("query") # required
                config.currentMessages[-1] = {"role": "user", "content": query}
            else:
                query = config.currentMessages[-1]["content"]
            completion = CallGoogleAI.regularCall(config.currentMessages)
            config.toolmate.streamCompletion(completion, openai=True)
            return ""

        functionSignature = {
            "examples": [],
            "name": "ask_googleai",
            "description": "Ask GoogleAI Model to chat or provide information",
            "parameters": {
                "type": "object",
                "properties": {} if not config.tool_selection_agent else {
                    "query": {
                        "type": "string",
                        "description": "The original request in detail, including any supplementary information",
                    },
                },
                "required": [] if not config.tool_selection_agent else ["query"],
            },
        }

        config.addFunctionCall(signature=functionSignature, method=ask_googleai)
        config.inputSuggestions.append("Ask GoogleAI: ")

    except:
        print("Plugin `ask googleai` not enabled! Check if your Google AI API key is valid!")