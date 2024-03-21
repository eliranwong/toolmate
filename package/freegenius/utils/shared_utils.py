from freegenius.utils.call_llm import CallLLM

from freegenius import config, getPythonFunctionResponse, fineTunePythonCode, getPygmentsStyle, showErrors, getLocalStorage, get_or_create_collection, add_vector

from packaging import version
from bs4 import BeautifulSoup
import platform, shutil, subprocess, os, pydoc, webbrowser, re, wcwidth, unicodedata, traceback, html2text, pprint
import datetime, requests, json, geocoder, base64, pkg_resources, chromadb, uuid, pygments
from pygments.lexers.python import PythonLexer
from pygments.styles import get_style_by_name
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import prompt
import tiktoken
from openai import OpenAI
from urllib.parse import quote
from pathlib import Path
from PIL import Image
if not config.isTermux:
    from autogen.retrieve_utils import TEXT_FORMATS
from typing import Callable, Optional, List, Dict, Union
from chromadb.config import Settings
from chromadb.utils import embedding_functions

import ollama, openai, vertexai
from llama_cpp import Llama
from freegenius.utils.download import Downloader
from ollama import Options

from vertexai.preview.generative_models import GenerativeModel, Content, Part, FunctionDeclaration, Tool
from vertexai.generative_models._generative_models import (
    GenerationConfig,
    HarmCategory,
    HarmBlockThreshold,
)


class SharedUtil:

    # token limit
    # reference: https://platform.openai.com/docs/models/gpt-4
    tokenLimits = {
        "gpt-4-turbo-preview": 128000, # Returns a maximum of 4,096 output tokens.
        "gpt-4-0125-preview": 128000, # Returns a maximum of 4,096 output tokens.
        "gpt-4-1106-preview": 128000, # Returns a maximum of 4,096 output tokens.
        "gpt-3.5-turbo": 16385, # Returns a maximum of 4,096 output tokens.
        "gpt-3.5-turbo-16k": 16385,
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
    }

    @staticmethod
    def setAPIkey():
        # instantiate a client that can shared with plugins
        os.environ["OPENAI_API_KEY"] = config.openaiApiKey
        config.oai_client = OpenAI()
        # set variable 'OAI_CONFIG_LIST' to work with pyautogen
        oai_config_list = []
        for model in SharedUtil.tokenLimits.keys():
            oai_config_list.append({"model": model, "api_key": config.openaiApiKey})
        os.environ["OAI_CONFIG_LIST"] = json.dumps(oai_config_list)

    @staticmethod
    def getPackageInstalledVersion(package):
        try:
            installed_version = pkg_resources.get_distribution(package).version
            return version.parse(installed_version)
        except pkg_resources.DistributionNotFound:
            return None

    @staticmethod
    def getPackageLatestVersion(package):
        try:
            response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=10)
            latest_version = response.json()['info']['version']
            return version.parse(latest_version)
        except:
            return None

    @staticmethod
    def isPackageUpgradable(package):
        latest_version = SharedUtil.getPackageLatestVersion(package)
        installed_version = SharedUtil.getPackageInstalledVersion(package)
        return (latest_version > installed_version)

    # handle document path dragged to the terminal
    @staticmethod
    def isExistingPath(docs_path):
        docs_path = docs_path.strip()
        search_replace = (
            ("^'(.*?)'$", r"\1"),
            ('^(File|Folder): "(.*?)"$', r"\2"),
        )
        for search, replace in search_replace:
            docs_path = re.sub(search, replace, docs_path)
        if "\\ " in docs_path or "\(" in docs_path:
            search_replace = (
                ("\\ ", " "),
                ("\(", "("),
            )
            for search, replace in search_replace:
                docs_path = docs_path.replace(search, replace)
        return docs_path if os.path.exists(os.path.expanduser(docs_path)) else ""

    @staticmethod
    def getCurrentDateTime():
        current_datetime = datetime.datetime.now()
        return current_datetime.strftime("%Y-%m-%d_%H_%M_%S")

    @staticmethod
    def addTimeStamp(content):
        time = re.sub("\.[^\.]+?$", "", str(datetime.datetime.now()))
        return f"{content}\n[Current time: {time}]"

    @staticmethod
    def downloadWebContent(url, timeout=60, folder="", ignoreKind=False):
        config.print2("Downloading web content ...")
        hasExt = re.search("\.([^\./]+?)$", url)
        supported_documents = TEXT_FORMATS[:]
        supported_documents.remove("org")

        response = requests.get(url, timeout=timeout)
        folder = folder if folder and os.path.isdir(folder) else os.path.join(config.freeGeniusAIFolder, "temp")
        filename = quote(url, safe="")
        def downloadBinary(filename=filename):
            filename = os.path.join(folder, filename)
            with open(filename, "wb") as fileObj:
                fileObj.write(response.content)
            return filename
        def downloadHTML(filename=filename):
            filename = os.path.join(folder, f"{filename}.html")
            with open(filename, "w", encoding="utf-8") as fileObj:
                fileObj.write(response.text)
            return filename

        try:
            if ignoreKind:
                filename = downloadBinary()
                config.print3(f"Downloaded at: {filename}")
                return ("any", filename)
            elif hasExt and hasExt.group(1) in supported_documents:
                return ("document", downloadBinary())
            elif SharedUtil.is_valid_image_url(url):
                return ("image", downloadBinary())
            else:
                # download content as text
                # Save the content to a html file
                return ("text", downloadHTML())
        except:
            showErrors()
            return ("", "")

    @staticmethod
    def is_valid_url(url):
        # Regular expression pattern for URL validation
        pattern = re.compile(
            r'^(http|https)://'  # http:// or https://
            r'([a-zA-Z0-9.-]+)'  # domain name
            r'(\.[a-zA-Z]{2,63})'  # dot and top-level domain (e.g. .com, .org)
            r'(:[0-9]{1,5})?'  # optional port number
            r'(/.*)?$'  # optional path
        )
        return bool(re.match(pattern, url))

    @staticmethod
    def is_valid_image_url(url): 
        try: 
            response = requests.head(url, timeout=30)
            content_type = response.headers['content-type'] 
            if 'image' in content_type: 
                return True 
            else: 
                return False 
        except requests.exceptions.RequestException: 
            return False

    @staticmethod
    def is_valid_image_file(file_path):
        try:
            # Open the image file
            with Image.open(file_path) as img:
                # Check if the file format is supported by PIL
                img.verify()
                return True
        except (IOError, SyntaxError) as e:
            # The file path is not a valid image file path
            return False

    # Function to encode the image
    @staticmethod
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        os.path.splitext(os.path.basename(image_path))[1]
        return f"data:image/png;base64,{base64_image}"

    def getWebText(url):
        try:
            # Download webpage content
            response = requests.get(url, timeout=30)
            # Parse the HTML content to extract text
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.get_text()
        except:
            return ""

    @staticmethod
    def transformText(text):
        for transformer in config.outputTransformers:
                text = transformer(text)
        return text

    @staticmethod
    def displayPythonCode(code):
        if config.developer or config.codeDisplay:
            config.print("```python")
            tokens = list(pygments.lex(code, lexer=PythonLexer()))
            print_formatted_text(PygmentsTokens(tokens), style=getPygmentsStyle())
            config.print("```")

    @staticmethod
    def showAndExecutePythonCode(code):
        SharedUtil.displayPythonCode(code)
        config.stopSpinning()
        refinedCode = fineTunePythonCode(code)
        information = SharedUtil.executePythonCode(refinedCode)
        return information

    @staticmethod
    def executePythonCode(code):
        try:
            exec(code, globals())
            pythonFunctionResponse = getPythonFunctionResponse(code)
        except:
            trace = showErrors()
            config.print(config.divider)
            if config.max_consecutive_auto_heal > 0:
                return CallLLM.autoHealPythonCode(code, trace)
            else:
                return "[INVALID]"
        if not pythonFunctionResponse:
            return ""
        return json.dumps({"information": pythonFunctionResponse})

    @staticmethod
    def convertFunctionSignaturesIntoTools(functionSignatures):
        return [{"type": "function", "function": functionSignature} for functionSignature in functionSignatures]

    @staticmethod
    def getDynamicTokens(messages, functionSignatures=None):
        if functionSignatures is None:
            functionTokens = 0
        else:
            functionTokens = SharedUtil.count_tokens_from_functions(functionSignatures)
        tokenLimit = SharedUtil.tokenLimits[config.chatGPTApiModel]
        currentMessagesTokens = SharedUtil.count_tokens_from_messages(messages) + functionTokens
        availableTokens = tokenLimit - currentMessagesTokens
        if availableTokens >= config.chatGPTApiMaxTokens:
            return config.chatGPTApiMaxTokens
        elif (config.chatGPTApiMaxTokens > availableTokens > config.chatGPTApiMinTokens):
            return availableTokens
        return config.chatGPTApiMinTokens

    @staticmethod
    def count_tokens_from_functions(functionSignatures, model=""):
        count = 0
        if not model:
            model = config.chatGPTApiModel
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        for i in functionSignatures:
            count += len(encoding.encode(str(i)))
        return count

    # The following method was modified from source:
    # https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    @staticmethod
    def count_tokens_from_messages(messages, model=""):
        if not model:
            model = config.chatGPTApiModel

        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-0125",
                "gpt-3.5-turbo-1106",
                "gpt-3.5-turbo-0613",
                "gpt-3.5-turbo-16k",
                "gpt-3.5-turbo-16k-0613",
                "gpt-4-turbo-preview",
                "gpt-4-0125-preview",
                "gpt-4-1106-preview",
                "gpt-4-0314",
                "gpt-4-32k-0314",
                "gpt-4",
                "gpt-4-0613",
                "gpt-4-32k",
                "gpt-4-32k-0613",
            }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            #print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return SharedUtil.count_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            #print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return SharedUtil.count_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""count_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            if not "content" in message or not message.get("content", ""):
                num_tokens += len(encoding.encode(str(message)))
            else:
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":
                        num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    # streaming
    @staticmethod
    def getToolArgumentsFromStreams(completion):
        toolArguments = {}
        for event in completion:
            delta = event.choices[0].delta
            if delta and delta.tool_calls:
                for tool_call in delta.tool_calls:
                    # handle functions
                    if tool_call.function:
                        func_index = tool_call.index
                        if func_index in toolArguments:
                            toolArguments[func_index] += tool_call.function.arguments
                        else:
                            toolArguments[func_index] = tool_call.function.arguments
                    # may support non functions later
        return toolArguments

    @staticmethod
    def getWeather(latlng=""):
        # get current weather information
        # Reference: https://openweathermap.org/api/one-call-3

        if not config.openweathermapApi:
            return None

        # latitude, longitude
        if not latlng:
            latlng = geocoder.ip('me').latlng

        try:
            latitude, longitude = latlng
            # Build the URL for the weather API
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={config.openweathermapApi}&units=metric"
            # Make the request to the API
            response = requests.get(url)
            # Parse the JSON response
            data = json.loads(response.text)
            # Get the current weather condition
            weather_condition = data["weather"][0]["description"]
            # Get the current temperature in Celsius
            temperature_celsius = data["main"]["temp"]

            # Convert the temperature to Fahrenheit
            #temperature_fahrenheit = (temperature_celsius * 9/5) + 32

            # Print the weather condition and temperature
            #print(f"The current weather condition is {weather_condition}.")
            #print(f"The current temperature is {temperature_fahrenheit} degrees Fahrenheit.")
            return temperature_celsius, weather_condition
        except:
            showErrors()
            return None

    @staticmethod
    def getStringWidth(text):
        width = 0
        for character in text:
            width += wcwidth.wcwidth(character)
        return width

    @staticmethod
    def is_CJK(text):
        for char in text:
            if 'CJK' in unicodedata.name(char):
                return True
        return False

    @staticmethod
    def isPackageInstalled(package):
        return True if shutil.which(package.split(" ", 1)[0]) else False

    @staticmethod
    def getCliOutput(cli):
        try:
            process = subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, *_ = process.communicate()
            return stdout.decode("utf-8")
        except:
            return ""

    @staticmethod
    def textTool(tool="", content=""):
        command = re.sub(" .*?$", "", tool.strip())
        if command and SharedUtil.isPackageInstalled(command):
            pydoc.pipepager(content, cmd=tool)
            if SharedUtil.isPackageInstalled("pkill"):
                os.system(f"pkill {command}")
        return ""

    @staticmethod
    def runSystemCommand(command):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout  # Captured standard output
        error = result.stderr  # Captured standard error
        response = ""
        response += f"# Output:\n{output}"
        if error.strip():
            response += f"\n# Error:\n{error}"
        return response

    # Function to convert HTML to Markdown
    @staticmethod
    def convert_html_to_markdown(html_string):
        # Create an instance of the HTML2Text converter
        converter = html2text.HTML2Text()
        # Convert the HTML string to Markdown
        markdown_string = converter.handle(html_string)
        # Return the Markdown string
        return markdown_string

    @staticmethod
    def openURL(url):
        config.stopSpinning()
        if config.terminalEnableTermuxAPI:
            command = f'''termux-open-url "{url}"'''
            SharedUtil.runSystemCommand(command)
        else:
            webbrowser.open(url)

    @staticmethod
    def setOsOpenCmd(thisPlatform=""):
        if not thisPlatform:
            thisPlatform = platform.system()
        config.thisPlatform = "macOS" if thisPlatform == "Darwin" else thisPlatform
        if config.terminalEnableTermuxAPI:
            config.open = "termux-share"
        elif thisPlatform == "Linux":
            config.open = "xdg-open"
        elif thisPlatform == "Darwin":
            config.open = "open"
        elif thisPlatform == "Windows":
            config.open = "start"
