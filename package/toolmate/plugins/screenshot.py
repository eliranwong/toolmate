"""
ToolMate AI Plugin - search google

Search internet for keywords when LLM lacks information or when user ask about news or latest updates

[TOOL_CALL]
"""

from toolmate import config
from PIL import ImageGrab
import os

# pip3 install googlesearch-python
# Use google https://pypi.org/project/googlesearch-python/ to search internet for information, about which ChatGPT doesn't know.

def screenshot(function_args):
    config.stopSpinning()
    if function_args:
        filepath = function_args.get("filepath")
        #config.currentMessages[-1] = {"role": "user", "content": keywords}
    else:
        filepath = config.currentMessages[-1]["content"]

    # Capture the entire screen
    screenshot = ImageGrab.grab()
    # Save the screenshot
    screenshot.save(filepath)

    

    return ""

functionSignature = {
    "examples": [],
    "name": "screenshot",
    "description": "Take a screenshot",
    "parameters": {
        "type": "object",
        "properties": {} if not config.tool_selection_agent else {
            "filepath": {
                "type": "string",
                "description": '''File path for saving the screenshot; return "screenshot.png" if it is not given.''',
            },
        },
        "required": [] if not config.tool_selection_agent else ["filepath"],
    },
}

config.addToolCall(signature=functionSignature, method=screenshot)