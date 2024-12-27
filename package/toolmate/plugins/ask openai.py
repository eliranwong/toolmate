"""
ToolMate AI Plugin - ask chatgpt

Ask ChatGPT for conversation only; no function calling

[TOOL_CALL]
"""


from toolmate import config

if config.online:

    from toolmate.utils.call_openai import CallOpenAI

    try:
        CallOpenAI.checkCompletion()

        def openai(function_args):
            config.stopSpinning()
            if function_args:
                query = function_args.get("query") # required
                config.currentMessages[-1] = {"role": "user", "content": query}
            else:
                query = config.currentMessages[-1]["content"]
            completion = CallOpenAI.regularCall(config.currentMessages)
            config.toolmate.streamCompletion(completion, openai=True)
            return ""

        functionSignature = {
            "examples": [
                "Ask ChatGPT",
            ],
            "name": "openai",
            "description": "Ask ChatGPT to chat or provide information",
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

        config.addToolCall(signature=functionSignature, method=openai)
        config.inputSuggestions.append("Ask ChatGPT: ")

    except:
        print("Plugin `ask chatgpt` not enabled! Check if your OpenAI API key is valid!")