"""
ToolMate AI Plugin - ask azure

Ask Azure for conversation only; no function calling

[TOOL_CALL]
"""


from toolmate import config

if config.online:

    from toolmate.utils.call_openai_azure import CallOpenAIAzure

    try:
        CallOpenAIAzure.checkCompletion()

        def azure(function_args):
            config.stopSpinning()
            if function_args:
                query = function_args.get("query") # required
                config.currentMessages[-1] = {"role": "user", "content": query}
            else:
                query = config.currentMessages[-1]["content"]
            completion = CallOpenAIAzure.regularCall(config.currentMessages)
            config.toolmate.streamCompletion(completion, openai=True)
            return ""

        functionSignature = {
            "examples": [
                "Ask ChatGPT",
            ],
            "name": "azure",
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

        config.addToolCall(signature=functionSignature, method=azure)
        config.inputSuggestions.append("Ask ChatGPT: ")

    except:
        print("Plugin `ask azure` not enabled! Check if your API key is valid!")