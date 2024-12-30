"""
ToolMate AI Plugin - convert audio into video

* download Youtube audio and convert it into mp3

* installation of 'ffmpeg' is required

[TOOL_CALL]
"""

import shutil

if shutil.which("ffmpeg"):
    from toolmate import config, packageFolder
    import re, os

    def convert_audio_into_video(function_args):
        config.stopSpinning()
        image_file_path = function_args.get("image_file_path", "")
        if not image_file_path:
            image_file_path = os.path.join(packageFolder, "icons", "ToolMate.png")
        audio_file_path = function_args.get("audio_file_path")
        video_file_path = re.sub(r"\.[^.]+?$", "", audio_file_path) + ".mp4"
        # ffmpeg -loop 1 -i 'image.png' -i 'audio.mp3' -c:v libx264 -tune stillimage -c:a aac -b:a 192k -shortest video.mp4
        cli = f'''ffmpeg -loop 1 -i "{image_file_path}" -i "{audio_file_path}" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -shortest {video_file_path}'''
        os.system(cli)
        config.toolTextOutput = f"Video saved: {video_file_path}"
        return ""

    functionSignature = {
        "examples": [
            "convert audio into video",
        ],
        "name": "convert_audio_into_video",
        "description": "Convert audio into video; requires an audio path; optionally provides an image path for the image to be displayed in the video",
        "parameters": {
            "type": "object",
            "properties": {
                "image_file_path": {
                    "type": "string",
                    "description": "The image file path of the image displayed in the video; return an empty string '' if it is not given",
                },
                "audio_file_path": {
                    "type": "string",
                    "description": "The audio file path to be converted",
                },
            },
            "required": ["audio_file_path"],
        },
    }

    config.addToolCall(signature=functionSignature, method=convert_audio_into_video)