"""
LetMeDoIt AI Plugin - create images

generate images with model "dall-e-3"

[FUNCTION_CALL]
"""

from freegenius import config
import openai, os
from base64 import b64decode
from letmedoit.utils.shared_utils import SharedUtil
from letmedoit.utils.terminal_mode_dialogs import TerminalModeDialogs
from openai import OpenAI
from pathlib import Path

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
    try:
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

    except openai.APIError as e:
        config.print("Error: Issue on OpenAI side.")
        config.print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
    #except openai.Timeout as e:
    #    config.print("Error: Request timed out.")
    #    config.print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
    except openai.RateLimitError as e:
        config.print("Error: You have hit your assigned rate limit.")
        config.print("Solution: Pace your requests. Read more in OpenAI [Rate limit guide](https://platform.openai.com/docs/guides/rate-limits).")
    except openai.APIConnectionError as e:
        config.print("Error: Issue connecting to our services.")
        config.print("Solution: Check your network settings, proxy configuration, SSL certificates, or firewall rules.")
    #except openai.InvalidRequestError as e:
    #    config.print("Error: Your request was malformed or missing some required parameters, such as a token or an input.")
    #    config.print("Solution: The error message should advise you on the specific error made. Check the [documentation](https://platform.openai.com/docs/api-reference/) for the specific API method you are calling and make sure you are sending valid and complete parameters. You may also need to check the encoding, format, or size of your request data.")
    except openai.AuthenticationError as e:
        config.print("Error: Your API key or token was invalid, expired, or revoked.")
        config.print("Solution: Check your API key or token and make sure it is correct and active. You may need to generate a new one from your account dashboard.")
    #except openai.ServiceUnavailableError as e:
    #    config.print("Error: Issue on OpenAI servers. ")
    #    config.print("Solution: Retry your request after a brief wait and contact us if the issue persists. Check the [status page](https://status.openai.com).")
    except:
        SharedUtil.showErrors()
    config.stopSpinning()
    return ""


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