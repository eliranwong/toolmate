"""
ToolMate AI Plugin - search financial data

search financial data with yfinance

[TOOL_CALL]
"""

from toolmate import config

if not config.isLite and config.online:

    from toolmate.utils.python_utils import PythonUtil
    import json

    def search_finance(function_args):
        code = function_args.get("code") # required
        information = PythonUtil.showAndExecutePythonCode(code)
        if information == "[INVALID]":
            return "[INVALID]"
        elif information.startswith("```executed\n"):
            config.toolTextOutput = information
        elif information:
            return information
        return ""

    functionSignature = {
        "examples": [
            "check stock price",
        ],
        "name": "search_finance",
        "description": f'''Search or analyze financial data. Use this function ONLY WHEN package yfinance is useful to resolve my request''',
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Generate python code that integrates package yfinance to resolve my request. Integrate package matplotlib to visualize data, if applicable.",
                },
            },
            "required": ["code"],
        },
    }

    config.addFunctionCall(signature=functionSignature, method=search_finance)