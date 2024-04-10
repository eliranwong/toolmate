"""
FreeGenius AI Plugin - create statistical graphics

create statistical graphics to visulize data

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.utils.python_utils import PythonUtil
import os, re

def create_statistical_graphics(function_args):
    config.stopSpinning()

    code = function_args.get("code") # required
    information = PythonUtil.showAndExecutePythonCode(code)

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
    "examples": [
        "plot a graph",
        "create a chart",
        "create a bar chart",
        "create a par chart",
        "visualize data",
        "statistics",
    ],
    "name": "create_statistical_graphics",
    "description": f'''Create statistical plots, such as pie charts or bar charts, to visualize statistical data''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Generate python code that integrates package matplotlib to resolve my input. Save the result in png format. Tell me the image path at the end.",
            },
        },
        "required": ["code"],
    },
}

config.addFunctionCall(signature=functionSignature, method=create_statistical_graphics)