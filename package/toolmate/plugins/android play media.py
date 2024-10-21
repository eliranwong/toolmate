"""
ToolMate AI Plugin - play media

play media on Android

[TOOL_CALL]
"""

if config.isTermux:

    from toolmate import config
    import subprocess

    def play_media(function_args):
        media_file_path = function_args.get("media_file_path").replace('"', '\\"') # required
        config.stopSpinning()
        cli = f'''termux-media-player play "{media_file_path}"'''
        subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return ""

    functionSignature = {
        "examples": [],
        "name": "play_media",
        "description": f'''Play a media file''',
        "parameters": {
            "type": "object",
            "properties": {
                "media_file_path": {
                    "type": "string",
                    "description": "The file path of the media file",
                },
            },
            "required": ["media_file_path"],
        },
    }

    config.addFunctionCall(signature=functionSignature, method=play_media)