"""
LetMeDoIt AI Plugin - modify images

modify the given images according to changes specified by users

[FUNCTION_CALL]
"""

from freegenius import config
import openai, os
from openai import OpenAI
from letmedoit.utils.shared_utils import SharedUtil
from letmedoit.utils.terminal_mode_dialogs import TerminalModeDialogs
from pathlib import Path
from base64 import b64decode
from urllib.parse import quote

def modify_images(function_args):
    changes = function_args.get("changes") # required
    files = function_args.get("files") # required
    #print(files)
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

    for i in files:
        description, filename = get_description(i)
        if description:
            if changes:
                description = f"""Description of the original image:
{description}

Make the following changes:
{changes}"""
            else:
                description = f"Image description:\n{description}"
            if config.developer:
                config.print(description)
            response = create_image(description, filename)
            if response == "[INVALID]" and len(files) == 1:
                return response
    return ""

def get_description(filename):
    content = []
    # validate image path
    if SharedUtil.is_valid_image_url(filename):
        content.append({"type": "image_url", "image_url": {"url": filename,},})
        filename = quote(filename, safe="")
    elif SharedUtil.is_valid_image_file(filename):
        content.append({"type": "image_url", "image_url": SharedUtil.encode_image(filename),})

    if content:
        content.insert(0, {"type": "text", "text": "Describe this image in as much detail as possible, including color patterns, positions and orientations of all objects and backgrounds in the image",})
        #print(content)
        try:
            response = OpenAI().chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                    "role": "user",
                    "content": content,
                    }
                ],
                max_tokens=4096,
            )
            answer = response.choices[0].message.content
            #print(answer)
            return (answer, filename)

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

    return ("", "")

def create_image(description, original_filename):
    basename = os.path.basename(original_filename)
    title = f"Modifying '{basename}' ..."
    dialogs = TerminalModeDialogs(None)
    # size selection
    options = ("1024x1024", "1024x1792", "1792x1024")
    size = dialogs.getValidOptions(
        options=options,
        title=title,
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
        title=title,
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
            prompt=f"I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:\n{description}",
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
        image_data = b64decode(response.data[0].b64_json)
        imageFile = f"{original_filename}_modified.png"
        with open(imageFile, mode="wb") as pngObj:
            pngObj.write(image_data)
        config.stopSpinning()
        if config.terminalEnableTermuxAPI:
            SharedUtil.getCliOutput(f"termux-share {imageFile}")
        else:
            os.system(f"{config.open} {imageFile}")

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
        "change files",
    ],
    "examples": [
        "Modify image",
    ],
    "name": "modify_images",
    "description": "modify the images that I provide",
    "parameters": {
        "type": "object",
        "properties": {
            "changes": {
                "type": "string",
                "description": "The requested changes in as much detail as possible. Return an empty string '' if changes are not specified.",
            },
            "files": {
                "type": "string",
                "description": """Return a list of image paths, e.g. '["image1.png", "/tmp/image2.png"]'. Return '[]' if image path is not provided.""",
            },
        },
        "required": ["changes", "files"],
    },
}

config.addFunctionCall(signature=functionSignature, method=modify_images)