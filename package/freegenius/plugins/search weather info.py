"""
LetMeDoIt AI Plugin - search weather info

search for weather information

[FUNCTION_CALL]
"""

if not config.openweathermapApi:
    config.changeOpenweathermapApi()

if config.openweathermapApi:
    from freegenius import config
    from freegenius.utils.shared_utils import SharedUtil
    import json

    def search_weather_info(function_args):
        code = function_args.get("code") # required
        information = SharedUtil.showAndExecutePythonCode(code)
        if information:
            return json.loads(information)["information"]
        return "Not found!"

    functionSignature = {
        "intent": [
            "access to internet real-time information",
        ],
        "examples": [
            "What's the current weather",
        ],
        "name": "search_weather_info",
        "description": f'''Answer query about weather''',
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": f"""Python code that use my OpenWeatherMap API key '{config.openweathermapApi}' to resolve my request.
To work with OpenWeatherMap API key, you may integrWhat is the current weather in New York?ate python package geocoder in the code to find the required Latitude and Longitude.
In the last line of your code, use 'print' function to print the requested information, without additional description or comment.""",
                },
            },
            "required": ["code"],
        },
    }

    config.addFunctionCall(signature=functionSignature, method=search_weather_info)
else:
    config.print("To use plugin 'search weather info', you need to set up an OpenWeatherMap API key first.")
    config.print3("Read: https://github.com/eliranwong/letmedoit/wiki/OpenWeatherMap-API-Setup")