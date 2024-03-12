"""
LetMeDoIt AI Plugin - install python package

install python package into the environment that runs LetMeDoIt AI

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.utils.install import installmodule

# Function method
def install_package(function_args):
    package = function_args.get("package") # required
    if package:
        config.stopSpinning()
        install = installmodule(f"--upgrade {package}")
        return "Installed!" if install else f"Failed to install '{package}'!"
    return ""

# Function Signature
functionSignature = {
    "intent": [
        "installation",
    ],
    "examples": [
        "Install package",
    ],
    "name": "install_package",
    "description": f'''Install python package''',
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