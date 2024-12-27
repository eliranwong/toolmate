"""
ToolMate AI Plugin - selfie

take a selfie on Android

[TOOL_CALL]
"""

from toolmate import config

if config.isTermux:

    from toolmate import print3
    import subprocess

    def selfie(function_args):
        jpeg_file_path = function_args.get("jpeg_file_path", "") # required
        if not jpeg_file_path:
            jpeg_file_path = "selfie.jpg"
        cli = f'''termux-camera-photo -c 1 "{jpeg_file_path}"'''
        subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print3(f"Saved :{jpeg_file_path}")
        return ""

    functionSignature = {
        "examples": [],
        "name": "selfie",
        "description": f'''Take a selfie with the main camera''',
        "parameters": {
            "type": "object",
            "properties": {
                "jpeg_file_path": {
                    "type": "string",
                    "description": "The file path at which the image is saved",
                },
            },
            "required": ["jpeg_file_path"],
        },
    }

    config.addToolCall(signature=functionSignature, method=selfie)