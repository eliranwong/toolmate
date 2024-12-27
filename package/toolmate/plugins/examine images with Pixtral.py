"""
ToolMate AI Plugin - analyze images with Mistral

analyze images with Mistral

Reference: https://console.mistral.com/docs/vision

[TOOL_CALL]
"""


from toolmate import config

if config.online:

    from toolmate import print1, print2, is_valid_image_file, is_valid_image_url, getMistralClient, is_valid_url, encode_image
    import os

    def examine_images_pixtral(function_args):
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
            if getFileSizeInMB(i) > 10:
                print1(f"File `{i}` exceeds 10MB!")
                continue
            elif is_valid_url(i) and is_valid_image_url(i):
                content.append({"type": "image_url", "image_url": {"url": i,},})
            elif os.path.isfile(i) and is_valid_image_file(i):
                content.append({"type": "image_url", "image_url": {"url": encode_image(i)},})
            else:
                files.remove(i)

        if content:
            content.insert(0, {"type": "text", "text": query,})

            completion = getMistralClient().chat.complete(
                model="pixtral-12b-2409",
                messages=[
                    {
                    "role": "user",
                    "content": content,
                    }
                ],
            )
            answer = completion.choices[0].message.content
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
        "name": "examine_images_pixtral",
        "description": "Describe or compare images with Pixtral",
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

    config.addToolCall(signature=functionSignature, method=examine_images_pixtral)
