"""
LetMeDoIt AI Plugin - dates and times

Retrieve information about dates and times

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.utils.shared_utils import SharedUtil

def datetimes(function_args):
    code = function_args.get("code") # required
    information = SharedUtil.showAndExecutePythonCode(code)
    return information

functionSignature = {
    "intent": [
        "access to internet real-time information",
    ],
    "examples": [
        "What time is it now?",
        "What is the current time",
    ],
    "name": "datetimes",
    "description": f'''Get information about dates and times''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Generate python code that integrates package pendulum to resolve my input. Please pay attention to any specific locations or dates.",
            },
        },
        "required": ["code"],
    },
}

config.addFunctionCall(signature=functionSignature, method=datetimes)