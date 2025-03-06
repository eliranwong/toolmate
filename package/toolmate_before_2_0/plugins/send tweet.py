"""
ToolMate AI Plugin - send tweet

send a tweet to twitter

[TOOL_CALL]
"""

from toolmate import config

if config.online:

    from toolmate import openURL
    import urllib.parse

    def send_tweet(function_args):
        config.stopSpinning()
        if function_args:
            message = function_args.get("message") # required
            #config.currentMessages[-1] = {"role": "user", "content": message}
        else:
            message = config.currentMessages[-1]["content"]
        if message:
            openURL(f"""https://twitter.com/intent/tweet?text={urllib.parse.quote(message)}""")
        return ""

    functionSignature = {
        "examples": [
            "send a tweet",
            "post to twitter",
        ],
        "name": "send_tweet",
        "description": f'''Send a tweet to twitter''',
        "parameters": {
            "type": "object",
            "properties": {} if not config.tool_selection_agent else {
                "message": {
                    "type": "string",
                    "description": "The message that is to be sent to twitter",
                },
            },
            "required": [] if not config.tool_selection_agent else ["message"],
        },
    }

    config.addToolCall(signature=functionSignature, method=send_tweet)