"""
LetMeDoIt AI Plugin - ask gemini pro

Ask Google Gemini Pro for information

[FUNCTION_CALL]
"""


from freegenius import config
from freegenius.geminipro import GeminiPro

def ask_gemini_pro(function_args):
    config.stopSpinning()
    query = function_args.get("query") # required
    GeminiPro(temperature=config.llmTemperature).run(query)
    return ""

functionSignature = {
    "intent": [
        "ask a chatbot",
    ],
    "examples": [
        "Ask Gemini about",
    ],
    "name": "ask_gemini_pro",
    "description": "Ask Gemini Pro to chat or provide information",
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

config.addFunctionCall(signature=functionSignature, method=ask_gemini_pro)
config.inputSuggestions.append("Ask Gemini Pro: ")