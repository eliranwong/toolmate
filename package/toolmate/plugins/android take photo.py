"""
ToolMate AI Plugin - take a photo

take a photo on Android

[TOOL_CALL]
"""

if config.isTermux:

    from toolmate import config, print3
    import subprocess

    def take_photo(function_args):
        jpeg_file_path = function_args.get("jpeg_file_path", "") # required
        if not jpeg_file_path:
            jpeg_file_path = "photo.jpg"
        cli = f'''termux-camera-photo "{jpeg_file_path}"'''
        subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print3(f"Saved :{jpeg_file_path}")
        return ""

    functionSignature = {
        "examples": [],
        "name": "take_photo",
        "description": f'''Take a photo with the main camera''',
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

    config.addFunctionCall(signature=functionSignature, method=take_photo)