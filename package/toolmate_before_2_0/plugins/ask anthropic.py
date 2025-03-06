"""
ToolMate AI Plugin - ask anthropic

Ask Anthropic Model for conversation only; no function calling

[TOOL_CALL]
"""


from toolmate import config

if config.online:

    from toolmate.utils.call_anthropic import CallAnthropic

    try:

        def anthropic(function_args):
            config.stopSpinning()
            if function_args:
                query = function_args.get("query") # required
                config.currentMessages[-1] = {"role": "user", "content": query}
            #else:
            #    query = config.currentMessages[-1]["content"]
            completion = CallAnthropic.regularCall(config.currentMessages)
            config.toolmate.streamCompletion(completion)
            return ""

        functionSignature = {
            "examples": [
                "Ask Anthropic",
            ],
            "name": "anthropic",
            "description": "Ask Anthropic to chat or provide information",
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

        config.addToolCall(signature=functionSignature, method=anthropic)
        config.inputSuggestions.append("Ask Anthropic: ")

    except:
        print("Plugin `ask anthropic` not enabled! Check if your API key is valid!")