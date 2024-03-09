"""
LetMeDoIt AI Plugin - analyze images

analyze images with model "gpt-4-vision-preview"

reference: https://platform.openai.com/docs/guides/vision

[FUNCTION_CALL]
"""

from freegenius import config
from letmedoit.utils.shared_utils import SharedUtil
import openai, os
from openai import OpenAI

def analyze_images(function_args):
    query = function_args.get("query") # required
    files = function_args.get("files") # required
    #print(files)
    if isinstance(files, str):
        if not files.startswith("["):
            files = f'["{files}"]'
        files = eval(files)

    filesCopy = files[:]
    for item in filesCopy:
        if os.path.isdir(item):
            for root, _, allfiles in os.walk(item):
                for file in allfiles:
                    file_path = os.path.join(root, file)
                    files.append(file_path)
            files.remove(item)

    content = []
    # valid image paths
    for i in files:
        if SharedUtil.is_valid_url(i) and SharedUtil.is_valid_image_url(i):
            content.append({"type": "image_url", "image_url": {"url": i,},})
        elif os.path.isfile(i) and SharedUtil.is_valid_image_file(i):
            content.append({"type": "image_url", "image_url": SharedUtil.encode_image(i),})

    if content:
        content.insert(0, {"type": "text", "text": query,})
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
            config.print(answer)
            config.tempContent = answer
            return ""

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

    return "[INVALID]"

functionSignature = {
    "intent": [
        "analyze files",
    ],
    "examples": [
        "analyze image",
    ],
    "name": "analyze_images",
    "description": "describe or analyze images",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Questions or requests that users ask about the given images",
            },
            "files": {
                "type": "string",
                "description": """Return a list of image paths or urls, e.g. '["image1.png", "/tmp/image2.png", "https://letmedoit.ai/image.png"]'. Return '[]' if image path is not provided.""",
            },
        },
        "required": ["query", "files"],
    },
}

config.addFunctionCall(signature=functionSignature, method=analyze_images)
config.inputSuggestions.append("Describe this image in detail: ")
config.inputSuggestions.append("Extract text from this image: ")