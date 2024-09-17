"""
ToolMate AI Plugin - remove image background

Remove image background

[FUNCTION_CALL]
"""

from toolmate import config, is_valid_image_file
from toolmate import print2, print3
from toolmate.utils.python_utils import PythonUtil
import os, json, rembg


def remove_image_background(function_args):
    files = function_args.get("filepath") # required
    if isinstance(files, str):
        if not files.startswith("["):
            files = f'["{files}"]'
        files = eval(files)
    if not files:
        return "[INVALID]"

    filesCopy = files[:]
    for item in filesCopy:
        if os.path.isdir(item):
            for root, _, allfiles in os.walk(item):
                for file in allfiles:
                    file_path = os.path.join(root, file)
                    files.append(file_path)
            files.remove(item)

    for input_path in files:
        if is_valid_image_file(input_path):
            output_path = f"{input_path}_no_bg.png"
            with open(input_path, 'rb') as i:
                with open(output_path, 'wb') as o:
                    print3(f"Reading image file: {input_path}")
                    img = rembg.remove(i.read())
                    o.write(img)
                    print3(f"File saved: {output_path}")
        else:
            print2(f"'{input_path}' is not an image file!")

def remove_image_background2(function_args):
    code = function_args.get("code") # required
    information = PythonUtil.showAndExecutePythonCode(code)
    if information:
        filepath = json.loads(information)["information"]
        if os.path.isfile(filepath):
            print3(f"File saved: {filepath}")
            try:
                os.system(f'''{config.open} "{filepath}"''')
            except:
                pass
    return ""

functionSignature = {
    "examples": [
        "remove image background",
    ],
    "name": "remove_image_background",
    "description": f'''Remove image background''',
    "parameters": {
        "type": "object",
        "properties": {
            "filepath": {
                "type": "string",
                "description": """Return a list of image paths, e.g. '["image1.png", "/tmp/image2.png"]'. Return '[]' if image path is not provided.""",
            },
        },
        "required": ["filepath"],
    },
}

config.addFunctionCall(signature=functionSignature, method=remove_image_background)