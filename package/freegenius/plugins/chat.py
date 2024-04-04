"""
FreeGenius AI Plugin - edit text

edit text files

[FUNCTION_CALL]
"""

from freegenius import config

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
    "description": f'''chat''',
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