"""
ToolMate AI Plugin - analyze images

analyze images

Platform: llamacpp, ollama
Model: llava <- customizable
To customise:
Change in config.py:
llamacppVisionModel_model_path
llamacppVisionModel_clip_model_path
ollamaVisionModel

Platform: gemini
Model: Gemini Pro Vision

Platform: chaptgpt, letmedoit
Model "gpt-4o"
Reference: https://platform.openai.com/docs/guides/vision

[FUNCTION_CALL]
"""

from toolmate import config, print1, print2, is_valid_image_file, is_valid_image_url, startLlamacppVisionServer, stopLlamacppVisionServer, is_valid_url, encode_image, runToolMateCommand, getLlamacppServerClient
from toolmate.utils.call_chatgpt import check_openai_errors
import os
from openai import OpenAI
from toolmate.geminiprovision import GeminiProVision
from toolmate.utils.call_ollama import CallOllama

@check_openai_errors
def analyze_images_llamacpp(function_args):
    from toolmate import config

    llmInterface = "llamacpp"

    if llmInterface == "gemini":
        answer = GeminiProVision(temperature=config.llmTemperature).analyze_images_llamacpp(function_args)
        if answer:
            config.toolTextOutput = answer
            return ""
        else:
            return "[INVALID]"
    elif llmInterface in ("chatgpt", "letmedoit") and not config.openaiApiKey:
        return "OpenAI API key not found!"

    query = function_args.get("query") # required
    files = function_args.get("image_filepath") # required
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
        if is_valid_url(i) and is_valid_image_url(i):
            content.append({"type": "image_url", "image_url": {"url": i,},})
        elif os.path.isfile(i) and is_valid_image_file(i):
            content.append({"type": "image_url", "image_url": encode_image(i),})
        else:
            files.remove(i)

    if content:
        if llmInterface in ("chatgpt", "letmedoit"):
            client = OpenAI()
        elif llmInterface == "llamacpp":
            # start llama.cpp vision server
            startLlamacppVisionServer()
            client = OpenAI(base_url=f"http://localhost:{config.llamacppVisionModel_server_port}/v1", api_key="toolmate")
        elif llmInterface == "llamacppserver":
            # start llama.cpp vision server
            runToolMateCommand("customvisionserver")
            client = getLlamacppServerClient("vision")
        elif llmInterface in ("ollama", "groq"):
            config.currentMessages[-1] = {'role': 'user', 'content': query, 'images': files}
            answer = CallOllama.getSingleChatResponse("", config.currentMessages, model=config.ollamaVisionModel)
            config.toolTextOutput = answer
            print2("```assistant")
            print1(answer)
            print2("```")
            return ""

        content.insert(0, {"type": "text", "text": query,})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                "role": "user",
                "content": content,
                }
            ],
            max_tokens=4096,
        )
        answer = response.choices[0].message.content
        config.toolTextOutput = answer

        # display answer
        print2("```assistant")
        print1(answer)
        print2("```")

        # stop llama.cpp vision server
        if llmInterface == "llamacpp":
            stopLlamacppVisionServer()

        return ""
    return "[INVALID]"

functionSignature = {
    "examples": [
        "describe image",
        "compare images",
        "analyze image",
    ],
    "name": "analyze_images_llamacpp",
    "description": "Describe or compare images with Llama.cpp",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Questions or requests that users ask about the given images",
            },
            "image_filepath": {
                "type": "string",
                "description": """Return a list of image paths or urls, e.g. '["image1.png", "/tmp/image2.png", "https://letmedoit.ai/image.png"]'. Return '[]' if image path is not provided.""",
            },
        },
        "required": ["query", "image_filepath"],
    },
}

config.addFunctionCall(signature=functionSignature, method=analyze_images_llamacpp)
config.inputSuggestions.append("Describe this image in detail: ")
config.inputSuggestions.append("Extract text from this image: ")