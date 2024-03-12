"""
LetMeDoIt AI Plugin - ask Gemma

Ask Google Gemma for information

[FUNCTION_CALL]
"""


from freegenius import config
from freegenius.ollamachat import OllamaChat

def ask_gemma(function_args):
    query = function_args.get("query") # required
    config.stopSpinning()
    OllamaChat().run(query, model="gemma:7b")
    return ""

functionSignature = {
    "intent": [
        "ask a chatbot",
    ],
    "examples": [
        "Ask Gemma about",
    ],
    "name": "ask_gemma",
    "description": "Ask Gemma to chat or provide information",
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

config.addFunctionCall(signature=functionSignature, method=ask_gemma)
config.inputSuggestions.append("Ask Gemma: ")