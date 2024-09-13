"""
ToolMate AI Plugin - ask groq

Ask Groq Model for conversation only; no function calling

[FUNCTION_CALL]
"""


from toolmate import config
from toolmate.groqchat import GroqChatbot

def ask_groq(function_args):
    config.stopSpinning()
    query = function_args.get("query") # required
    config.currentMessages = config.currentMessages[:-1]
    GroqChatbot().run(query, once=True)
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