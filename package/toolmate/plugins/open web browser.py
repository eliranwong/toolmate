"""
ToolMate AI Plugin - open web browser

open a url with default web browser

[TOOL_CALL]
"""

from toolmate import config, openURL

# Function method
def open_browser(function_args):
    url = function_args.get("url") # required
    if url:
        openURL(url)
    return ""

# Function Signature
functionSignature = {
    "examples": [
        "open web browser",
        "browse website",
        "https://",
        "open url",
    ],
    "name": "open_browser",
    "description": f'''Open https:// url with web browser''',
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The url",
            },
        },
        "required": ["url"],
    },
}

# Integrate the signature and method into LetMeDoIt AI
config.addFunctionCall(signature=functionSignature, method=open_browser)
config.inputSuggestions.append("Open url: ")