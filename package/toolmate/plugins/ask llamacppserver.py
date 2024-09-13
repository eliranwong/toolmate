"""
ToolMate AI Plugin - ask llama.cpp server

Ask llama.cpp server Model for conversation only; no function calling

[FUNCTION_CALL]
"""


from toolmate import config
from toolmate.llamacppserver import LlamacppServerChat

def ask_llamacppserver(function_args):
    config.stopSpinning()
    query = function_args.get("query") # required
    config.currentMessages = config.currentMessages[:-1]
    LlamacppServerChat().run(query, once=True)
    return ""

functionSignature = {
    "examples": [
        "Ask Llama.cpp Server",
    ],
    "name": "ask_llamacppserver",
    "description": "Ask Llama.cpp Server to chat or provide information",
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

config.addFunctionCall(signature=functionSignature, method=ask_llamacppserver)
config.inputSuggestions.append("Ask Llama.cpp Server: ")