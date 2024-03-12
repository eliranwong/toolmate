"""
LetMeDoIt AI Plugin - create images

generate images with model "dall-e-3"

[FUNCTION_CALL]
"""

from freegenius import config
import os
from base64 import b64decode
from freegenius.utils.shared_utils import SharedUtil, check_openai_errors
from freegenius.utils.terminal_mode_dialogs import TerminalModeDialogs
from openai import OpenAI
from pathlib import Path

@check_openai_errors
def create_image(function_args):
    prompt = function_args.get("prompt") # required
    dialogs = TerminalModeDialogs(None)
    # size selection
    options = ("1024x1024", "1024x1792", "1792x1024")
    size = dialogs.getValidOptions(
        options=options,
        title="Generating an image ...",
        default="1024x1024",
        text="Select size below:"
    )
    if not size:
        config.stopSpinning()
        return "[INVALID]"
    # quality selection
    options = ("standard", "hd")
    quality = dialogs.getValidOptions(
        options=options,
        title="Generating an image ...",
        default="hd",
        text="Select quality below:"
    )
    if not quality:
        config.stopSpinning()
        return "[INVALID]"

    # get responses
    #https://platform.openai.com/docs/guides/images/introduction
    response = OpenAI().images.generate(
        model="dall-e-3",
        prompt=f"I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:\n{prompt}",
        size=size,
        quality=quality, # "hd" or "standard"
        response_format="b64_json",
        n=1,
    )
    # open image
    #imageUrl = response.data[0].url
    #jsonFile = os.path.join(config.letMeDoItAIFolder, "temp", "openai_image.json")
    #with open(jsonFile, mode="w", encoding="utf-8") as fileObj:
    #    json.dump(response.data[0].b64_json, fileObj)
    folder = config.getLocalStorage()
    folder = os.path.join(folder, "images")
    Path(folder).mkdir(parents=True, exist_ok=True)
    imageFile = os.path.join(folder, f"{SharedUtil.getCurrentDateTime()}.png")
    image_data = b64decode(response.data[0].b64_json)
    with open(imageFile, mode="wb") as pngObj:
        pngObj.write(image_data)
    config.stopSpinning()
    if config.terminalEnableTermuxAPI:
        SharedUtil.getCliOutput(f"termux-share {imageFile}")
    else:
        os.system(f"{config.open} {imageFile}")
    return f"Saved as '{imageFile}'"

functionSignature = {
    "intent": [
        "create content",
    ],
    "examples": [
        "Create image",
    ],
    "name": "create_image",
    "description": "create an image",
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Description of the image in as much detail as possible",
            },
        },
        "required": ["prompt"],
    },
}

config.addFunctionCall(signature=functionSignature, method=create_image)