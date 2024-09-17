"""
ToolMate AI Plugin - search weather info

search for weather information

[FUNCTION_CALL]
"""

if not config.openweathermapApi:
    config.changeOpenweathermapApi()

if config.openweathermapApi:
    from toolmate import config
    from toolmate import print1, print3
    from toolmate.utils.python_utils import PythonUtil
    import json

    def search_weather_info(function_args):
        code = function_args.get("code") # required
        information = PythonUtil.showAndExecutePythonCode(code)
        if information:
            return json.loads(information)["information"]
        return "Not found!"

    functionSignature = {
        "examples": [
            "current weather",
            "search weather",
        ],
        "name": "search_weather_info",
        "description": f'''Answer a query about weather''',
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": f"""Generate python code that use my OpenWeatherMap API key '{config.openweathermapApi}' to resolve my request. Use Celsius as the unit for temperature.""",
                },
            },
            "required": ["code"],
        },
    }

    config.addFunctionCall(signature=functionSignature, method=search_weather_info)
else:
    print1("To use plugin 'search weather info', you need to set up an OpenWeatherMap API key first.")
    print3("Read: https://github.com/eliranwong/letmedoit/wiki/OpenWeatherMap-API-Setup")