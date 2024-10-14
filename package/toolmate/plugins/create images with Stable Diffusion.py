"""
ToolMate AI Plugin - create images

generate images with model "dall-e-3"

[TOOL_CALL]
"""

if not config.isTermux:

    from toolmate import config, print2, print3, getCurrentDateTime, getCliOutput, getCpuThreads, downloadStableDiffusionFiles
    import os, shutil
    from base64 import b64decode
    from toolmate.utils.call_chatgpt import check_openai_errors
    from toolmate.utils.terminal_mode_dialogs import TerminalModeDialogs
    from openai import OpenAI
    from pathlib import Path
    from stable_diffusion_cpp import StableDiffusion
    from toolmate.utils.single_prompt import SinglePrompt
    from prompt_toolkit.styles import Style
    from toolmate.utils.prompt_validator import NumberValidator


    def create_image_sd(function_args):
        def callback(step: int, steps: int, time: float):
            print("Completed step: {} of {}".format(step, steps))

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

        prompt = function_args.get("prompt") # required

        # image file path
        folder = os.path.join(config.localStorage, "images")
        Path(folder).mkdir(parents=True, exist_ok=True)
        imageFile = os.path.join(folder, f"{getCurrentDateTime()}.png")

        config.stopSpinning()

        # customize width and height
        promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })
        change = False
        print("# Width & Height")
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
        print("# Sample steps")
        print1("Increasing the number of sampling steps generally enhances image quality by refining details and reducing noise, but it also requires more processing time.")
        print2("Specify the sample steps:")
        new_stableDiffusion_sample_steps = SinglePrompt.run(style=promptStyle, default=str(config.stableDiffusion_sample_steps), validator=NumberValidator())
        if new_stableDiffusion_sample_steps and not new_stableDiffusion_sample_steps.strip().lower() == config.exit_entry and int(new_stableDiffusion_sample_steps) > 0 and not new_stableDiffusion_sample_steps == config.stableDiffusion_sample_steps:
            config.stableDiffusion_sample_steps = int(new_stableDiffusion_sample_steps)
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
            sample_steps=config.stableDiffusion_sample_steps,
            progress_callback=callback,
        )[0].save(imageFile)
        openImageFile(imageFile)
        return ""


    functionSignature = {
        "examples": [
            "generate image",
            "create image",
        ],
        "name": "create_image_sd",
        "description": "Create an image with Stable Diffusion Models",
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

    config.addFunctionCall(signature=functionSignature, method=create_image_sd)