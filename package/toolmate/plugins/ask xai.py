"""
ToolMate AI Plugin - ask xai

Ask ChatGPT for conversation only; no function calling

[TOOL_CALL]
"""


from toolmate import config
from toolmate.utils.call_xai import CallXAI

if config.xaiApi_key:

    try:
        CallXAI.checkCompletion()

        def ask_xai(function_args):
            config.stopSpinning()
            if function_args:
                query = function_args.get("query") # required
                config.currentMessages[-1] = {"role": "user", "content": query}
            else:
                query = config.currentMessages[-1]["content"]
            completion = CallXAI.regularCall(config.currentMessages)
            config.toolmate.streamCompletion(completion, openai=True)
            return ""

        functionSignature = {
            "examples": [],
            "name": "ask_xai",
            "description": "Ask X AI Model to chat or provide information",
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

        config.addFunctionCall(signature=functionSignature, method=ask_xai)
        config.inputSuggestions.append("Ask X AI: ")

    except:
        print("Plugin `ask xai` not enabled! Check if your X AI API key is valid!")