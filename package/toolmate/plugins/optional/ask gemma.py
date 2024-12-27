"""
ToolMate AI Plugin - ask Gemma

Ask Google Gemma for information

[TOOL_CALL]
"""


from toolmate import config
from toolmate.ollamachat import OllamaChat

def ask_gemma(function_args):
    query = function_args.get("query") # required
    config.stopSpinning()
    OllamaChat().run(query, model="gemma:7b", once=True)
    return ""

functionSignature = {
    "examples": [
        "Ask Gemma",
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

config.addToolCall(signature=functionSignature, method=ask_gemma)
config.inputSuggestions.append("Ask Gemma: ")