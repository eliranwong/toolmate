"""
ToolMate AI Plugin - ask mistral

Ask Mistral Model for conversation only; no function calling

[TOOL_CALL]
"""


from toolmate import config
from toolmate.utils.call_mistral import CallMistral

def ask_mistral(function_args):
    query = function_args.get("query") # required
    config.currentMessages[-1] = {"role": "user", "content": query}
    completion = CallMistral.regularCall(config.currentMessages, chat_model=config.mistralApi_chat_model if config.useAdditionalChatModel else None, max_tokens=config.mistralApi_chat_model_max_tokens if config.useAdditionalChatModel else None)
    config.stopSpinning()
    config.toolmate.streamCompletion(completion, openai=True)
    return ""

functionSignature = {
    "examples": [
        "Ask Mistral",
    ],
    "name": "ask_mistral",
    "description": "Ask Mistral to chat or provide information",
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

config.addFunctionCall(signature=functionSignature, method=ask_mistral)
config.inputSuggestions.append("Ask Mistral: ")