"""
ToolMate AI Plugin - ask LLava

Ask LLava for information

[TOOL_CALL]
"""


from toolmate import config
from toolmate.ollamachat import OllamaChat

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

config.addToolCall(signature=functionSignature, method=ask_llava)
config.inputSuggestions.append("Ask LLava: ")