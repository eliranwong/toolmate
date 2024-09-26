"""
ToolMate AI Plugin - send tweet

send a tweet to twitter

[TOOL_CALL]
"""

from toolmate import config, openURL
import urllib.parse

def send_tweet(function_args):
    message = function_args.get("message") # required
    config.stopSpinning()
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
        "properties": {
            "message": {
                "type": "string",
                "description": "The message that is to be sent to twitter",
            },
        },
        "required": ["message"],
    },
}

config.addFunctionCall(signature=functionSignature, method=send_tweet)