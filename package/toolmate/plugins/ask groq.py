"""
ToolMate AI Plugin - ask groq

Ask Groq Model for conversation only; no function calling

[TOOL_CALL]
"""


from toolmate import config

if config.online:

    from toolmate.utils.call_groq import CallGroq

    def groq(function_args):
        config.stopSpinning()
        if function_args:
            query = function_args.get("query") # required
            config.currentMessages[-1] = {"role": "user", "content": query}
        else:
            query = config.currentMessages[-1]["content"]
        completion = CallGroq.regularCall(config.currentMessages, chat_model=config.groqApi_chat_model if config.useAdditionalChatModel else None, max_tokens=config.groqApi_chat_model_max_tokens if config.useAdditionalChatModel else None)
        config.toolmate.streamCompletion(completion, openai=True)
        return ""

    functionSignature = {
        "examples": [
            "Ask Groq",
        ],
        "name": "groq",
        "description": "Ask Groq to chat or provide information",
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

    config.addToolCall(signature=functionSignature, method=groq)
    config.inputSuggestions.append("Ask Groq: ")