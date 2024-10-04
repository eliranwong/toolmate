"""
ToolMate AI Plugin - create images flux

generate images with model "Flux.1"

[TOOL_CALL]
"""


if not config.isTermux:

    from toolmate import config, print2, print3, getCurrentDateTime, getCliOutput, getCpuThreads
    import os
    from pathlib import Path
    from stable_diffusion_cpp import StableDiffusion
    from toolmate.utils.single_prompt import SinglePrompt
    from prompt_toolkit.styles import Style
    from toolmate.utils.promptValidator import NumberValidator

    def downloadFluxModels():
        # reference: https://github.com/william-murray1204/stable-diffusion-cpp-python#flux-image-generation
        # llm directory
        llm_directory = os.path.join(config.localStorage, "LLMs", "flux")
        Path(llm_directory).mkdir(parents=True, exist_ok=True)
        lora_model_dir = os.path.join(llm_directory, "lora")
        Path(lora_model_dir).mkdir(parents=True, exist_ok=True)
        filename = "flux1-dev-q4_k.gguf"
        flux_model_path = os.path.join(llm_directory, filename)
        if not config.flux_model_path or not os.path.isfile(config.flux_model_path):
            config.flux_model_path = flux_model_path

        if not os.path.isfile(config.flux_model_path):
            print2("Downloading Flux.1-dev model ...")
            hf_hub_download(
                repo_id="leejet/FLUX.1-dev-gguf",
                filename=filename,
                local_dir=llm_directory,
                #local_dir_use_symlinks=False,
            )
            flux_model_path = os.path.join(llm_directory, filename)
            if os.path.isfile(flux_model_path):
                config.flux_model_path = flux_model_path
                config.saveConfig()

        filename = "ae.safetensors"
        lora_file = os.path.join(llm_directory, filename)
        if not os.path.isfile(lora_file):
            print2("Downloading Flux.1 vae ...")
            hf_hub_download(
                repo_id="black-forest-labs/FLUX.1-dev",
                filename=filename,
                local_dir=llm_directory,
                #local_dir_use_symlinks=False,
            )

        filename = "clip_l.safetensors"
        lora_file = os.path.join(llm_directory, filename)
        if not os.path.isfile(lora_file):
            print2("Downloading Flux.1 clip_l ...")
            hf_hub_download(
                repo_id="comfyanonymous/flux_text_encoders",
                filename=filename,
                local_dir=llm_directory,
                #local_dir_use_symlinks=False,
            )

        filename = "t5xxl_fp16.safetensors"
        lora_file = os.path.join(llm_directory, filename)
        if not os.path.isfile(lora_file):
            print2("Downloading Flux.1 t5xxl ...")
            hf_hub_download(
                repo_id="comfyanonymous/flux_text_encoders",
                filename=filename,
                local_dir=llm_directory,
                #local_dir_use_symlinks=False,
            )

    def create_image_flux(function_args):
        def callback(step: int, steps: int, time: float):
            print("Completed step: {} of {}".format(step, steps))

        def openImageFile(imageFile):
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
        print1("""Flux.1 natively supports any resolution up to 2 mp (1920x1088), and any aspect ratio thereof. By default will use 1MP 1024x1024 in ToolMate AI. You can take it down to 256x256 and still get good results.""")
        print2("Specify the width:")
        new_width = SinglePrompt.run(style=promptStyle, default=str(config.flux_output_width), validator=NumberValidator())
        if new_width and not new_width.strip().lower() == config.exit_entry and int(new_width) > 0 and not new_width == config.flux_output_width:
            config.flux_output_width = int(new_width)
            change = True
        print2("Specify the height:")
        new_height = SinglePrompt.run(style=promptStyle, default=str(config.flux_output_height), validator=NumberValidator())
        if new_height and not new_height.strip().lower() == config.exit_entry and int(new_height) > 0 and not new_height == config.flux_output_height:
            config.flux_output_height = int(new_height)
            change = True
        print("# Sample steps")
        print1("Increasing the number of sampling steps generally enhances image quality by refining details and reducing noise, but it also requires more processing time.")
        print2("Specify the sample steps:")
        new_flux_sample_steps = SinglePrompt.run(style=promptStyle, default=str(config.flux_sample_steps), validator=NumberValidator())
        if new_flux_sample_steps and not new_flux_sample_steps.strip().lower() == config.exit_entry and int(new_flux_sample_steps) > 0 and not new_flux_sample_steps == config.flux_sample_steps:
            config.flux_sample_steps = int(new_flux_sample_steps)
            change = True
        # save changes
        if change:
            config.saveConfig()

        downloadFluxModels()
        llm_directory = os.path.join(config.localStorage, "LLMs", "flux")
        lora_model_dir = os.path.join(llm_directory, "lora")
        flux = StableDiffusion(
            diffusion_model_path=config.flux_model_path,
            lora_model_dir=lora_model_dir if config.flux_model_path.endswith("flux1-dev-q8_0.gguf") else "", # Only the Flux-dev q8_0 will work with LoRAs.
            wtype="default", # Weight type (options: default, f32, f16, q4_0, q4_1, q5_0, q5_1, q8_0)
            # seed=1337, # Uncomment to set a specific seed
            verbose=config.flux_verbose,
            n_threads=getCpuThreads(),
            clip_l_path=os.path.join(llm_directory, "clip_l.safetensors"),
            t5xxl_path=os.path.join(llm_directory, "t5xxl_fp16.safetensors"),
            vae_path=os.path.join(llm_directory, "ae.safetensors"),
        )
        flux.txt_to_img(
            prompt,
            width=config.flux_output_width,
            height=config.flux_output_height,
            sample_steps=config.flux_sample_steps,
            cfg_scale=1.0, # a cfg_scale of 1 is recommended for FLUX
            sample_method="euler", # euler is recommended for FLUX
            progress_callback=callback,
        )[0].save(imageFile)
        openImageFile(imageFile)
        return ""


    functionSignature = {
        "examples": [
            "generate image",
            "create image",
        ],
        "name": "create_image_flux",
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

    config.addFunctionCall(signature=functionSignature, method=create_image_flux)