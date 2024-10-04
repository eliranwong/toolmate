"""
ToolMate AI Plugin - ask chatgpt

Ask ChatGPT for conversation only; no function calling

[TOOL_CALL]
"""


if not config.isTermux:

    from toolmate import config
    from toolmate.utils.call_chatgpt import CallChatGPT

    try:
        CallChatGPT.checkCompletion()

        def ask_chatgpt(function_args):
            config.stopSpinning()
            query = function_args.get("query") # required
            config.currentMessages[-1] = {"role": "user", "content": query}
            completion = CallChatGPT.regularCall(config.currentMessages)
            config.toolmate.streamCompletion(completion, openai=True)
            return ""

        functionSignature = {
            "examples": [
                "Ask ChatGPT",
            ],
            "name": "ask_chatgpt",
            "description": "Ask ChatGPT to chat or provide information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The original request in detail, including any supplementary information",
                    },
                },
                "required": ["query"],
            },
        }

        config.addFunctionCall(signature=functionSignature, method=ask_chatgpt)
        config.inputSuggestions.append("Ask ChatGPT: ")

    except:
        print("Plugin `ask chatgpt` not enabled! Check if your OpenAI API key is valid!")