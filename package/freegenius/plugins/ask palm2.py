"""
LetMeDoIt AI Plugin - ask PaLM 2

Ask Google PaLM 2 for information

[FUNCTION_CALL]
"""


from freegenius import config
from freegenius.palm2 import Palm2

def ask_palm2(function_args):
    query = function_args.get("query") # required
    config.stopSpinning()
    Palm2().run(query, temperature=config.llmTemperature)
    return ""

functionSignature = {
    "intent": [
        "ask a chatbot",
    ],
    "examples": [
        "Ask PaLM about",
    ],
    "name": "ask_palm2",
    "description": "Ask PaLM 2 to chat or provide information",
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

config.addFunctionCall(signature=functionSignature, method=ask_palm2)
config.inputSuggestions.append("Ask PaLM 2: ")