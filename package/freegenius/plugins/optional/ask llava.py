"""
FreeGenius AI Plugin - ask LLava

Ask LLava for information

[FUNCTION_CALL]
"""


from freegenius import config
from freegenius.ollamachat import OllamaChat

def ask_llava(function_args):
    query = function_args.get("query") # required
    config.stopSpinning()
    OllamaChat().run(query, model="llava", once=True)
    return ""

functionSignature = {
    "examples": [
        "Ask Llava",
    ],
    "name": "ask_llava",
    "description": "Ask LLava to chat or provide information",
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

config.addFunctionCall(signature=functionSignature, method=ask_llava)
config.inputSuggestions.append("Ask LLava: ")