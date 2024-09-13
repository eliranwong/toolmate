"""
ToolMate AI Plugin - ask chatgpt

Ask ChatGPT for conversation only; no function calling

[FUNCTION_CALL]
"""


from toolmate import config
from toolmate.llamacpp import LlamacppChat

def ask_llamacpp(function_args):
    config.stopSpinning()
    query = function_args.get("query") # required
    config.currentMessages = config.currentMessages[:-1]
    LlamacppChat().run(query, once=True)
    return ""

functionSignature = {
    "examples": [
        "Ask Llama.cpp",
    ],
    "name": "ask_llamacpp",
    "description": "Ask Llama.cpp to chat or provide information",
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

config.addFunctionCall(signature=functionSignature, method=ask_llamacpp)
config.inputSuggestions.append("Ask ChatGPT: ")