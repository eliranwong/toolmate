"""
ToolMate AI Plugin - ask Llama2

Ask Llama2 for information

[FUNCTION_CALL]
"""


from toolmate import config
from toolmate.ollamachat import OllamaChat

def ask_llama2(function_args):
    query = function_args.get("query") # required
    config.stopSpinning()
    OllamaChat().run(query, model="llama2", once=True)
    return ""

functionSignature = {
    "examples": [
        "Ask Llama2",
    ],
    "name": "ask_llama2",
    "description": "Ask Llama2 to chat or provide information",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The request in detail, including any supplementary information",
            },
        },
        "required": ["query"],
    },
}

config.addFunctionCall(signature=functionSignature, method=ask_llama2)
config.inputSuggestions.append("Ask Llama2: ")