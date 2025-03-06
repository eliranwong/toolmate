"""
ToolMate AI Plugin - modify images

modify the given images according to changes specified by users

[TOOL_CALL]
"""

from toolmate import config

if config.online:

    from toolmate import is_valid_image_file, is_valid_image_url, print1, print3, print2, encode_image, getCliOutput
    import os, shutil, subprocess
    from openai import OpenAI
    from toolmate.utils.call_openai import check_openai_errors
    from toolmate.utils.terminal_mode_dialogs import TerminalModeDialogs
    from base64 import b64decode
    from urllib.parse import quote


    def modify_images(function_args):
        changes = function_args.get("requested_changes_in_detail") # required
        files = function_args.get("image_fullpath") # required
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
                    print1(description)
                response = create_image(description, filename)
                if response == "[INVALID]" and len(files) == 1:
                    return response
        return ""

    @check_openai_errors
    def get_description(filename):
        content = []
        # validate image path
        if is_valid_image_url(filename):
            content.append({"type": "image_url", "image_url": {"url": filename,},})
            filename = quote(filename, safe="")
        elif is_valid_image_file(filename):
            content.append({"type": "image_url", "image_url": {"url": encode_image(filename)},})

        if content:
            content.insert(0, {"type": "text", "text": "Describe this image in as much detail as possible, including color patterns, positions and orientations of all objects and backgrounds in the image",})

            response = OpenAI().chat.completions.create(
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
            #print(answer)
            return (answer, filename)

        return ("", "")

    @check_openai_errors
    def create_image(description, original_filename):
        basename = os.path.basename(original_filename)
        config.stopSpinning()
        title = f"Modifying '{basename}' ..."
        dialogs = TerminalModeDialogs(None)
        # size selection
        if hasattr(config, "api_server_id"):
            if config.imagewidth and config.imageheight:
                if config.imagewidth == config.imageheight:
                    size = "1024x1024"
                elif config.imagewidth > config.imageheight:
                    size = "1792x1024"
                elif config.imageheight < config.imagewidth:
                    size = "1024x1792"
            else:
                size = "1024x1024"
        else:
            options = ("1024x1024", "1024x1792", "1792x1024")
            size = dialogs.getValidOptions(
                options=options,
                title=title,
                default="1024x1024",
                text="Select size below:"
            )
            if not size:
                return "[INVALID]"
            config.imagewidth = config.imageheight = None
        # quality selection
        if hasattr(config, "api_server_id"):
            quality = "hd" if config.imagehd else "standard"
        else:
            options = ("standard", "hd")
            quality = dialogs.getValidOptions(
                options=options,
                title=title,
                default="hd",
                text="Select quality below:"
            )
            if not quality:
                return "[INVALID]"
            config.imagehd = True if quality == "hd" else False

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
        #jsonFile = os.path.join(config.toolMateAIFolder, "temp", "openai_image.json")
        #with open(jsonFile, mode="w", encoding="utf-8") as fileObj:
        #    json.dump(response.data[0].b64_json, fileObj)
        image_data = b64decode(response.data[0].b64_json)
        imageFile = f"{os.path.splitext(original_filename)[0]}_modified.png"
        with open(imageFile, mode="wb") as pngObj:
            pngObj.write(image_data)
        config.stopSpinning()
        if config.terminalEnableTermuxAPI:
            getCliOutput(f"termux-share {imageFile}")
        elif shutil.which(config.open):
            os.system(f"{config.open} {imageFile}")
        config.stopSpinning()
        config.toolTextOutput = f"Image saved: {imageFile}"
        print3(config.toolTextOutput)
        return ""

    functionSignature = {
        "examples": [
            "change image",
            "modify image",
        ],
        "name": "modify_images",
        "description": "Modify images with ChatGPT and DALLE-3",
        "parameters": {
            "type": "object",
            "properties": {
                "requested_changes_in_detail": {
                    "type": "string",
                    "description": "The requested changes in as much detail as possible. Return an empty string '' if changes are not specified.",
                },
                "image_fullpath": {
                    "type": "string",
                    "description": """Return a list of image paths, e.g. '["image1.png", "/tmp/image2.png"]'. Return '[]' if image path is not provided.""",
                },
            },
            "required": ["image_fullpath", "requested_changes_in_detail"],
        },
    }

    config.addToolCall(signature=functionSignature, method=modify_images)