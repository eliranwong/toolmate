"""
LetMeDoIt AI Plugin - analyze images

analyze images with model "gpt-4-vision-preview"

reference: https://platform.openai.com/docs/guides/vision

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.utils.shared_utils import SharedUtil, check_openai_errors
import openai, os
from openai import OpenAI

@check_openai_errors
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