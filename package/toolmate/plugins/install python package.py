"""
ToolMate AI Plugin - install python package

install python package into the environment that runs LetMeDoIt AI

[TOOL_CALL]
"""

from toolmate import config

if config.online:

    from toolmate import installPipPackage

    # Function method
    def install_python_package(function_args):
        config.stopSpinning()
        if function_args:
            package = function_args.get("package") # required
            #config.currentMessages[-1] = {"role": "user", "content": package}
        else:
            package = config.currentMessages[-1]["content"]
        if package:
            install = installPipPackage(f"--upgrade {package}")
            return "Installed!" if install else f"Failed to install '{package}'!"
        return ""

    # Function Signature
    functionSignature = {
        "examples": [
            "install python package",
        ],
        "name": "install_python_package",
        "description": f'''Install a python package''',
        "parameters": {
            "type": "object",
            "properties": {} if not config.tool_selection_agent else {
                "package": {
                    "type": "string",
                    "description": "Package name",
                },
            },
            "required": [] if not config.tool_selection_agent else ["package"],
        },
    }

    # Integrate the signature and method into LetMeDoIt AI
    config.addToolCall(signature=functionSignature, method=install_python_package)