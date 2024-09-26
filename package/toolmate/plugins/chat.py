"""
ToolMate AI Plugin - edit text

edit text files

[TOOL_CALL]
"""

from toolmate import config

def chat(_):
    # a dummy plugin to avoid using tool
    return "[INVALID]"

functionSignature = {
    "examples": [
        "Hi",
        "How are you?",
        "In python, how"
    ],
    "name": "chat",
    "description": f'''Provide information or answer a question''',
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "My message",
            },
        },
        "required": ["message"],
    },
}

config.addFunctionCall(signature=functionSignature, method=chat)