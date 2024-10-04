"""
ToolMate AI Plugin - modify images

modify the given images according to changes specified by users

[TOOL_CALL]
"""


if not config.isTermux:

    from toolmate import config, is_valid_image_file, is_valid_image_url, print1, print3, startLlamacppVisionServer, stopLlamacppVisionServer, print2, encode_image, getCliOutput, getCpuThreads, runToolMateCommand, getLlamacppServerClient, downloadStableDiffusionFiles
    import os
    from openai import OpenAI
    from toolmate.utils.call_chatgpt import check_openai_errors
    from toolmate.utils.terminal_mode_dialogs import TerminalModeDialogs
    from base64 import b64decode
    from urllib.parse import quote
    from stable_diffusion_cpp import StableDiffusion
    from PIL import Image
    from toolmate.utils.single_prompt import SinglePrompt
    from prompt_toolkit.styles import Style
    from toolmate.utils.promptValidator import NumberValidator


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
            print3(f"Saved image: {imageFile}")
            if config.terminalEnableTermuxAPI:
                getCliOutput(f"termux-share {imageFile}")
            else:
                cli = f"{config.open} {imageFile}"
                #os.system(cli)
                subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            message = f"Saved image: {imageFile}"
            config.toolTextOutput = message
            print3(message)

        llmInterface = "chatgpt"

        if llmInterface in ("llamacpp", "llamacppserver", "ollama", "gemini", "groq"):
            config.stopSpinning()
            promptStyle = Style.from_dict({
                # User input (default text).
                "": config.terminalCommandEntryColor2,
                # Prompt.
                "indicator": config.terminalPromptIndicatorColor2,
            })
            runToolMateCommand("customvisionserver") if llmInterface=="llamacppserver" else startLlamacppVisionServer()
            client = getLlamacppServerClient("vision") if llmInterface=="llamacppserver" else OpenAI(base_url=f"http://localhost:{config.llamacppVisionModel_server_port}/v1", api_key="toolmate")
            downloadStableDiffusionFiles()
            stable_diffusion = StableDiffusion(
                model_path=config.stableDiffusion_model_path,
                lora_model_dir=os.path.join(config.localStorage, "LLMs", "stable_diffusion", "lora"),
                wtype="default", # Weight type (options: default, f32, f16, q4_0, q4_1, q5_0, q5_1, q8_0)
                # seed=1337, # Uncomment to set a specific seed
                verbose=config.stableDiffusion_verbose,
                n_threads=getCpuThreads(),
            )
            for imageFile in files:
                width, height = Image.open(imageFile).size
                print2("Specify the width:")
                new_width = SinglePrompt.run(style=promptStyle, default=str(width), validator=NumberValidator())
                if new_width and not new_width.strip().lower() == config.exit_entry and int(new_width) > 0:
                    width = int(new_width)
                print2("Specify the height:")
                new_height = SinglePrompt.run(style=promptStyle, default=str(height), validator=NumberValidator())
                if new_height and not new_height.strip().lower() == config.exit_entry and int(new_height) > 0:
                    height = int(new_height)
                image_description = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe image in detail",},
                            {"type": "image_url", "image_url": {"url": encode_image(imageFile)},}
                        ],
                        }
                    ],
                    max_tokens=4096,
                ).choices[0].message.content
                imageFile_modified = f"{os.path.splitext(imageFile)[0]}_modified.png"
                output = stable_diffusion.img_to_img(
                    image=imageFile,
                    prompt=f"""Description of the original image:
{image_description}

Make the following changes in your output:
{changes}""",
                    width=width,
                    height=height,
                )
                #print(output)
                output[0].save(imageFile_modified)
                openImageFile(imageFile_modified)
            stopLlamacppVisionServer()
            return ""

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
        else:
            os.system(f"{config.open} {imageFile}")

        config.stopSpinning()
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

    config.addFunctionCall(signature=functionSignature, method=modify_images)