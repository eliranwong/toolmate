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

[TOOL_CALL]
"""


from toolmate import config

if config.online:

    from toolmate import print1, print2, is_valid_image_file, is_valid_image_url, is_valid_url, encode_image, getGoogleGenAIClient
    from toolmate.utils.call_openai import check_openai_errors
    import os

    @check_openai_errors
    def examine_images_googleai(function_args):
        from toolmate import config

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
                content.append({"type": "image_url", "image_url": {"url": encode_image(i)},})
            else:
                files.remove(i)

        if content:
            client = getGoogleGenAIClient()

            content.insert(0, {"type": "text", "text": query,})

            response = client.chat.completions.create(
                model="gemini-1.5-pro",
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

            return ""
        return "[INVALID]"

    functionSignature = {
        "examples": [
            "describe image",
            "compare images",
            "analyze image",
        ],
        "name": "examine_images_googleai",
        "description": "Describe or compare images with ChatGPT",
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

    config.addToolCall(signature=functionSignature, method=examine_images_googleai)
