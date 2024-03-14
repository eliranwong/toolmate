"""
LetMeDoIt AI Plugin - create maps

Create maps

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.utils.shared_utils import SharedUtil
import re, os

def create_map(function_args):
    code = function_args.get("code") # required
    information = SharedUtil.showAndExecutePythonCode(code)
    htmlPattern = """\.save\(["']([^\(\)]+\.html)["']\)"""
    match = re.search(htmlPattern, code)
    if match:
        htmlFile = match.group(1)
        os.system(f"{config.open} {htmlFile}")
        return f"Saved as '{htmlFile}'"
    elif information:
        return information
    return ""

functionSignature = {
    "intent": [
        "create content",
    ],
    "examples": [
        "Create a map",
    ],
    "name": "create_map",
    "description": f'''Create maps''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Generate python code that integrates package folium to resolve my request. Created maps are saved in *.html file. Tell me the file path at the end.",
            },
        },
        "required": ["code"],
    },
}

config.addFunctionCall(signature=functionSignature, method=create_map)