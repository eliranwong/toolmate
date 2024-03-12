"""
LetMeDoIt AI Plugin - open web browser

open a url with default web browser

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.utils.shared_utils import SharedUtil

# Function method
def open_browser(function_args):
    url = function_args.get("url") # required
    if url:
        SharedUtil.openURL(url)
    return ""

# Function Signature
functionSignature = {
    "intent": [
        "access to internet real-time information",
    ],
    "examples": [
        "Open web browser",
        "Open website",
        "Open https://letmedoit.ai",
    ],
    "name": "open_browser",
    "description": f'''Open an url with default web browser''',
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