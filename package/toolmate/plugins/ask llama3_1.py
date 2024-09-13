"""
ToolMate AI Plugin - ask Llama2

Ask Llama2 for information

[FUNCTION_CALL]
"""


from toolmate import config
from toolmate.ollamachat import OllamaChat

def ask_llama3_1(function_args):
    query = function_args.get("query") # required
    config.stopSpinning()
    OllamaChat().run(query, model="llama3.1", once=True)
    return ""

functionSignature = {
    "examples": [
        "Ask Llama3.1",
    ],
    "name": "ask_llama3_1",
    "description": "Ask Llama3.1 to chat or provide information",
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

config.addFunctionCall(signature=functionSignature, method=ask_llama3_1)
config.inputSuggestions.append("Ask Llama3.1: ")