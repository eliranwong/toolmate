import vertexai, os, argparse, re
from vertexai.preview.generative_models import GenerativeModel
from vertexai.generative_models._generative_models import (
    GenerationConfig,
    HarmCategory,
    HarmBlockThreshold,
)
from freegenius import config
from freegenius.utils.streaming_word_wrapper import StreamingWordWrapper
from freegenius.health_check import HealthCheck
if not hasattr(config, "currentMessages"):
    HealthCheck.setBasicConfig()
    config.saveConfig()
    #print("Configurations updated!")

import shutil, textwrap
from PIL import Image as im
import requests
import http.client
import typing
import urllib.request
from vertexai.preview.generative_models import Image
from prompt_toolkit.styles import Style


# Install google-cloud-aiplatform FIRST!
#!pip install --upgrade google-cloud-aiplatform


class GeminiProVision:

    def __init__(self, temperature=0.9, max_output_tokens=2048):
        # authentication
        if os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Vertex AI" in config.enabledGoogleAPIs:
            self.runnable = True
        else:
            print("Vertex AI is disabled!")
            print("Read https://github.com/eliranwong/letmedoit/wiki/Google-API-Setup for setting up Google API.")
            self.runnable = False
        # initiation
        vertexai.init()
        self.generation_config=GenerationConfig(
            temperature=temperature, # 0.0-1.0; default 0.9
            max_output_tokens=max_output_tokens, # default
            candidate_count=1,
        )
        self.safety_settings={
            HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

    def refinePath(self, img_path):
        img_path = img_path.strip()
        img_path = re.sub("^'(.*?)'$", r"\1", img_path)
        if "\\ " in img_path or "\(" in img_path:
            img_path = img_path.replace("\\ ", " ")
            img_path = img_path.replace("\(", "(")
        return os.path.expanduser(img_path)

    def run(self, query="", files=[]):
        promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })

        HealthCheck.print2("\nGemini Pro Vision loaded!")
        print(f"""[press '{str(config.hotkey_exit).replace("'", "")[1:-1]}' to exit]""")
        if not files:
            HealthCheck.print2("Enter image path below (file / folder):")
            files = HealthCheck.simplePrompt(style=promptStyle)
        if files:
            # handle path dragged to terminal
            files = self.refinePath(files)
        if files == config.exit_entry:
            pass
        elif files and os.path.exists(files):
            files = [files]
            if not query:
                HealthCheck.print2("Enter your query below:")
                query = HealthCheck.simplePrompt(style=promptStyle)
            if query and not query == config.exit_entry:
                try:
                    function_args = {
                        "query": query,
                        "files": files,
                    }
                    self.analyze_images(function_args)
                except:
                    HealthCheck.showErrors()
        else:
            HealthCheck.print2("Entered path does not exist!")
        HealthCheck.print2("\nGemini Pro Vision closed!")

    def analyze_images(self, function_args):
        def is_valid_url(url: str) -> bool:
            # Regular expression pattern for URL validation
            pattern = re.compile(
                r'^(http|https)://'  # http:// or https://
                r'([a-zA-Z0-9.-]+)'  # domain name
                r'(\.[a-zA-Z]{2,63})'  # dot and top-level domain (e.g. .com, .org)
                r'(:[0-9]{1,5})?'  # optional port number
                r'(/.*)?$'  # optional path
            )
            return bool(re.match(pattern, url))
        def is_valid_image_url(url: str) -> bool:
            try: 
                response = requests.head(url, timeout=30)
                content_type = response.headers['content-type'] 
                if 'image' in content_type: 
                    return True 
                else: 
                    return False 
            except requests.exceptions.RequestException: 
                return False
        def load_image_from_url(image_url: str) -> Image:
            with urllib.request.urlopen(image_url) as response:
                response = typing.cast(http.client.HTTPResponse, response)
                image_bytes = response.read()
            return Image.from_bytes(image_bytes)
        def is_valid_image_file(file_path: str) -> bool:
            try:
                # Open the image file
                with im.open(file_path) as img:
                    # Check if the file format is supported by PIL
                    img.verify()
                    return True
            except (IOError, SyntaxError) as e:
                # The file path is not a valid image file path
                return False
        def load_image_from_file(file_path: str) -> Image:
            with open(file_path, "rb") as file:
                image_bytes = file.read()
            return Image.from_bytes(image_bytes)

        query = function_args.get("query") # required
        files = function_args.get("files") # required
        if not files:
            self.defaultPrompt = f"{query}\n[NO_FUNCTION_CALL]"
            return None
        if isinstance(files, str):
            if not files.startswith("["):
                files = f'["{files}"]'
            files = eval(files)
        else:
            files = list(files)

        # check if some items are directory that contain images
        filesCopy = files[:]
        for item in filesCopy:
            if os.path.isdir(item):
                for root, _, allfiles in os.walk(item):
                    for file in allfiles:
                        file_path = os.path.join(root, file)
                        files.append(file_path)
                files.remove(item)

        content = []
        imageFiles = []
        # validate image paths
        for i in files:
            if is_valid_url(i) and is_valid_image_url(i):
                content.append(load_image_from_url(i))
                imageFiles.append(i)
            elif os.path.isfile(i) and is_valid_image_file(i):
                content.append(load_image_from_file(i))
                imageFiles.append(i)
        content.append(f"{query} Please give your answer in as much detail as possible.")

        if imageFiles:
            HealthCheck.print3(f"Reading: '{', '.join(imageFiles)}'")
            model = GenerativeModel("gemini-pro-vision")
            response = model.generate_content(
                content,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
            )
            if response:
                try:
                    chat_response = response.text.strip()
                    if chat_response:
                        print(StreamingWordWrapper.wrapText(chat_response))
                        return chat_response
                except:
                    HealthCheck.showErrors()
                    return ""
        else:
            HealthCheck.print2("No image file is found!")
        return ""

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="geminipro vision cli options")
    # Add arguments
    parser.add_argument("default", nargs="?", default=None, help="default entry")
    parser.add_argument('-f', '--files', action='store', dest='files', help="specify a file of a directory of files with -f flag")
    parser.add_argument('-o', '--outputtokens', action='store', dest='outputtokens', help="specify maximum output tokens with -o flag; default: 2048")
    parser.add_argument('-t', '--temperature', action='store', dest='temperature', help="specify temperature with -t flag: default: 0.9")
    # Parse arguments
    args = parser.parse_args()
    # Get options
    query = args.default.strip() if args.default and args.default.strip() else ""
    files = [args.files.strip()] if args.files and os.path.exists(args.files.strip()) else []
    if args.outputtokens and args.outputtokens.strip():
        try:
            max_output_tokens = int(args.outputtokens.strip())
        except:
            max_output_tokens = 2048
    else:
        max_output_tokens = 2048
    if max_output_tokens > 2048:
        max_output_tokens = 2048
    if args.temperature and args.temperature.strip():
        try:
            temperature = float(args.temperature.strip())
        except:
            temperature = 0.9
    else:
        temperature = 0.9
    if temperature > 1.0:
        temperature = 1.0
    GeminiProVision(
        temperature=temperature,
        max_output_tokens = max_output_tokens,
    ).run(
        query=query,
        files=files,
    )

if __name__ == '__main__':
    main()