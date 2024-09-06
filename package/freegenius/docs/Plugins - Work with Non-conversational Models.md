# Plugins - Work with Non-conversational Model

LetMeDoIt AI main UI is based on conversational models, e.g. gpt-3, gpt-4.

Developers can utilise [function calls in plugins](https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Function-Calling) to work with non-conversational models.

# For example - Generate Image with DALL-E-3

In our plugin "[create images](https://github.com/eliranwong/letmedoit/blob/main/package/letmedoit/plugins/create%20images.py)", we utilise a function call to pass the prompt to work with DALL-E-3 for image generation.

```
from letmedoit import config
import json, openai, os
from base64 import b64decode
from letmedoit.utils.shared_utils import SharedUtil
from openai import OpenAI

def generate_image(function_args):
    prompt = function_args.get("prompt") # required
    try:
        # get responses
        #https://platform.openai.com/docs/guides/images/introduction
        response = OpenAI().images.generate(
            model="dall-e-3",
            prompt=f"I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:\n{prompt}",
            size="1024x1024",
            quality="hd", # "hd" or "standard"
            response_format="b64_json",
            n=1,
        )
        # open image
        #imageUrl = response.data[0].url
        #jsonFile = os.path.join(config.taskWizAIFolder, "temp", "openai_image.json")
        #with open(jsonFile, mode="w", encoding="utf-8") as fileObj:
        #    json.dump(response.data[0].b64_json, fileObj)
        imageFile = os.path.join(config.taskWizAIFolder, "temp", f"{SharedUtil.getCurrentDateTime()}.png")
        image_data = b64decode(response.data[0].b64_json)
        with open(imageFile, mode="wb") as pngObj:
            pngObj.write(image_data)
        if config.terminalEnableTermuxAPI:
            config.mainWindow.getCliOutput(f"termux-share {imageFile}")
        else:
            os.system(f"{config.open} {imageFile}")

    except openai.APIError as e:
        config.print("Error: Issue on OpenAI side.")
        config.print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
    except openai.RateLimitError as e:
        config.print("Error: You have hit your assigned rate limit.")
        config.print("Solution: Pace your requests. Read more in OpenAI [Rate limit guide](https://platform.openai.com/docs/guides/rate-limits).")
    except openai.APIConnectionError as e:
        config.print("Error: Issue connecting to our services.")
        config.print("Solution: Check your network settings, proxy configuration, SSL certificates, or firewall rules.")
    except openai.AuthenticationError as e:
        config.print("Error: Your API key or token was invalid, expired, or revoked.")
        config.print("Solution: Check your API key or token and make sure it is correct and active. You may need to generate a new one from your account dashboard.")
    except:
        SharedUtil.showErrors()

functionSignature = {
    "name": "generate_image",
    "description": "create an image",
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "description about the image",
            },
        },
        "required": ["prompt"],
    },
}

config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["generate_image"] = generate_image
```

# Related Post

[Plugin - anaylze image](https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Analyze-Images)

# More about taskWiz AI Plugins

https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Overview