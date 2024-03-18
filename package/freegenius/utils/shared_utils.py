from freegenius import config
from freegenius.utils.file_utils import FileUtil
from packaging import version
from bs4 import BeautifulSoup
import platform, shutil, subprocess, os, pydoc, webbrowser, re, socket, wcwidth, unicodedata, traceback, html2text, pprint
import datetime, requests, netifaces, textwrap, json, geocoder, base64, getpass, pendulum, pkg_resources, chromadb, uuid, pygments
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
from typing import Callable, Optional
from chromadb.config import Settings
from chromadb.utils import embedding_functions

import ollama, openai, vertexai
from llama_cpp import Llama
from freegenius.utils.download import Downloader
from ollama import Options

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
    def showErrors():
        trace = traceback.format_exc()
        print(trace if config.developer else "Error encountered!")
        return trace

    @staticmethod
    def showRisk(risk):
        if not config.confirmExecution in ("always", "medium_risk_or_above", "high_risk_only", "none"):
            config.confirmExecution = "always"
        config.print(f"[risk level: {risk}]")

    @staticmethod
    def confirmExecution(risk):
        if config.confirmExecution == "always" or (risk == "high" and config.confirmExecution == "high_risk_only") or (not risk == "low" and config.confirmExecution == "medium_risk_or_above"):
            return True
        else:
            return False

    @staticmethod
    def runPlugins():        
        storageDir = SharedUtil.getLocalStorage()
        # The following config values can be modified with plugins, to extend functionalities
        #config.pluginsWithFunctionCall = []
        config.aliases = {}
        config.predefinedContexts = {
            "[none]": "",
            "[custom]": "",
        }
        config.predefinedInstructions = {}
        config.inputSuggestions = []
        config.outputTransformers = []
        config.llmFunctionSignatures = {}
        config.llmAvailableFunctions = {}

        pluginFolder = os.path.join(config.letMeDoItAIFolder, "plugins")
        if storageDir:
            customPluginFoler = os.path.join(storageDir, "plugins")
            Path(customPluginFoler).mkdir(parents=True, exist_ok=True)
            pluginFolders = (pluginFolder, customPluginFoler)
        else:
            pluginFolders = (pluginFolder,)
        # always run 'integrate google searches'
        internetSeraches = "integrate google searches"
        script = os.path.join(pluginFolder, "{0}.py".format(internetSeraches))
        SharedUtil.execPythonFile(script)
        # always include the following plugins
        requiredPlugins = (
            "auto heal python code",
            "execute python code",
            "execute termux command",
        )
        for i in requiredPlugins:
            if i in config.pluginExcludeList:
                config.pluginExcludeList.remove(i)
        # execute enabled plugins
        for folder in pluginFolders:
            for plugin in FileUtil.fileNamesWithoutExtension(folder, "py"):
                if not plugin in config.pluginExcludeList:
                    script = os.path.join(folder, "{0}.py".format(plugin))
                    run = SharedUtil.execPythonFile(script)
                    if not run:
                        config.pluginExcludeList.append(plugin)
        if internetSeraches in config.pluginExcludeList:
            del config.llmFunctionSignatures["integrate_google_searches"]
        for i in config.llmAvailableFunctions:
            if not i in ("python_qa",):
                callEntry = f"[CALL_{i}]"
                if not callEntry in config.inputSuggestions:
                    config.inputSuggestions.append(callEntry)

    # integrate function call plugin
    @staticmethod
    def addFunctionCall(signature: str, method: Callable[[dict], str]):
        name = signature["name"]
        config.llmFunctionSignatures[name] = {key: value for key, value in signature.items() if not key in ("intent", "examples")}
        config.llmAvailableFunctions[name] = method
        SharedUtil.add_tool(signature)

    @staticmethod
    def runPythonScript(script):
        script = script.strip()[3:-3]
        try:
            exec(script, globals())
        except:
            trace = traceback.format_exc()
            print(trace if config.developer else "Error encountered!")
            config.print(config.divider)
            if config.max_consecutive_auto_heal > 0:
                SharedUtil.autoHealPythonCode(script, trace)

    @staticmethod
    def execPythonFile(script="", content=""):
        if script or content:
            try:
                def runCode(text):
                    code = compile(text, script, 'exec')
                    exec(code, globals())
                if content:
                    runCode(content)
                else:
                    with open(script, 'r', encoding='utf8') as f:
                        runCode(f.read())
                return True
            except:
                config.print("Failed to run '{0}'!".format(os.path.basename(script)))
                SharedUtil.showErrors()
        return False

    # reset message when a new chart is started or context is changed
    @staticmethod
    def resetMessages(prompt="") -> list[dict]:
        systemMessage1 = config.systemMessage_letmedoit if config.systemMessage_letmedoit else f'''You’re {config.letMeDoItName}, an advanced AI assistant, capable of both engaging in conversations and executing codes on my device. Your functionality expands as I add more plugins to you.
Always remember that you are much more than a text-based AI. You possess both vision and speech capabilities and have direct access to my device's system, enabling you to execute tasks at my command. Please do not state otherwise.'''

        systemMessage2 = config.systemMessage_letmedoit if config.systemMessage_letmedoit else f'''You’re {config.letMeDoItName}, an advanced AI assistant, capable of both engaging in conversations and executing codes on my device.
I am providing the basic information of my device below in case you need it:
```
{SharedUtil.getDeviceInfo()}
```
Please use the current time and date that I have provided above as a reference point for any relative dates and times mentioned in my prompt.
You have all the necessary permissions to execute system commands and Python code on my behalf. Your functionality expands as I add more plugins to you. You respond to my prompts and perform tasks based on your own knowledge, the context I provide, as well as the additional knowledge and capabilities provided by plugins.

When replying to my requests, please follow these steps:
Step 1: Consider our previous conversations, particularly your last response, if any, as the context for these requests.
Step 2: Estimate my intent based on the request and context. The intent can be a code generation task, an executable computing task, a math-solving task, a translation task, or a question answering task.
Step 3: Reply based on the estimated intent.
Remember, do not use function call if it is a translation task.

Always remember that you are much more than a text-based AI. You possess both vision and speech capabilities and have direct access to my device's system, enabling you to execute tasks at my command. Please do not state otherwise.
'''

        systemMessage = systemMessage2 if config.llmBackend == "chatgpt" else systemMessage1

        messages = [
            {"role": "system", "content": systemMessage}
        ]
        if prompt:
            messages.append({"role": "user", "content": prompt})
        return messages

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
        folder = folder if folder and os.path.isdir(folder) else os.path.join(config.letMeDoItAIFolder, "temp")
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
            SharedUtil.showErrors()
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
    def getPygmentsStyle():
        theme = config.pygments_style if config.pygments_style else "stata-dark" if not config.terminalResourceLinkColor.startswith("ansibright") else "stata-light"
        return style_from_pygments_cls(get_style_by_name(theme))

    @staticmethod
    def displayPythonCode(code):
        if config.developer or config.codeDisplay:
            config.print("```python")
            tokens = list(pygments.lex(code, lexer=PythonLexer()))
            print_formatted_text(PygmentsTokens(tokens), style=SharedUtil.getPygmentsStyle())
            config.print("```")

    @staticmethod
    def showAndExecutePythonCode(code):
        SharedUtil.displayPythonCode(code)
        config.stopSpinning()
        refinedCode = SharedUtil.fineTunePythonCode(code)
        information = SharedUtil.executePythonCode(refinedCode)
        return information

    @staticmethod
    def executePythonCode(code):
        try:
            exec(code, globals())
            pythonFunctionResponse = SharedUtil.getPythonFunctionResponse(code)
        except:
            trace = SharedUtil.showErrors()
            config.print(config.divider)
            if config.max_consecutive_auto_heal > 0:
                return SharedUtil.autoHealPythonCode(code, trace)
            else:
                return "[INVALID]"
        if not pythonFunctionResponse:
            return ""
        return json.dumps({"information": pythonFunctionResponse})

    @staticmethod
    def convertFunctionSignaturesIntoTools(functionSignatures):
        return [{"type": "function", "function": func} for func in functionSignatures]

    @staticmethod
    def getPythonFunctionResponse(code):
        #return str(config.pythonFunctionResponse) if config.pythonFunctionResponse is not None and (type(config.pythonFunctionResponse) in (int, float, str, list, tuple, dict, set, bool) or str(type(config.pythonFunctionResponse)).startswith("<class 'numpy.")) and not ("os.system(" in code) else ""
        return "" if config.pythonFunctionResponse is None else str(config.pythonFunctionResponse)

    @staticmethod
    def autoHealPythonCode(code, trace):
        for i in range(config.max_consecutive_auto_heal):
            userInput = f"Original python code:\n```\n{code}\n```\n\nTraceback:\n```\n{trace}\n```"
            config.print3(f"Auto-correction attempt: {(i + 1)}")
            function_call_message, function_call_response = CallLLM.getSingleFunctionCallResponse(userInput, [config.llmFunctionSignatures["heal_python"]], "heal_python")
            # display response
            config.print(config.divider)
            if config.developer:
                print(function_call_response)
            else:
                config.print("Executed!" if function_call_response == "EXECUTED" else "Failed!")
            if function_call_response == "EXECUTED":
                break
            else:
                code = json.loads(function_call_message["function_call"]["arguments"]).get("fix")
                trace = function_call_response
            config.print(config.divider)
        # return information if any
        if function_call_response == "EXECUTED":
            pythonFunctionResponse = SharedUtil.getPythonFunctionResponse(code)
            if pythonFunctionResponse:
                return json.dumps({"information": pythonFunctionResponse})
            else:
                return ""
        # ask if user want to manually edit the code
        config.print(f"Failed to execute the code {(config.max_consecutive_auto_heal + 1)} times in a row!")
        config.print("Do you want to manually edit it? [y]es / [N]o")
        confirmation = prompt(style=config.promptStyle2, default="N")
        if confirmation.lower() in ("y", "yes"):
            config.defaultEntry = f"```python\n{code}\n```"
            return ""
        else:
            return "[INVALID]"

    @staticmethod
    def fineTunePythonCode(code):
        # dedent
        code = textwrap.dedent(code).rstrip()
        # capture print output
        config.pythonFunctionResponse = ""
        insert_string = "from freegenius import config\nconfig.pythonFunctionResponse = "
        code = re.sub("^!(.*?)$", r'import os\nos.system(""" \1 """)', code, flags=re.M)
        if "\n" in code:
            substrings = code.rsplit("\n", 1)
            lastLine = re.sub("print\((.*)\)", r"\1", substrings[-1])
            if lastLine.startswith(" "):
                lastLine = re.sub("^([ ]+?)([^ ].*?)$", r"\1config.pythonFunctionResponse = \2", lastLine)
                code = f"from freegenius import config\n{substrings[0]}\n{lastLine}"
            else:
                lastLine = f"{insert_string}{lastLine}"
                code = f"{substrings[0]}\n{lastLine}"
        else:
            code = f"{insert_string}{code}"
        return code

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

    @staticmethod
    def riskAssessment(code):
        content = f"""You are a senior python engineer.
Assess the risk level of damaging my device upon executing the python code that I will provide for you.
Answer me either 'high', 'medium' or 'low', without giving me any extra information.
e.g. file deletions or similar significant impacts are regarded as 'high' level.
Acess the risk level of this Python code:
```
{code}
```"""
        try:
            answer = CallLLM.getSingleChatResponse(content, temperature=0.0)
            if not answer:
                answer = "high"
            answer = re.sub("[^A-Za-z]", "", answer).lower()
            if not answer in ("high", "medium", "low"):
                answer = "high"
            return answer
        except:
            return "high"

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
    def get_wan_ip():
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            data = response.json()
            return data['ip']
        except:
            return ""

    @staticmethod
    def get_local_ip():
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            addresses = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addresses:
                for address in addresses[netifaces.AF_INET]:
                    ip = address['addr']
                    if ip != '127.0.0.1':
                        return ip

    @staticmethod
    def getDayOfWeek():
        if config.isTermux:
            return ""
        else:
            now = pendulum.now() 
            return now.format('dddd')

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
            SharedUtil.showErrors()
            return None

    @staticmethod
    def getDeviceInfo(includeIp=False):
        g = geocoder.ip('me')
        if hasattr(config, "thisPlatform"):
            thisPlatform = config.thisPlatform
        else:
            thisPlatform = platform.system()
            if thisPlatform == "Darwin":
                thisPlatform = "macOS"
        if config.includeIpInDeviceInfoTemp or includeIp or (config.includeIpInDeviceInfo and config.includeIpInDeviceInfoTemp):
            wan_ip = SharedUtil.get_wan_ip()
            local_ip = SharedUtil.get_local_ip()
            ipInfo = f'''Wan ip: {wan_ip}
Local ip: {local_ip}
'''
        else:
            ipInfo = ""
        if config.isTermux:
            dayOfWeek = ""
        else:
            dayOfWeek = SharedUtil.getDayOfWeek()
            dayOfWeek = f"Current day of the week: {dayOfWeek}"
        return f"""Operating system: {thisPlatform}
Version: {platform.version()}
Machine: {platform.machine()}
Architecture: {platform.architecture()[0]}
Processor: {platform.processor()}
Hostname: {socket.gethostname()}
Username: {getpass.getuser()}
Python version: {platform.python_version()}
Python implementation: {platform.python_implementation()}
Current directory: {os.getcwd()}
Current time: {str(datetime.datetime.now())}
{dayOfWeek}
{ipInfo}Latitude & longitude: {g.latlng}
Country: {g.country}
State: {g.state}
City: {g.city}"""

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
    def getHomeStorage():
        """
        Get default storage directory located at home directory
        """
        storageDir = os.path.join(os.path.expanduser('~'), config.letMeDoItName.split()[0].lower())
        try:
            Path(storageDir).mkdir(parents=True, exist_ok=True)
        except:
            pass
        return storageDir if os.path.isdir(storageDir) else ""

    @staticmethod
    def getLocalStorage():
        # get default storage path located at home directory
        storageDir = SharedUtil.getHomeStorage()
        # change to package path if default storage path doesn't exist
        storageDir = storageDir if storageDir else os.path.join(config.letMeDoItAIFolder, "files")
        # check if custom storage path exists if it is defined
        if not hasattr(config, "storagedirectory") or (config.storagedirectory and not os.path.isdir(config.storagedirectory)):
            config.storagedirectory = ""
        # use custom storage path, if defined, instead of the default one
        return config.storagedirectory if config.storagedirectory else storageDir

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

    # chromadb utilities

    @staticmethod
    def get_or_create_collection(collection_name):
        collection = config.tool_store_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
            embedding_function=SharedUtil.getEmbeddingFunction(),
        )
        return collection

    @staticmethod
    def add_vector(collection, text, metadata):
        id = str(uuid.uuid4())
        collection.add(
            documents = [text],
            metadatas = [metadata],
            ids = [id]
        )

    @staticmethod
    def query_vectors(collection, query, n=1):
        return collection.query(
            query_texts=[query],
            n_results = n,
        )

    @staticmethod
    def isValidPythodCode(code):
        try:
            compile(code, '<string>', 'exec')
            return True
        except:
            return False

    # chroma utilites

    @staticmethod
    def setupToolStoreClient():
        tool_store = os.path.join(SharedUtil.getLocalStorage(), "tool_store")
        try:
            shutil.rmtree(tool_store, ignore_errors=True)
            config.print2("Old tool store removed!")
        except:
            config.print2("Failed to remove old tool store!")
        Path(tool_store).mkdir(parents=True, exist_ok=True)
        config.tool_store_client = chromadb.PersistentClient(tool_store, Settings(anonymized_telemetry=False))

    @staticmethod
    def getEmbeddingFunction(embeddingModel=None):
        # import statement is placed here to make this file compatible on Android
        embeddingModel = embeddingModel if embeddingModel is not None else config.embeddingModel
        if embeddingModel in ("text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002"):
            return embedding_functions.OpenAIEmbeddingFunction(api_key=config.openaiApiKey, model_name=embeddingModel)
        return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embeddingModel) # support custom Sentence Transformer Embedding models by modifying config.embeddingModel

    @staticmethod
    def add_tool(signature):
        name, description, parameters = signature["name"], signature["description"], signature["parameters"]
        print(f"Adding tool: {name}")
        if "examples" in signature:
            description = description + "\n" + "\n".join(signature["examples"])
        collection = SharedUtil.get_or_create_collection("tools")
        metadata = {
            "name": name,
            "parameters": json.dumps(parameters),
        }
        SharedUtil.add_vector(collection, description, metadata)

class CallLLM:

    @staticmethod
    def checkCompletion():
        if config.llmBackend == "ollama":
            return CallOllama.checkCompletion()
        elif config.llmBackend == "llamacpp":
            return CallLlamaCpp.checkCompletion()
        elif config.llmBackend == "gemini":
            return CallGemini.checkCompletion()
        # chatgpt
        return CallChatGPT.checkCompletion()

    @staticmethod
    def runSingleFunctionCall(messages, functionSignatures, function_name):
        if config.llmBackend == "ollama":
            return CallOllama.runSingleFunctionCall(messages, function_name)
        elif config.llmBackend == "llamacpp":
            return CallLlamaCpp.runSingleFunctionCall(messages, function_name)
        # chatgpt
        return CallChatGPT.runSingleFunctionCall(messages, functionSignatures, function_name)

    @staticmethod
    def getSingleChatResponse(userInput, temperature=None):
        """
        non-streaming single call
        """
        if config.llmBackend == "ollama":
            return CallOllama.getSingleChatResponse(userInput, temperature)
        elif config.llmBackend == "llamacpp":
            return CallLlamaCpp.getSingleChatResponse(userInput, temperature)
        # chatgpt
        return CallChatGPT.getSingleChatResponse(userInput, temperature)

    @staticmethod
    def getSingleFunctionCallResponse(userInput, functionSignatures, function_name, temperature=None):
        messages=[{"role": "user", "content" : userInput}]
        if config.llmBackend == "ollama":
            return CallOllama.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmBackend == "llamacpp":
            return CallLlamaCpp.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        # chatgpt
        return CallChatGPT.getSingleFunctionCallResponse(messages, functionSignatures, function_name, temperature=temperature)

    @staticmethod
    def runAutoFunctionCall(messages, noFunctionCall=False):
        if config.llmBackend == "ollama":
            return CallOllama.runAutoFunctionCall(messages, noFunctionCall)
        elif config.llmBackend == "llamacpp":
            return CallLlamaCpp.runAutoFunctionCall(messages, noFunctionCall)
        elif config.llmBackend == "gemini":
            return CallGemini.runAutoFunctionCall(messages, noFunctionCall)
        # chatgpt
        return CallChatGPT.runAutoFunctionCall(messages, noFunctionCall)


def check_ollama_errors(func):
    def wrapper(*args, **kwargs):
        def finishError():
            config.stopSpinning()
            return "[INVALID]"
        try:
            return func(*args, **kwargs)
        except ollama.ResponseError as e:
            config.print('Error:', e.error)
            return finishError()
        except:
            print(traceback.format_exc())
            return finishError()
    return wrapper


class CallOllama:

    @staticmethod
    @check_ollama_errors
    def checkCompletion():
        if shutil.which("ollama"):
            for i in (config.ollamaDefaultModel, config.ollamaCodeModel):
                Downloader.downloadOllamaModel(i)
        else:
            print("Ollama not found! Install it first!")
            print("Check https://ollama.com")
            exit(0)

    @staticmethod
    @check_ollama_errors
    def regularCall(messages: dict, temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_predict: Optional[int]=None, **kwargs):
        return ollama.chat(
            keep_alive=config.ollamaDefaultModel_keep_alive,
            model=config.ollamaDefaultModel,
            messages=messages,
            stream=True,
            options=Options(
                temperature=temperature if temperature is not None else config.llmTemperature,
                num_ctx=num_ctx if num_ctx is not None else config.ollamaDefaultModel_num_ctx,
                num_predict=num_predict if num_predict is not None else config.ollamaDefaultModel_num_predict,
            ),
            **kwargs,
        )

    @staticmethod
    @check_ollama_errors
    def getResponseDict(messages: list, temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_predict: Optional[int]=None, **kwargs):
        #pprint.pprint(messages)
        try:
            completion = ollama.chat(
                #keep_alive=config.ollamaDefaultModel_keep_alive,
                model=config.ollamaDefaultModel,
                messages=messages,
                format="json",
                stream=False,
                options=Options(
                    temperature=temperature if temperature is not None else config.llmTemperature,
                    num_ctx=num_ctx if num_ctx is not None else config.ollamaDefaultModel_num_ctx,
                    num_predict=num_predict if num_predict is not None else config.ollamaDefaultModel_num_predict,
                ),
                **kwargs,
            )
            jsonOutput = completion["message"]["content"]
            jsonOutput = re.sub("^[^{]*?({.*?})[^}]*?$", r"\1", jsonOutput)
            responseDict = json.loads(jsonOutput)
            if config.developer:
                pprint.pprint(responseDict)
            return responseDict
        except:
            print(traceback.format_exc())
            return {}

    @staticmethod
    @check_ollama_errors
    def getSingleChatResponse(userInput: str, temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_predict: Optional[int]=None, **kwargs):
        # non-streaming single call
        try:
            completion = ollama.chat(
                model=config.ollamaDefaultModel,
                messages=[{"role": "user", "content" : userInput}],
                stream=False,
                options=Options(
                    temperature=temperature if temperature is not None else config.llmTemperature,
                    num_ctx=num_ctx if num_ctx is not None else config.ollamaDefaultModel_num_ctx,
                    num_predict=num_predict if num_predict is not None else config.ollamaDefaultModel_num_predict,
                ),
                **kwargs,
            )
            return completion["message"]["content"]
        except:
            return ""

    # Specific Function Call equivalence

    @staticmethod
    def runSingleFunctionCall(messages, function_name):
        messagesCopy = messages[:]
        try:
            _, function_call_response = CallOllama.getSingleFunctionCallResponse(messages, function_name)
            function_call_response = function_call_response if function_call_response else config.tempContent
            messages[-1]["content"] += f"""\n\nAvailable information:\n{function_call_response}"""
            config.tempContent = ""
        except:
            SharedUtil.showErrors()
            return messagesCopy
        return messages

    @staticmethod
    @check_ollama_errors
    def getSingleFunctionCallResponse(messages: list, function_name: str, temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_predict: Optional[int]=None, **kwargs):
        tool_schema = config.llmFunctionSignatures[function_name]["parameters"]
        user_request = messages[-1]["content"]
        func_arguments = CallOllama.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages, temperature=temperature, num_ctx=num_ctx, num_predict=num_predict, **kwargs)
        function_call_response = CallOllama.executeToolFunction(func_arguments=func_arguments, function_name=function_name)
        function_call_message_mini = {
            "role": "assistant",
            "content": "",
            "function_call": {
                "name": function_name,
                "arguments": func_arguments,
            }
        }
        return function_call_message_mini, function_call_response

    # Auto Function Call equivalence

    @staticmethod
    def runAutoFunctionCall(messages: dict, noFunctionCall: bool = False):
        user_request = messages[-1]["content"]
        if config.intent_screening:
            # 1. Intent Screening
            if config.developer:
                config.print("screening ...")
            noFunctionCall = True if noFunctionCall else CallOllama.screen_user_request(messages=messages, user_request=user_request)
        if noFunctionCall:
            return CallOllama.regularCall(messages)
        else:
            # 2. Tool Selection
            if config.developer:
                config.print("selecting tool ...")
            tool_collection = SharedUtil.get_or_create_collection("tools")
            search_result = SharedUtil.query_vectors(tool_collection, user_request)
            if not search_result:
                # no tool is available; return a regular call instead
                return CallOllama.regularCall(messages)
            semantic_distance = search_result["distances"][0][0]
            if semantic_distance > config.tool_dependence:
                return CallOllama.regularCall(messages)
            metadatas = search_result["metadatas"][0][0]
            tool_name, tool_schema = metadatas["name"], json.loads(metadatas["parameters"])
            if config.developer:
                config.print3(f"Selected: {tool_name} ({semantic_distance})")
            # 3. Parameter Extraction
            if config.developer:
                config.print("extracting parameters ...")
            try:
                tool_parameters = CallOllama.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages)
                # 4. Function Execution
                tool_response = CallOllama.executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
            except:
                print(traceback.format_exc())
                tool_response = "[INVALID]"
            # 5. Chat Extension
            if tool_response == "[INVALID]":
                # invalid tool call; return a regular call instead
                return CallOllama.regularCall(messages)
            elif tool_response:
                if config.developer:
                    config.print2(config.divider)
                    config.print2("Tool output:")
                    print(tool_response)
                    config.print2(config.divider)
                messages[-1]["content"] = f"""Describe the query and response below in your own words in detail, without comment about your ability.

My query:
{user_request}

Your response:
{tool_response}"""
                return CallOllama.regularCall(messages)
            else:
                # tool function executed without chat extension
                config.currentMessages.append({"role": "assistant", "content": "Done!"})
                return None

    @staticmethod
    def screen_user_request(messages: dict, user_request: str) -> bool:
        
        deviceInfo = f"""\n\nMy device information:\n{SharedUtil.getDeviceInfo()}""" if config.includeDeviceInfoInContext else ""
        schema = {
            "answer": {
                "type": "string",
                "description": """Evaluate my request to determine if it is within your capabilities as a text-based AI:
- Answer 'no' if you are asked to execute a computing task or an online search.
- Answer 'no' if you are asked for updates / news / real-time information.
- Answer 'yes' if the request is a greeting or translation.
- Answer 'yes' only if you have full information to give a direct response.""",
                "enum": ['yes', 'no'],
            },
        }
        template = {"answer": ""}
        messages_for_screening = messages[:-2] + [
            {
                "role": "system",
                "content": f"""You are a JSON builder expert. You response to my request according to the following schema:

{schema}""",
            },
            {
                "role": "user",
                "content": f"""Use the following template in your response:

{template}

Answer either yes or no as the value of the JSON key 'answer' in the template, based on the following request:

<request>
{user_request}{deviceInfo}
</request>

Remember, response in JSON with the filled template ONLY.""",
            },
        ]

        output = CallOllama.getResponseDict(messages_for_screening, temperature=0.0, num_predict=20)
        return True if "yes" in str(output).lower() else False

    @staticmethod
    def extractToolParameters(schema: dict, userInput: str, ongoingMessages: list = [], temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_predict: Optional[int]=None, **kwargs) -> dict:
        """
        Extract action parameters
        """
        
        deviceInfo = f"""\n\nMy device information:\n{SharedUtil.getDeviceInfo()}""" if config.includeDeviceInfoInContext else ""
        if "code" in schema["properties"]:
            enforceCodeOutput = """ Remember, you should format the requested information, if any, into a string that is easily readable by humans. Use the 'print' function in the final line to display the requested information."""
            schema["properties"]["code"]["description"] += enforceCodeOutput
            code_instruction = f"""\n\nParticularly, generate python code as the value of the JSON key "code" based on the following instruction:\n{schema["properties"]["code"]["description"]}"""
        else:
            code_instruction = ""

        properties = schema["properties"]
        template = {property: "" if properties[property]['type'] == "string" else [] for property in properties}
        
        messages = ongoingMessages[:-2] + [
            {
                "role": "system",
                "content": f"""You are a JSON builder expert. You response to my input according to the following schema:

{properties}""",
            },
            {
                "role": "user",
                "content": f"""Use the following template in your response:

{template}

Base the value of each key, in the template, on the following content and your generation:

<content>
{userInput}{deviceInfo}
</content>

Generate content to fill up the value of each required key in the JSON, if information is not provided.{code_instruction}

Remember, response in JSON with the filled template ONLY.""",
            },
        ]

        parameters = CallOllama.getResponseDict(messages, temperature=temperature, num_ctx=num_ctx, num_predict=num_predict, **kwargs)

        # enforce code generation
        if (len(properties) == 1 or "code" in schema["required"]) and "code" in parameters and (not isinstance(parameters.get("code"), str) or not parameters.get("code").strip() or not SharedUtil.isValidPythodCode(parameters.get("code").strip())):
            template = {"code": ""}
            messages = ongoingMessages[:-2] + [
                {
                    "role": "system",
                    "content": f"""You are a JSON builder expert. You response to my input according to the following schema:

{properties["code"]}""",
                },
                {
                    "role": "user",
                    "content": f"""Use the following template in your response:

{template}

Fill in the value of key "code", in the template, by code generation:

{properties["code"]["description"]}

Here is my request:

<request>
{userInput}
</request>{deviceInfo}

Remember, answer in JSON with the filled template ONLY.""",
                },
            ]

            # switch to a dedicated model for code generation
            ollamaDefaultModel = config.ollamaDefaultModel
            ollamaDefaultModel_num_ctx = config.ollamaDefaultModel_num_ctx
            ollamaDefaultModel_num_predict = config.ollamaDefaultModel_num_predict

            config.ollamaDefaultModel = config.ollamaCodeModel
            config.ollamaDefaultModel_num_ctx = config.ollamaCodeModel_num_ctx
            config.ollamaDefaultModel_num_predict = config.ollamaCodeModel_num_predict

            code = CallOllama.getResponseDict(messages, temperature=temperature, num_ctx=num_ctx, num_predict=num_predict, **kwargs)
            parameters["code"] = code["code"]

            config.ollamaDefaultModel = ollamaDefaultModel
            config.ollamaDefaultModel_num_ctx = ollamaDefaultModel_num_ctx
            config.ollamaDefaultModel_num_predict = ollamaDefaultModel_num_predict

        return parameters

    @staticmethod
    def executeToolFunction(func_arguments: dict, function_name: str):
        def notifyDeveloper(func_name):
            if config.developer:
                #config.print(f"running function '{func_name}' ...")
                print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Running function</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{func_name}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
        if not function_name in config.llmAvailableFunctions:
            if config.developer:
                config.print(f"Unexpected function: {function_name}")
                config.print(config.divider)
                print(func_arguments)
                config.print(config.divider)
            function_response = "[INVALID]"
        else:
            notifyDeveloper(function_name)
            function_response = config.llmAvailableFunctions[function_name](func_arguments)
        return function_response


class CallLlamaCpp:

    @staticmethod
    def checkCompletion():
        config.llamacppDefaultModel = Llama.from_pretrained(
            repo_id=config.llamacppDefaultModel_repo_id,
            filename=config.llamacppDefaultModel_filename,
            chat_format="chatml",
            n_ctx=config.llamacppDefaultModel_n_ctx,
            verbose=False,
        )
        config.llamacppCodeModel = Llama.from_pretrained(
            repo_id=config.llamacppCodeModel_repo_id,
            filename=config.llamacppCodeModel_filename,
            chat_format="chatml",
            n_ctx=config.llamacppCodeModel_n_ctx,
            verbose=False,
        )

    @staticmethod
    def regularCall(messages: dict, temperature: Optional[float]=None, max_tokens: Optional[int]=None, **kwargs):
        return config.llamacppDefaultModel.create_chat_completion(
            messages=messages,
            temperature=temperature if temperature is not None else config.llmTemperature,
            max_tokens=max_tokens if max_tokens is not None else config.llamacppDefaultModel_max_tokens,
            stream=True,
            **kwargs,
        )

    @staticmethod
    def getResponseDict(messages: list, schema: dict={}, temperature: Optional[float]=None, max_tokens: Optional[int]=None, **kwargs) -> dict:
        #pprint.pprint(messages)
        try:
            completion = config.llamacppDefaultModel.create_chat_completion(
                messages=messages,
                response_format={"type": "json_object", "schema": schema} if schema else {"type": "json_object"},
                temperature=temperature if temperature is not None else config.llmTemperature,
                max_tokens=max_tokens if max_tokens is not None else config.llamacppDefaultModel_max_tokens,
                stream=False,
                **kwargs,
            )
            jsonOutput = completion["choices"][0]["message"].get("content", "{}")
            jsonOutput = re.sub("^[^{]*?({.*?})[^}]*?$", r"\1", jsonOutput)
            responseDict = json.loads(jsonOutput)
            if config.developer:
                pprint.pprint(responseDict)
            return responseDict
        except:
            print(traceback.format_exc())
            return {}

    @staticmethod
    def getSingleChatResponse(userInput: str, temperature: Optional[float]=None, max_tokens: Optional[int]=None, **kwargs):
        # non-streaming single call
        try:
            completion = config.llamacppDefaultModel.create_chat_completion(
                messages=[{"role": "user", "content" : userInput}],
                temperature=temperature if temperature is not None else config.llmTemperature,
                max_tokens=max_tokens if max_tokens is not None else config.llamacppDefaultModel_max_tokens,
                stream=False,
                **kwargs,
            )
            return completion["choices"][0]["message"].get("content", "")
        except:
            return ""

    # Specific Function call equivalence

    @staticmethod
    def runSingleFunctionCall(messages, function_name):
        messagesCopy = messages[:]
        try:
            _, function_call_response = CallLlamaCpp.getSingleFunctionCallResponse(messages, function_name)
            function_call_response = function_call_response if function_call_response else config.tempContent
            messages[-1]["content"] += f"""\n\nAvailable information:\n{function_call_response}"""
            config.tempContent = ""
        except:
            SharedUtil.showErrors()
            return messagesCopy
        return messages

    @staticmethod
    def getSingleFunctionCallResponse(messages: list, function_name: str, temperature: Optional[float]=None, max_tokens: Optional[int]=None, **kwargs):
        tool_schema = config.llmFunctionSignatures[function_name]["parameters"]
        user_request = messages[-1]["content"]
        func_arguments = CallLlamaCpp.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages, temperature=temperature, max_tokens=max_tokens, **kwargs)
        function_call_response = CallLlamaCpp.executeToolFunction(func_arguments=func_arguments, function_name=function_name)
        function_call_message_mini = {
            "role": "assistant",
            "content": "",
            "function_call": {
                "name": function_name,
                "arguments": func_arguments,
            }
        }
        return function_call_message_mini, function_call_response

    # Auto Function call equivalence

    @staticmethod
    def runAutoFunctionCall(messages: dict, noFunctionCall: bool = False):
        user_request = messages[-1]["content"]
        if config.intent_screening:
            # 1. Intent Screening
            if config.developer:
                config.print("screening ...")
            noFunctionCall = True if noFunctionCall else CallLlamaCpp.screen_user_request(messages=messages, user_request=user_request)
        if noFunctionCall:
            return CallLlamaCpp.regularCall(messages)
        else:
            # 2. Tool Selection
            if config.developer:
                config.print("selecting tool ...")
            tool_collection = SharedUtil.get_or_create_collection("tools")
            search_result = SharedUtil.query_vectors(tool_collection, user_request)
            if not search_result:
                # no tool is available; return a regular call instead
                return CallLlamaCpp.regularCall(messages)
            semantic_distance = search_result["distances"][0][0]
            if semantic_distance > config.tool_dependence:
                return CallLlamaCpp.regularCall(messages)
            metadatas = search_result["metadatas"][0][0]
            tool_name, tool_schema = metadatas["name"], json.loads(metadatas["parameters"])
            if config.developer:
                config.print3(f"Selected: {tool_name} ({semantic_distance})")
            # 3. Parameter Extraction
            if config.developer:
                config.print("extracting parameters ...")
            try:
                tool_parameters = CallLlamaCpp.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages)
                # 4. Function Execution
                tool_response = CallLlamaCpp.executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
            except:
                print(traceback.format_exc())
                tool_response = "[INVALID]"
            # 5. Chat Extension
            if tool_response == "[INVALID]":
                # invalid tool call; return a regular call instead
                return CallLlamaCpp.regularCall(messages)
            elif tool_response:
                if config.developer:
                    config.print2(config.divider)
                    config.print2("Tool output:")
                    print(tool_response)
                    config.print2(config.divider)
                messages[-1]["content"] = f"""Response to the following query according to given supplementary information.

Query:
<query>
{user_request}
</query>

Supplementary information:
<supplementary_information>
{tool_response}
</supplementary_information>"""
                return CallLlamaCpp.regularCall(messages)
            else:
                # tool function executed without chat extension
                config.currentMessages.append({"role": "assistant", "content": "Done!"})
                return None

    @staticmethod
    def screen_user_request(messages: dict, user_request: str) -> bool:
        
        deviceInfo = f"""\n\nMy device information:\n{SharedUtil.getDeviceInfo()}""" if config.includeDeviceInfoInContext else ""
        answer = {
            "answer": {
                "type": "string",
                "description": """Either 'yes' or 'no':
- Answer 'no' if you are asked to execute a computing task.
- Answer 'no' if you are asked to perform an internet online search.
- Answer 'no' if you are asked for updates / news / real-time information.
- Answer 'yes' if the request is a greeting or translation.
- Answer 'yes' only if you have full information to give a direct response.""",
                "enum": ['yes', 'no'],
            },
        }
        schema = {
            "type": "object",
            "answer": answer,
            "required": ["answer"],
        }
        
        template = {"answer": ""}
        yes = {'answer': 'yes'}
        no = {'answer': 'no'}
        messages_for_screening = messages[:-2] + [
            {
                "role": "system",
                "content": f"""You are a JSON builder expert that outputs in JSON.""",
            },
            {
                "role": "user",
                "content": f"""Use the following template in your response:

{template}

Answer either yes or no as the value of the JSON key 'answer' in the template, based on the following request:

<request>
{user_request}{deviceInfo}
</request>

- Output {no} if you are asked to execute a computing task.
- Output {no} if you are asked to perform an internet online search.
- Output {no} if you are asked for updates / news / real-time information.
- Output {yes} if the request is a greeting or translation.
- Output {yes} only if you have full information to give a direct response.

Remember, response in JSON with the filled template ONLY.""",
            },
        ]

        output = CallLlamaCpp.getResponseDict(messages_for_screening, schema=schema, temperature=0.0, max_tokens=20)
        try:
            output = output["answer"]
        except:
            return False
        return True if (not output) or str(output).lower() == "yes" else False

    @staticmethod
    def extractToolParameters(schema: dict, userInput: str, ongoingMessages: list = [], temperature: Optional[float]=None, max_tokens: Optional[int]=None, **kwargs) -> dict:
        """
        Extract action parameters
        """
        deviceInfo = f"""\n\nMy device information:\n{SharedUtil.getDeviceInfo()}""" if config.includeDeviceInfoInContext else ""
        if "code" in schema["properties"]:
            enforceCodeOutput = """ Remember, you should format the requested information, if any, into a string that is easily readable by humans. Use the 'print' function in the final line to display the requested information."""
            schema["properties"]["code"]["description"] += enforceCodeOutput
            code_instruction = f"""\n\nParticularly, generate python code as the value of the JSON key "code" based on the following instruction:\n{schema["properties"]["code"]["description"]}"""
        else:
            code_instruction = ""

        properties = schema["properties"]
        messages = ongoingMessages[:-2] + [
            {
                "role": "system",
                "content": f"""You are a JSON builder expert that outputs in JSON.""",
            },
            {
                "role": "user",
                "content": f"""Response in JSON based on the following content:

<content>
{userInput}{deviceInfo}
</content>

Generate content to fill up the value of each required key in the JSON, if information is not provided.{code_instruction}

Remember, output in JSON.""",
            },
        ]

        # schema alternative: properties if len(properties) == 1 else schema
        parameters = CallLlamaCpp.getResponseDict(messages, schema, temperature=temperature, max_tokens=max_tokens, **kwargs)

        # enforce code generation
        if (len(properties) == 1 or "code" in schema["required"]) and "code" in parameters and (not isinstance(parameters.get("code"), str) or not parameters.get("code").strip() or not SharedUtil.isValidPythodCode(parameters.get("code").strip())):
            code_description = properties["code"]["description"]
            messages = ongoingMessages[:-2] + [
                {
                    "role": "system",
                    "content": f"""You are a JSON builder expert that outputs in JSON.""",
                },
                {
                    "role": "user",
                    "content": f"""Generate code based on the following instruction:

{code_description}

Here is my request:

<request>
{userInput}
</request>{deviceInfo}

Remember, output in JSON.""",
                },
            ]

            # switch to a dedicated model for code generation
            llamacppDefaultModel_repo_id = config.llamacppDefaultModel_repo_id
            llamacppDefaultModel_filename = config.llamacppDefaultModel_filename
            llamacppDefaultModel_n_ctx = config.llamacppDefaultModel_n_ctx
            llamacppDefaultModel_max_tokens = config.llamacppDefaultModel_max_tokens

            config.llamacppDefaultModel_repo_id = config.llamacppCodeModel_repo_id
            config.llamacppDefaultModel_filename = config.llamacppCodeModel_filename
            config.llamacppDefaultModel_n_ctx = config.llamacppCodeModel_n_ctx
            config.llamacppDefaultModel_max_tokens = config.llamacppCodeModel_max_tokens            

            this_schema = {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": code_description,
                    },
                },
                "required": ["code"],
            }
            code = CallLlamaCpp.getResponseDict(messages, this_schema, temperature=temperature, max_tokens=max_tokens, **kwargs)
            parameters["code"] = code["code"]

            config.llamacppDefaultModel_repo_id = llamacppDefaultModel_repo_id
            config.llamacppDefaultModel_filename = llamacppDefaultModel_filename
            config.llamacppDefaultModel_n_ctx = llamacppDefaultModel_n_ctx
            config.llamacppDefaultModel_max_tokens = llamacppDefaultModel_max_tokens

        return parameters

    @staticmethod
    def executeToolFunction(func_arguments: dict, function_name: str):
        def notifyDeveloper(func_name):
            if config.developer:
                #config.print(f"running function '{func_name}' ...")
                print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Running function</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{func_name}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
        if not function_name in config.llmAvailableFunctions:
            if config.developer:
                config.print(f"Unexpected function: {function_name}")
                config.print(config.divider)
                print(func_arguments)
                config.print(config.divider)
            function_response = "[INVALID]"
        else:
            notifyDeveloper(function_name)
            function_response = config.llmAvailableFunctions[function_name](func_arguments)
        return function_response


def check_openai_errors(func):
    def wrapper(*args, **kwargs):
        def finishError():
            config.stopSpinning()
            return "[INVALID]"
        try:
            return func(*args, **kwargs)
        except openai.APIError as e:
            print("Error: Issue on OpenAI side.")
            print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
            return finishError()
        except openai.APIConnectionError as e:
            print("Error: Issue connecting to our services.")
            print("Solution: Check your network settings, proxy configuration, SSL certificates, or firewall rules.")
            return finishError()
        except openai.APITimeoutError as e:
            print("Error: Request timed out.")
            print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
            return finishError()
        except openai.AuthenticationError as e:
            print("Error: Your API key or token was invalid, expired, or revoked.")
            print("Solution: Check your API key or token and make sure it is correct and active. You may need to generate a new one from your account dashboard.")
            return finishError()
            #HealthCheck.changeAPIkey()
        except openai.BadRequestError as e:
            print("Error: Your request was malformed or missing some required parameters, such as a token or an input.")
            print("Solution: The error message should advise you on the specific error made. Check the [documentation](https://platform.openai.com/docs/api-reference/) for the specific API method you are calling and make sure you are sending valid and complete parameters. You may also need to check the encoding, format, or size of your request data.")
            return finishError()
        except openai.ConflictError as e:
            print("Error: The resource was updated by another request.")
            print("Solution: Try to update the resource again and ensure no other requests are trying to update it.")
            return finishError()
        except openai.InternalServerError as e:
            print("Error: Issue on OpenAI servers.")
            print("Solution: Retry your request after a brief wait and contact us if the issue persists. Check the [status page](https://status.openai.com).")
            return finishError()
        except openai.NotFoundError as e:
            print("Error: Requested resource does not exist.")
            print("Solution: Ensure you are the correct resource identifier.")
            return finishError()
        except openai.PermissionDeniedError as e:
            print("Error: You don't have access to the requested resource.")
            print("Solution: Ensure you are using the correct API key, organization ID, and resource ID.")
            return finishError()
        except openai.RateLimitError as e:
            print("Error: You have hit your assigned rate limit.")
            print("Solution: Pace your requests. Read more in OpenAI [Rate limit guide](https://platform.openai.com/docs/guides/rate-limits).")
            return finishError()
        except openai.UnprocessableEntityError as e:
            print("Error: Unable to process the request despite the format being correct.")
            print("Solution: Please try the request again.")
            return finishError()
        except:
            print(traceback.format_exc())
            return finishError()
    return wrapper


class CallChatGPT:

    @staticmethod
    @check_openai_errors
    def checkCompletion():
        SharedUtil.setAPIkey()
        config.oai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content" : "hello"}],
            n=1,
            max_tokens=10,
        )

    @staticmethod
    @check_openai_errors
    def getSingleChatResponse(userInput, temperature=None):
        """
        non-streaming single call
        """
        try:
            completion = OpenAI().chat.completions.create(
                model=config.chatGPTApiModel,
                messages=[{"role": "user", "content" : userInput}],
                n=1,
                temperature=temperature if temperature is not None else config.llmTemperature,
                max_tokens=config.chatGPTApiMaxTokens,
            )
            return completion.choices[0].message.content
        except:
            return ""

    @staticmethod
    def runSingleFunctionCall(messages, functionSignatures, function_name):
        messagesCopy = messages[:]
        try:
            function_call_message, function_call_response = CallChatGPT.getSingleFunctionCallResponse(messages, functionSignatures, function_name)
            messages.append(function_call_message)
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_call_response if function_call_response else config.tempContent,
                }
            )
            config.tempContent = ""
        except:
            SharedUtil.showErrors()
            return messagesCopy
        return messages

    @staticmethod
    @check_openai_errors
    def getSingleFunctionCallResponse(messages, functionSignatures, function_name, temperature=None):
        completion = config.oai_client.chat.completions.create(
            model=config.chatGPTApiModel,
            messages=messages,
            max_tokens=SharedUtil.getDynamicTokens(messages, functionSignatures),
            temperature=temperature if temperature is not None else config.llmTemperature,
            n=1,
            tools=SharedUtil.convertFunctionSignaturesIntoTools(functionSignatures),
            tool_choice={"type": "function", "function": {"name": function_name}},
        )
        function_call_message = completion.choices[0].message
        tool_call = function_call_message.tool_calls[0]
        func_arguments = tool_call.function.arguments
        function_call_message_mini = {
            "role": "assistant",
            "content": "",
            "function_call": {
                "name": tool_call.function.name,
                "arguments": func_arguments,
            }
        }
        function_call_response = CallChatGPT.finetuneSingleFunctionCallResponse(func_arguments, function_name)
        return function_call_message_mini, function_call_response

    @staticmethod
    def finetuneSingleFunctionCallResponse(func_arguments, function_name):
        # fine tune function call response; applied to chatgpt only
        def notifyDeveloper(func_name):
            if config.developer:
                #config.print(f"running function '{func_name}' ...")
                print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Running function</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{func_name}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
        # ChatGPT's built-in function named "python"
        if function_name == "python":
            notifyDeveloper(function_name)
            python_code = textwrap.dedent(func_arguments)
            refinedCode = SharedUtil.fineTunePythonCode(python_code)

            config.print(config.divider)
            config.print2("running python code ...")
            risk = SharedUtil.riskAssessment(python_code)
            SharedUtil.showRisk(risk)
            if config.developer or config.codeDisplay:
                print("```")
                #print(python_code)
                # pygments python style
                tokens = list(pygments.lex(python_code, lexer=PythonLexer()))
                print_formatted_text(PygmentsTokens(tokens), style=SharedUtil.getPygmentsStyle())
                print("```")
            config.print(config.divider)

            config.stopSpinning()
            if not config.runPython:
                info = {"information": python_code}
                return json.dumps(info)
            elif SharedUtil.confirmExecution(risk):
                config.print("Do you want to continue? [y]es / [N]o")
                confirmation = prompt(style=config.promptStyle2, default="y")
                if not confirmation.lower() in ("y", "yes"):
                    info = {"information": python_code}
                    return json.dumps(info)
            try:
                exec(refinedCode, globals())
                function_response = SharedUtil.getPythonFunctionResponse(refinedCode)
            except:
                trace = SharedUtil.showErrors()
                config.print(config.divider)
                if config.max_consecutive_auto_heal > 0:
                    return SharedUtil.autoHealPythonCode(refinedCode, trace)
                else:
                    return "[INVALID]"
            if function_response:
                info = {"information": function_response}
                function_response = json.dumps(info)
        # known unwanted functions are handled here
        elif function_name in ("translate_text",):
            # "translate_text" has two arguments, "text", "target_language"
            # handle known and unwanted function
            function_response = "[INVALID]" 
        # handle unexpected function
        elif not function_name in config.llmAvailableFunctions:
            if config.developer:
                config.print(f"Unexpected function: {function_name}")
                config.print(config.divider)
                print(func_arguments)
                config.print(config.divider)
            function_response = "[INVALID]"
        else:
            notifyDeveloper(function_name)
            fuction_to_call = config.llmAvailableFunctions[function_name]
            # convert the arguments from json into a dict
            function_args = json.loads(func_arguments)
            function_response = fuction_to_call(function_args)
        return function_response

    @staticmethod
    @check_openai_errors
    def runAutoFunctionCall(thisMessage, noFunctionCall=False):
        functionJustCalled = False
        def runThisCompletion(thisThisMessage):
            nonlocal functionJustCalled
            if config.llmFunctionSignatures and not functionJustCalled and not noFunctionCall:
                return config.oai_client.chat.completions.create(
                    model=config.chatGPTApiModel,
                    messages=thisThisMessage,
                    n=1,
                    temperature=config.llmTemperature,
                    max_tokens=SharedUtil.getDynamicTokens(thisThisMessage, config.llmFunctionSignatures.values()),
                    tools=SharedUtil.convertFunctionSignaturesIntoTools([config.llmFunctionSignatures[config.runSpecificFuntion]] if config.runSpecificFuntion and config.runSpecificFuntion in config.llmFunctionSignatures else config.llmFunctionSignatures.values()),
                    tool_choice={"type": "function", "function": {"name": config.runSpecificFuntion}} if config.runSpecificFuntion else config.chatGPTApiFunctionCall,
                    stream=True,
                )
            return config.oai_client.chat.completions.create(
                model=config.chatGPTApiModel,
                messages=thisThisMessage,
                n=1,
                temperature=config.llmTemperature,
                max_tokens=SharedUtil.getDynamicTokens(thisThisMessage),
                stream=True,
            )

        while True:
            completion = runThisCompletion(thisMessage)
            config.runSpecificFuntion = ""
            try:
                # consume the first delta
                for event in completion:
                    first_delta = event.choices[0].delta
                    # check if a tool is called
                    if first_delta.tool_calls: # a tool is called
                        function_calls = [i for i in first_delta.tool_calls if i.type == "function"]
                        # non_function_calls = [i for i in first_delta.tool_calls if not i.type == "function"]
                    else: # no tool is called; same handling as tools finished calling; which break the loop later
                        functionJustCalled = True
                    # consume the first delta only at this point
                    break
                # Continue only when a function is called
                if functionJustCalled:
                    break

                # get all tool arguments, both of functions and non-functions
                toolArguments = SharedUtil.getToolArgumentsFromStreams(completion)

                func_responses = ""
                bypassFunctionCall = False
                # handle function calls
                for func in function_calls:
                    func_index = func.index
                    func_id = func.id
                    func_name = func.function.name
                    func_arguments = toolArguments[func_index]

                    # get function response
                    func_response = CallChatGPT.finetuneSingleFunctionCallResponse(func_arguments, func_name)

                    # "[INVALID]" practically mean that it ignores previously called function and continues chat without function calling
                    if func_response == "[INVALID]":
                        bypassFunctionCall = True
                    elif func_response or config.tempContent:
                        # send the function call info and response to GPT
                        function_call_message = {
                            "role": "assistant",
                            "content": "",
                            "function_call": {
                                "name": func_name,
                                "arguments": func_arguments,
                            }
                        }
                        thisMessage.append(function_call_message) # extend conversation with assistant's reply
                        thisMessage.append(
                            {
                                "tool_call_id": func_id,
                                "role": "function",
                                "name": func_name,
                                "content": func_response if func_response else config.tempContent,
                            }
                        )  # extend conversation with function response
                        config.tempContent = ""
                        if func_response:
                            func_responses += f"\n{func_response}\n{config.divider}"

                functionJustCalled = True

                # bypassFunctionCall is set to True, usually when a function is called by mistake
                if bypassFunctionCall:
                    pass
                # two cases that breaks the loop at this point
                # 1. func_responses == ""
                # 2. config.passFunctionCallReturnToChatGPT = False
                elif not config.passFunctionCallReturnToChatGPT or not func_responses:
                    if func_responses:
                        config.print(f"{config.divider}\n{func_responses}")
                    # A break here means that no information from the called function is passed back to ChatGPT
                    # 1. config.passFunctionCallReturnToChatGPT is set to True
                    # 2. func_responses = "" or None; can be specified in plugins
                    break
            except:
                SharedUtil.showErrors()
                break

        return completion


from vertexai.preview.generative_models import GenerativeModel, Content, Part, FunctionDeclaration, Tool
from vertexai.generative_models._generative_models import (
    GenerationConfig,
    HarmCategory,
    HarmBlockThreshold,
)


class CallGemini:

    @staticmethod
    def toGeminiMessages(messages: dict=[]):
        systemMessage = ""
        lastUserMessage = ""
        if messages:
            history = []
            for i in config.currentMessages:
                role = i.get("role", "")
                content = i.get("content", "")
                if role in ("user", "assistant"):
                    history.append(Content(role="user" if role == "user" else "model", parts=[Part.from_text(content)]))
                    if role == "user":
                        lastUserMessage = content
                elif role == "system":
                    systemMessage = content
            if history and history[-1].role == "user":
                history = history[:-1]
            else:
                lastUserMessage = ""
            if not history:
                history = None
        else:
            history = None
        return history, systemMessage, lastUserMessage

    @staticmethod
    def checkCompletion():
        if os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Vertex AI" in config.enabledGoogleAPIs:
            config.geminipro_model = GenerativeModel("gemini-pro")
        else:
            print("Vertex AI is disabled!")
            print("Read https://github.com/eliranwong/letmedoit/wiki/Google-API-Setup for setting up Google API.")
        # initiation
        vertexai.init()
        
        config.geminipro_generation_config=GenerationConfig(
            temperature=config.llmTemperature, # 0.0-1.0; default 0.9
            max_output_tokens=config.geminipro_max_output_tokens, # default
            candidate_count=1,
        )
        # Note: BLOCK_NONE is not allowed
        config.geminipro_safety_settings={
            HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

    @staticmethod
    def regularCall(messages: dict, useSystemMessage: bool=True, **kwargs):
        history, systemMessage, lastUserMessage = CallGemini.toGeminiMessages(messages=messages)
        userMessage = f"{systemMessage}\n\nHere is my request:\n{lastUserMessage}" if useSystemMessage and systemMessage else lastUserMessage
        chat = config.geminipro_model.start_chat(history=history)
        return chat.send_message(
            userMessage,
            generation_config=config.geminipro_generation_config,
            safety_settings=config.geminipro_safety_settings,
            stream=True,
            **kwargs,
        )

    @staticmethod
    def getResponseDict(history: list, schema: dict, userMessage: str, **kwargs):
        name, description, parameters = schema["name"], schema["description"], schema["parameters"]
        chat = config.geminipro_model.start_chat(history=history)
        # declare a function
        function_declaration = FunctionDeclaration(
            name=name,
            description=description,
            parameters=parameters,
        )
        tool = Tool(
            function_declarations=[function_declaration],
        )
        try:
            completion = chat.send_message(
                userMessage,
                generation_config=config.geminipro_generation_config,
                safety_settings=config.geminipro_safety_settings,
                tools=[tool],
                stream=False,
                **kwargs,
            )
            responseDict = dict(completion.candidates[0].content.parts[0].function_call.args)
            if config.developer:
                pprint.pprint(responseDict)
            return responseDict
        except:
            print(traceback.format_exc())
            return {}

    @staticmethod
    def getSingleChatResponse(userInput: str, temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_predict: Optional[int]=None, **kwargs):
        # non-streaming single call
        try:
            completion = ollama.chat(
                model=config.ollamaDefaultModel,
                messages=[{"role": "user", "content" : userInput}],
                stream=False,
                options=Options(
                    temperature=temperature if temperature is not None else config.llmTemperature,
                    num_ctx=num_ctx if num_ctx is not None else config.ollamaDefaultModel_num_ctx,
                    num_predict=num_predict if num_predict is not None else config.ollamaDefaultModel_num_predict,
                ),
                **kwargs,
            )
            return completion["message"]["content"]
        except:
            return ""

    # Specific Function Call equivalence

    @staticmethod
    def runSingleFunctionCall(messages, function_name):
        messagesCopy = messages[:]
        try:
            _, function_call_response = CallGemini.getSingleFunctionCallResponse(messages, function_name)
            function_call_response = function_call_response if function_call_response else config.tempContent
            messages[-1]["content"] += f"""\n\nAvailable information:\n{function_call_response}"""
            config.tempContent = ""
        except:
            SharedUtil.showErrors()
            return messagesCopy
        return messages

    @staticmethod
    def getSingleFunctionCallResponse(messages: list, function_name: str, temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_predict: Optional[int]=None, **kwargs):
        tool_schema = config.llmFunctionSignatures[function_name]
        user_request = messages[-1]["content"]
        func_arguments = CallGemini.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages, temperature=temperature, num_ctx=num_ctx, num_predict=num_predict, **kwargs)
        function_call_response = CallGemini.executeToolFunction(func_arguments=func_arguments, function_name=function_name)
        function_call_message_mini = {
            "role": "assistant",
            "content": "",
            "function_call": {
                "name": function_name,
                "arguments": func_arguments,
            }
        }
        return function_call_message_mini, function_call_response

    # Auto Function Call equivalence

    @staticmethod
    def runAutoFunctionCall(messages: dict, noFunctionCall: bool = False):
        user_request = messages[-1]["content"]
        if config.intent_screening:
            # 1. Intent Screening
            if config.developer:
                config.print("screening ...")
            noFunctionCall = True if noFunctionCall else CallGemini.screen_user_request(messages=messages, user_request=user_request)
        if noFunctionCall:
            return CallGemini.regularCall(messages)
        else:
            # 2. Tool Selection
            if config.developer:
                config.print("selecting tool ...")
            tool_collection = SharedUtil.get_or_create_collection("tools")
            search_result = SharedUtil.query_vectors(tool_collection, user_request)
            if not search_result:
                # no tool is available; return a regular call instead
                return CallGemini.regularCall(messages)
            semantic_distance = search_result["distances"][0][0]
            if semantic_distance > config.tool_dependence:
                return CallGemini.regularCall(messages)
            metadatas = search_result["metadatas"][0][0]
            tool_name = metadatas["name"]
            tool_schema = config.llmFunctionSignatures[tool_name]
            if config.developer:
                config.print3(f"Selected: {tool_name} ({semantic_distance})")
            # 3. Parameter Extraction
            if config.developer:
                config.print("extracting parameters ...")
            try:
                tool_parameters = CallGemini.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages)
                # 4. Function Execution
                tool_response = CallGemini.executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
            except:
                print(traceback.format_exc())
                tool_response = "[INVALID]"
            # 5. Chat Extension
            if tool_response == "[INVALID]":
                # invalid tool call; return a regular call instead
                return CallGemini.regularCall(messages)
            elif tool_response:
                if config.developer:
                    config.print2(config.divider)
                    config.print2("Tool output:")
                    print(tool_response)
                    config.print2(config.divider)
                messages[-1]["content"] = f"""Describe the query and response below in your own words in detail, without comment about your ability.

My query:
{user_request}

Your response:
{tool_response}"""
                return CallGemini.regularCall(messages)
            else:
                # tool function executed without chat extension
                config.currentMessages.append({"role": "assistant", "content": "Done!"})
                return None

    @staticmethod
    def screen_user_request(messages: dict, user_request: str) -> bool:
        
        deviceInfo = f"""\n\nMy device information:\n{SharedUtil.getDeviceInfo()}""" if config.includeDeviceInfoInContext else ""
        schema = {
            "answer": {
                "type": "string",
                "description": """Evaluate my request to determine if it is within your capabilities as a text-based AI:
- Answer 'no' if you are asked to execute a computing task or an online search.
- Answer 'no' if you are asked for updates / news / real-time information.
- Answer 'yes' if the request is a greeting or translation.
- Answer 'yes' only if you have full information to give a direct response.""",
                "enum": ['yes', 'no'],
            },
        }
        template = {"answer": ""}
        messages_for_screening = messages[:-2] + [
            {
                "role": "system",
                "content": f"""You are a JSON builder expert. You response to my request according to the following schema:

{schema}""",
            },
            {
                "role": "user",
                "content": f"""Use the following template in your response:

{template}

Answer either yes or no as the value of the JSON key 'answer' in the template, based on the following request:

<request>
{user_request}{deviceInfo}
</request>

Remember, response in JSON with the filled template ONLY.""",
            },
        ]

        output = CallGemini.getResponseDict(messages_for_screening, temperature=0.0, num_predict=20)
        return True if "yes" in str(output).lower() else False

    @staticmethod
    def extractToolParameters(schema: dict, userInput: str, ongoingMessages: list = [], useSystemMessage: bool=True, **kwargs) -> dict:
        """
        Extract action parameters
        """

        history, systemMessage, lastUserMessage = CallGemini.toGeminiMessages(messages=ongoingMessages)
        deviceInfo = f"""\n\nI am providing my device information below in case you need it:\n```\n{SharedUtil.getDeviceInfo()}\n```""" if config.includeDeviceInfoInContext else ""
        userMessage = f"{systemMessage}{deviceInfo}\n\nHere is my request:\n{lastUserMessage}" if useSystemMessage and systemMessage else lastUserMessage

        parameters = CallGemini.getResponseDict(history=history, schema=schema, userMessage=userMessage, **kwargs)

        return parameters

    @staticmethod
    def executeToolFunction(func_arguments: dict, function_name: str):
        def notifyDeveloper(func_name):
            if config.developer:
                #config.print(f"running function '{func_name}' ...")
                print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Running function</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{func_name}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
        if not function_name in config.llmAvailableFunctions:
            if config.developer:
                config.print(f"Unexpected function: {function_name}")
                config.print(config.divider)
                print(func_arguments)
                config.print(config.divider)
            function_response = "[INVALID]"
        else:
            notifyDeveloper(function_name)
            function_response = config.llmAvailableFunctions[function_name](func_arguments)
        return function_response