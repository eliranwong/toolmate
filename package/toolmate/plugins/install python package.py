"""
ToolMate AI Plugin - install python package

install python package into the environment that runs LetMeDoIt AI

[TOOL_CALL]
"""

from toolmate import config
from toolmate import installPipPackage

# Function method
def install_package(function_args):
    package = function_args.get("package") # required
    if package:
        config.stopSpinning()
        install = installPipPackage(f"--upgrade {package}")
        return "Installed!" if install else f"Failed to install '{package}'!"
    return ""

# Function Signature
functionSignature = {
    "examples": [
        "install python package",
    ],
    "name": "install_package",
    "description": f'''Install a python package''',
    "parameters": {
        "type": "object",
        "properties": {
            "package": {
                "type": "string",
                "description": "Package name",
            },
        },
        "required": ["package"],
    },
}

# Integrate the signature and method into LetMeDoIt AI
config.addFunctionCall(signature=functionSignature, method=install_package)