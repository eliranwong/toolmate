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
        "What is the current time in Hong Kong?",
        "Tell me the date of the upcoming Friday?",
    ],
    "name": "datetimes",
    "description": f'''Get information about dates and times''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code that integrates package pendulum to resolve my query",
            },
        },
        "required": ["code"],
    },
}

config.addFunctionCall(signature=functionSignature, method=datetimes)