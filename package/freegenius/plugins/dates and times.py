"""
FreeGenius AI Plugin - dates and times

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
    "examples": [
        "what time is it",
        "current time",
        "dates",
    ],
    "name": "datetimes",
    "description": f'''Get information about dates and times''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": f"Generate python code that uses my current date and time in {config.state}, {config.country} with package 'pytz' to resolve my request. Please pay attention to any specific locations or dates.",
            },
        },
        "required": ["code"],
    },
}

config.addFunctionCall(signature=functionSignature, method=datetimes)