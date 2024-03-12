"""
LetMeDoIt AI Plugin - ask Codey

Ask Google Codey for information about coding

[FUNCTION_CALL]
"""


from freegenius import config
from freegenius.codey import Codey

def ask_codey(function_args):
    query = function_args.get("query") # required
    config.stopSpinning()
    Codey().run(query, temperature=config.llmTemperature)
    return ""

functionSignature = {
    "intent": [
        "ask a chatbot",
    ],
    "examples": [
        "Ask Codey about",
    ],
    "name": "ask_codey",
    "description": "Ask Codey for information about coding",
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

config.addFunctionCall(signature=functionSignature, method=ask_codey)
config.inputSuggestions.append("Ask Codey: ")