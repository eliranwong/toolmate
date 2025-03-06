"""
ToolMate AI Plugin - create maps

Create maps

[TOOL_CALL]
"""

from toolmate import config, print3
from toolmate.utils.python_utils import PythonUtil
import re, os, shutil

def create_map(function_args):
    code = function_args.get("code") # required
    information = PythonUtil.showAndExecutePythonCode(code)
    if information == "[INVALID]":
        return "[INVALID]"
    htmlPattern = r"""\.save\(["']([^\(\)]+\.html)["']\)"""
    match = re.search(htmlPattern, code)
    if match:
        htmlFile = match.group(1)
        if shutil.which(config.open):
            os.system(f"{config.open} {htmlFile}")
        config.toolTextOutput = f"Saved: {htmlFile}"
        print3(config.toolTextOutput)
        return ""
    elif information.startswith("```executed\n"):
        config.toolTextOutput = information
    elif information:
        return information
    return ""

functionSignature = {
    "examples": [
        "create map",
        "pin on map",
    ],
    "name": "create_map",
    "description": f'''Create maps''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Generate python code that integrates packages 'folium' and 'geopy', when needed, to resolve my request. Created maps are saved in *.html file. Tell me the file path at the end.",
            },
        },
        "required": ["code"],
    },
}

config.addToolCall(signature=functionSignature, method=create_map)