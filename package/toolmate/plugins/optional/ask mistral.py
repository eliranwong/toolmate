"""
ToolMate AI Plugin - ask Mistral

Ask Mistral for information

[FUNCTION_CALL]
"""


from toolmate import config
from toolmate.ollamachat import OllamaChat

def ask_mistral(function_args):
    query = function_args.get("query") # required
    config.stopSpinning()
    OllamaChat().run(query, model="mistral", once=True)
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
                "description": "The request in detail, including any supplementary information",
            },
        },
        "required": ["query"],
    },
}

config.addFunctionCall(signature=functionSignature, method=ask_mistral)
config.inputSuggestions.append("Ask Mistral: ")