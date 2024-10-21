"""
ToolMate AI Plugin - add a calendar event

add a calendar event on Android

[TOOL_CALL]
"""

if config.isTermux:

    from toolmate import config, stopSpinning

    def add_calendar_event(function_args):
        title = function_args.get("title") # required
        description = function_args.get("description") # required
        url = function_args.get("url", "") # optional
        start_time = function_args.get("start_time_converted_in_milliseconds", "") # optional
        end_time = function_args.get("end_time_converted_in_milliseconds", "") # optional
        location = function_args.get("location", "") # optional

        insert_url = f"\nURL: {url}\n" if url else ""
        insert_location = f"\nLocation: {location}" if location else ""
        description = f'''{description}{insert_url}{insert_location}'''.replace('"', '\\"')

        stopSpinning()

        cli = f'''am start -a android.intent.action.INSERT -t vnd.android.cursor.item/event -e title "{title}" -e description "{description}" -e beginTime {start_time} -e endTime {end_time} -e location {location}'''
        subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return ""

    functionSignature = {
        "examples": [
            "add a calendar event",
        ],
        "name": "add_calendar_event",
        "description": "Add a calendar event",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title of the event.",
                },
                "description": {
                    "type": "string",
                    "description": "The detailed description of the event, including the people involved and their roles, if any.",
                },
                "url": {
                    "type": "string",
                    "description": "Event url",
                },
                "start_time_converted_in_milliseconds": {
                    "type": "string",
                    "description": "The start date and time converted in milliseconds since epoch",
                },
                "end_time_converted_in_milliseconds": {
                    "type": "string",
                    "description": "The start date and time converted in milliseconds since epoch. If not given, return 1 hour later than the start_time_converted_in_milliseconds",
                },
                "location": {
                    "type": "string",
                    "description": "The location or venue of the event.",
                },
            },
            "required": ["title", "description"],
        },
    }

    config.addFunctionCall(signature=functionSignature, method=add_calendar_event, deviceInfo=True, datetimeSensitive=True)