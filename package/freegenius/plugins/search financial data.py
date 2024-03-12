"""
LetMeDoIt AI Plugin - search financial data

search financial data with yfinance

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.utils.shared_utils import SharedUtil
import json

def search_finance(function_args):
    code = function_args.get("code") # required
    information = SharedUtil.showAndExecutePythonCode(code)
    if information:
        info = {
            "information": information,
        }
        return json.dumps(info)
    return ""

functionSignature = {
    "intent": [
        "access to internet real-time information",
    ],
    "examples": [
        "Check stock price",
    ],
    "name": "search_finance",
    "description": f'''Search or analyze financial data. Use this function ONLY WHEN package yfinance is useful to resolve my request''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code that integrates package yfinance to resolve my request. Integrate package matplotlib to visualize data, if applicable.",
            },
        },
        "required": ["code"],
    },
}

config.addFunctionCall(signature=functionSignature, method=search_finance)