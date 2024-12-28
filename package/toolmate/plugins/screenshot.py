"""
ToolMate AI Plugin - screenshot

Take a screenshot

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
    else:
        filepath = config.currentMessages[-1]["content"]
    filepath = filepath.rstrip()
    if not filepath.endswith(".png"):
        filepath += ".png"
    # Capture the entire screen
    screenshot = ImageGrab.grab()
    # Save the screenshot
    screenshot.save(filepath)
    config.currentMessages[-1]["content"] = "Take a screenshot."
    config.toolTextOutput = f"Screenshot saved: {filepath}"
    print(config.toolTextOutput)
    return ""

functionSignature = {
    "examples": [],
    "name": "screenshot",
    "description": "Take a screenshot and save it in a file",
    "parameters": {
        "type": "object",
        "properties": {} if not config.tool_selection_agent else {
            "filepath_or_filename": {
                "type": "string",
                "description": '''The file path or name for saving the screenshot; return "screenshot.png" if it is not given.''',
            },
        },
        "required": [] if not config.tool_selection_agent else ["filepath_or_filename"],
    },
}

config.addToolCall(signature=functionSignature, method=screenshot)