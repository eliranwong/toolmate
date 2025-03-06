"""
ToolMate AI Plugin - search weather info

search for weather information

[TOOL_CALL]
"""

from toolmate import config

if config.online:

    if not config.openweathermapApi or config.openweathermapApi == "toolmate":
        config.changeOpenweathermapApi()

    if config.openweathermapApi:
        from toolmate import print1, print3, getOpenweathermapApi_key
        from toolmate.utils.python_utils import PythonUtil
        import json

        def search_weather(function_args):
            code = function_args.get("code") # required
            information = PythonUtil.showAndExecutePythonCode(code)
            if information == "[INVALID]":
                return "[INVALID]"
            elif information.startswith("```executed\n"):
                config.toolTextOutput = information
            elif information:
                return json.loads(information)["information"]
            return ""

        functionSignature = {
            "examples": [
                "current weather",
                "search weather",
            ],
            "name": "search_weather",
            "description": f'''Answer a query about weather''',
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": f"""Generate python code that use my OpenWeatherMap API key '{getOpenweathermapApi_key()}' to resolve my request. Use Celsius as the unit for temperature.""",
                    },
                },
                "required": ["code"],
            },
        }

        config.addToolCall(signature=functionSignature, method=search_weather)
    else:
        print1("To use plugin 'search weather info', you need to set up an OpenWeatherMap API key first.")
        print3("Read: https://github.com/eliranwong/letmedoit/wiki/OpenWeatherMap-API-Setup")