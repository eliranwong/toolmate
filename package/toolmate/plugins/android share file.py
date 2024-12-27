"""
ToolMate AI Plugin - share file

share file on Android

[TOOL_CALL]
"""

from toolmate import config

if config.isTermux:

    import subprocess

    def share_file(function_args):
        file_path = function_args.get("file_path").replace('"', '\\"') # required
        config.stopSpinning()
        cli = f'''termux-share -a send "{file_path}"'''
        subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return ""

    functionSignature = {
        "examples": [
            "share file",
        ],
        "name": "share_file",
        "description": f'''Share a file''',
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The file path of the shared file",
                },
            },
            "required": ["file_path"],
        },
    }

    config.addToolCall(signature=functionSignature, method=share_file)