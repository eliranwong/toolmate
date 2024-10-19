"""
ToolMate AI Plugin - create images

generate images with model "dall-e-3"

[TOOL_CALL]
"""


from toolmate import config, print2, print3, getCurrentDateTime, getCliOutput, getCpuThreads
import os, shutil
from base64 import b64decode
from toolmate.utils.call_chatgpt import check_openai_errors
from toolmate.utils.terminal_mode_dialogs import TerminalModeDialogs
from openai import OpenAI
from pathlib import Path


@check_openai_errors
def create_image_dalle3(function_args):
    def openImageFile(imageFile):
        if config.terminalEnableTermuxAPI:
            getCliOutput(f"termux-share {imageFile}")
        elif shutil.which(config.open):
            cli = f"{config.open} {imageFile}"
            #os.system(cli)
            subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        message = f"Image saved: {imageFile}"
        config.toolTextOutput = message
        print3(message)

    prompt = function_args.get("prompt") # required

    # image file path
    folder = os.path.join(config.localStorage, "images")
    Path(folder).mkdir(parents=True, exist_ok=True)
    imageFile = os.path.join(folder, f"{getCurrentDateTime()}.png")

    config.stopSpinning()
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
    #jsonFile = os.path.join(config.toolMateAIFolder, "temp", "openai_image.json")
    #with open(jsonFile, mode="w", encoding="utf-8") as fileObj:
    #    json.dump(response.data[0].b64_json, fileObj)
    image_data = b64decode(response.data[0].b64_json)
    with open(imageFile, mode="wb") as pngObj:
        pngObj.write(image_data)
    openImageFile(imageFile)
    return ""

functionSignature = {
    "examples": [
        "generate image",
        "create image",
    ],
    "name": "create_image_dalle3",
    "description": "Create an image with DALLE-3",
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

config.addFunctionCall(signature=functionSignature, method=create_image_dalle3)