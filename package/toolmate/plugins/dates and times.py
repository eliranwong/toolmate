"""
ToolMate AI Plugin - dates and times

Retrieve information about dates and times

[FUNCTION_CALL]
"""

from toolmate import config
from toolmate.utils.python_utils import PythonUtil
import pprint, json

def datetimes(function_args):
    code = function_args.get("code") # required
    #information = PythonUtil.showAndExecutePythonCode(code)
    #return information
    config.toolTextOutput = PythonUtil.showAndExecutePythonCode(code)
    try:
        pprint.pprint(json.loads(config.toolTextOutput))
    except:
        print(config.toolTextOutput)
    return ""

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
                "description": f"Generate python code that uses package 'pytz' to resolve my request. Please pay attention to any specific locations or dates.",
            },
        },
        "required": ["code"],
    },
}

config.addFunctionCall(signature=functionSignature, method=datetimes, deviceInfo=True)