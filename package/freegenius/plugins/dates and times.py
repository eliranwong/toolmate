"""
FreeGenius AI Plugin - dates and times

Retrieve information about dates and times

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.utils.python_utils import PythonUtil
import pprint, json

def datetimes(function_args):
    code = function_args.get("code") # required
    #information = PythonUtil.showAndExecutePythonCode(code)
    #return information
    config.tempContent = PythonUtil.showAndExecutePythonCode(code)
    try:
        pprint.pprint(json.loads(config.tempContent))
    except:
        print(config.tempContent)
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