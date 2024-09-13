"""
ToolMate AI Plugin - ask gemini pro

Ask Google Gemini Pro for information

[FUNCTION_CALL]
"""


from toolmate import config
from toolmate.geminipro import GeminiPro

def ask_gemini(function_args):
    config.stopSpinning()
    query = function_args.get("query") # required
    GeminiPro(temperature=config.llmTemperature).run(query, once=True)
    return ""

functionSignature = {
    "examples": [
        "Ask Gemini",
    ],
    "name": "ask_gemini",
    "description": "Ask Gemini to chat or provide information",
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

config.addFunctionCall(signature=functionSignature, method=ask_gemini)
config.inputSuggestions.append("Ask Gemini: ")