"""
ToolMate AI Plugin - create images

generate images with model "dall-e-3"

[TOOL_CALL]
"""


if not config.isTermux:

    from toolmate import config, print2, print3, getCurrentDateTime, getCliOutput, getCpuThreads, downloadStableDiffusionFiles
    import os
    from base64 import b64decode
    from toolmate.utils.call_chatgpt import check_openai_errors
    from toolmate.utils.terminal_mode_dialogs import TerminalModeDialogs
    from openai import OpenAI
    from pathlib import Path
    from stable_diffusion_cpp import StableDiffusion
    from toolmate.utils.single_prompt import SinglePrompt
    from prompt_toolkit.styles import Style
    from toolmate.utils.promptValidator import NumberValidator


    @check_openai_errors
    def create_image_dalle3(function_args):
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

        prompt = function_args.get("prompt") # required

        # image file path
        folder = os.path.join(config.localStorage, "images")
        Path(folder).mkdir(parents=True, exist_ok=True)
        imageFile = os.path.join(folder, f"{getCurrentDateTime()}.png")

        llmInterface = "chatgpt"

        if llmInterface in ("llamacpp", "llamacppserver", "ollama", "gemini", "groq"):
            config.stopSpinning()

            # customize width and height
            promptStyle = Style.from_dict({
                # User input (default text).
                "": config.terminalCommandEntryColor2,
                # Prompt.
                "indicator": config.terminalPromptIndicatorColor2,
            })
            change = False
            print2("Specify the width:")
            new_width = SinglePrompt.run(style=promptStyle, default=str(config.stableDiffusion_output_width), validator=NumberValidator())
            if new_width and not new_width.strip().lower() == config.exit_entry and int(new_width) > 0 and not new_width == config.stableDiffusion_output_width:
                config.stableDiffusion_output_width = int(new_width)
                change = True
            print2("Specify the height:")
            new_height = SinglePrompt.run(style=promptStyle, default=str(config.stableDiffusion_output_height), validator=NumberValidator())
            if new_height and not new_height.strip().lower() == config.exit_entry and int(new_height) > 0 and not new_height == config.stableDiffusion_output_height:
                config.stableDiffusion_output_height = int(new_height)
                change = True
            if change:
                config.saveConfig()

            downloadStableDiffusionFiles()
            stable_diffusion = StableDiffusion(
                model_path=config.stableDiffusion_model_path,
                lora_model_dir=os.path.join(config.localStorage, "LLMs", "stable_diffusion", "lora"),
                wtype="default", # Weight type (options: default, f32, f16, q4_0, q4_1, q5_0, q5_1, q8_0)
                # seed=1337, # Uncomment to set a specific seed
                verbose=config.stableDiffusion_verbose,
                n_threads=getCpuThreads(),
            )
            stable_diffusion.txt_to_img(
                prompt,
                width=config.stableDiffusion_output_width,
                height=config.stableDiffusion_output_height,
            )[0].save(imageFile)
            openImageFile(imageFile)
            return ""

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
        #jsonFile = os.path.join(config.toolMateAIFolder, "temp", "openai_image.json")
        #with open(jsonFile, mode="w", encoding="utf-8") as fileObj:
        #    json.dump(response.data[0].b64_json, fileObj)
        image_data = b64decode(response.data[0].b64_json)
        with open(imageFile, mode="wb") as pngObj:
            pngObj.write(image_data)
        openImageFile(imageFile)
        return ""

    functionSignature = {
        "examples": [
            "generate image",
            "create image",
        ],
        "name": "create_image_dalle3",
        "description": "Create an image with DALLE-3",
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

    config.addFunctionCall(signature=functionSignature, method=create_image_dalle3)