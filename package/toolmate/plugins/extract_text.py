"""
ToolMate AI Plugin - extract_text

Extract text from a file

[TOOL_CALL]
"""

from toolmate import config, getOpenAIClient
from markitdown import MarkItDown
import os, re

# pip3 install googlesearch-python
# Use google https://pypi.org/project/googlesearch-python/ to search internet for information, about which ChatGPT doesn't know.

def extract_text(function_args):
    config.stopSpinning()
    if function_args:
        filepath = function_args.get("filepath")
    else:
        filepath = config.currentMessages[-1]["content"]
    filepath = filepath.rstrip()
    if os.path.isfile(filepath):
        if re.search("(\.jpg|\.jpeg|\.png)$", filepath.lower()):
            md = MarkItDown(llm_client=getOpenAIClient(), llm_model="gpt-4o")
        else:
            md = MarkItDown()
        result = md.convert(filepath)
        config.currentMessages[-1]["content"] = f"Extract text from this file: {filepath}"
        config.toolTextOutput = result.text_content
        print(config.toolTextOutput)
        return ""
    print("Invalid file path!")
    return "[INVALID]"

functionSignature = {
    "examples": [],
    "name": "extract_text",
    "description": "Extract text from a given file and export it in markdown format",
    "parameters": {
        "type": "object",
        "properties": {} if not config.tool_selection_agent else {
            "filepath_or_filename": {
                "type": "string",
                "description": '''The file path or name of the file to be read.''',
            },
        },
        "required": [] if not config.tool_selection_agent else ["filepath_or_filename"],
    },
}

config.addToolCall(signature=functionSignature, method=extract_text)