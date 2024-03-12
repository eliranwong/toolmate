"""
LetMeDoIt AI Plugin - dates and times

Retrieve information about dates and times

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.utils.shared_utils import SharedUtil
import os, re

def create_statistical_graphics(function_args):
    config.stopSpinning()

    code = function_args.get("code") # required
    information = SharedUtil.showAndExecutePythonCode(code)

    pngPattern = """\.savefig\(["']([^\(\)]+\.png)["']\)"""
    match = re.search(pngPattern, code)
    if match:
        pngFile = match.group(1)
        os.system(f"{config.open} {pngFile}")
        return f"Saved as '{pngFile}'"
    elif information:
        return information
    return ""

functionSignature = {
    "intent": [
        "create content",
    ],
    "examples": [
        "Create a plot / graph / chart",
        "Visualize data",
    ],
    "name": "create_statistical_graphics",
    "description": f'''Create statistical plots, such as pie charts or bar charts, to visualize statistical data''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code that integrates package seaborn to resolve my request. Use TkAgg as backend. Created plots are saved in png format",
            },
        },
        "required": ["code"],
    },
}

config.addFunctionCall(signature=functionSignature, method=create_statistical_graphics)