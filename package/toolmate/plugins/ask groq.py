"""
ToolMate AI Plugin - ask groq

Ask Groq Model for conversation only; no function calling

[TOOL_CALL]
"""


from toolmate import config
from toolmate.utils.call_groq import CallGroq

def ask_groq(function_args):
    query = function_args.get("query") # required
    config.currentMessages[-1] = {"role": "user", "content": query}
    completion = CallGroq.regularCall(config.currentMessages, chat_model=config.groqApi_chat_model if config.useAdditionalChatModel else None, max_tokens=config.groqApi_chat_model_max_tokens if config.useAdditionalChatModel else None)
    config.stopSpinning()
    config.toolmate.streamCompletion(completion, openai=True)
    return ""

functionSignature = {
    "examples": [
        "Ask Groq",
    ],
    "name": "ask_groq",
    "description": "Ask Groq to chat or provide information",
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

config.addFunctionCall(signature=functionSignature, method=ask_groq)
config.inputSuggestions.append("Ask Groq: ")