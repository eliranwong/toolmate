from freegenius import config
from freegenius.utils.file_utils import FileUtil
from packaging import version
from bs4 import BeautifulSoup
import platform, shutil, subprocess, os, pydoc, webbrowser, re, socket, wcwidth, unicodedata, traceback, html2text, ollama
import datetime, requests, netifaces, textwrap, json, geocoder, base64, getpass, pendulum, pkg_resources, chromadb, uuid
import pygments
from pygments.lexers.python import PythonLexer
from pygments.styles import get_style_by_name
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import prompt
import tiktoken
import openai
from openai import OpenAI
from urllib.parse import quote
from pathlib import Path
from PIL import Image
if not config.isTermux:
    from autogen.retrieve_utils import TEXT_FORMATS
from typing import Callable
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from ollama import Options


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
        # remove old tool store, allowing changes in plugins
        try:
            config.tool_store_client.delete_collection("tools")
            print("Old tool store removed!")
        except:
            print(traceback.format_exc())
        
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
        config.chatGPTApiFunctionSignatures = {}
        config.chatGPTApiAvailableFunctions = {}

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
            del config.chatGPTApiFunctionSignatures["integrate_google_searches"]
        for i in config.chatGPTApiAvailableFunctions:
            if not i in ("python_qa",):
                callEntry = f"[CALL_{i}]"
                if not callEntry in config.inputSuggestions:
                    config.inputSuggestions.append(callEntry)

    # integrate function call plugin
    @staticmethod
    def addFunctionCall(signature: str, method: Callable[[dict], str]):
        name = signature["name"]
        config.chatGPTApiFunctionSignatures[name] = {key: value for key, value in signature.items() if not key in ("intent", "examples")}
        config.chatGPTApiAvailableFunctions[name] = method
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
        systemMessage1 = config.systemMessage_letmedoit if config.systemMessage_letmedoit else f'''You’re {config.letMeDoItName}, an advanced AI assistant, capable of both engaging in conversations and executing codes on my device.
I am providing the basic information of my device below in case you need it:
```
{SharedUtil.getDeviceInfo()}
```
Please use the current time and date that I have provided above as a reference point for any relative dates and times mentioned in my prompt.
'''

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

        if config.llmServer == "ollama":
            systemMessage = systemMessage1
        elif config.llmServer == "chatgpt":
            systemMessage = systemMessage2

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
        return str(config.pythonFunctionResponse) if config.pythonFunctionResponse is not None and (type(config.pythonFunctionResponse) in (int, float, str, list, tuple, dict, set, bool) or str(type(config.pythonFunctionResponse)).startswith("<class 'numpy.")) and not ("os.system(" in code) else ""

    @staticmethod
    def autoHealPythonCode(code, trace):
        for i in range(config.max_consecutive_auto_heal):
            userInput = f"Original python code:\n```\n{code}\n```\n\nTraceback:\n```\n{trace}\n```"
            config.print3(f"Auto-correction attempt: {(i + 1)}")
            function_call_message, function_call_response = SharedUtil.getSingleFunctionResponse(userInput, [config.chatGPTApiFunctionSignatures["heal_python"]], "heal_python")
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
            answer = SharedUtil.getSingleChatResponse(content, temperature=0.0)
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
        if config.includeIpInSystemMessageTemp or includeIp or (config.includeIpInSystemMessage and config.includeIpInSystemMessageTemp):
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

    # function call related methods

    @staticmethod
    def getSingleFunctionResponse(userInput, functionSignatures, function_name, temperature=None):
        messages=[{"role": "user", "content" : userInput}]
        return SharedUtil.getFunctionMessageAndResponse(messages, functionSignatures, function_name, temperature=temperature)

    @staticmethod
    @check_openai_errors
    def getSingleChatResponse(userInput, temperature=None):
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

    # call a specific function and return messages
    @staticmethod
    def runFunction(messages, functionSignatures, function_name):
        messagesCopy = messages[:]
        try:
            function_call_message, function_call_response = SharedUtil.getFunctionMessageAndResponse(messages, functionSignatures, function_name)
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
    def getFunctionMessageAndResponse(messages, functionSignatures, function_name, temperature=None):
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
        function_call_response = SharedUtil.getFunctionResponse(func_arguments, function_name)
        return function_call_message_mini, function_call_response

    @staticmethod
    def getFunctionResponse(func_arguments, function_name):
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
        elif not function_name in config.chatGPTApiAvailableFunctions:
            if config.developer:
                config.print(f"Unexpected function: {function_name}")
                config.print(config.divider)
                print(func_arguments)
                config.print(config.divider)
            function_response = "[INVALID]"
        else:
            notifyDeveloper(function_name)
            fuction_to_call = config.chatGPTApiAvailableFunctions[function_name]
            # convert the arguments from json into a dict
            function_args = json.loads(func_arguments)
            function_response = fuction_to_call(function_args)
        return function_response

    @staticmethod
    @check_openai_errors
    def runCompletion(thisMessage, noFunctionCall=False):
        if config.llmServer == "ollama":
            return CallOllama.runCompletion(thisMessage, noFunctionCall)

        functionJustCalled = False
        def runThisCompletion(thisThisMessage):
            nonlocal functionJustCalled
            if config.chatGPTApiFunctionSignatures and not functionJustCalled and not noFunctionCall:
                return config.oai_client.chat.completions.create(
                    model=config.chatGPTApiModel,
                    messages=thisThisMessage,
                    n=1,
                    temperature=config.llmTemperature,
                    max_tokens=SharedUtil.getDynamicTokens(thisThisMessage, config.chatGPTApiFunctionSignatures.values()),
                    tools=SharedUtil.convertFunctionSignaturesIntoTools([config.chatGPTApiFunctionSignatures[config.runSpecificFuntion]] if config.runSpecificFuntion and config.runSpecificFuntion in config.chatGPTApiFunctionSignatures else config.chatGPTApiFunctionSignatures.values()),
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
                    func_response = SharedUtil.getFunctionResponse(func_arguments, func_name)

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

    # tool store related

    @staticmethod
    def setupToolStoreClient():
        tool_store = os.path.join(SharedUtil.getLocalStorage(), "tool_store")
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
        name, description, parameters = signature["name"], signature["description"], signature["parameters"]["properties"]
        print(f"Adding tool: {name}")
        if "examples" in signature:
            description = description + "\n" + "\n".join(signature["examples"])
        collection = SharedUtil.get_or_create_collection("tools")
        metadata = {
            "name": name,
            "parameters": json.dumps(parameters),
        }
        SharedUtil.add_vector(collection, description, metadata)

class CallOllama:

    @staticmethod
    def runCompletion(messages: dict, noFunctionCall: bool = False):
        user_request = messages[-1]["content"]
        # 1. Intent Screening
        if config.developer:
            config.print("screening ...")
        noFunctionCall = True if noFunctionCall else CallOllama.screen_user_request(messages=messages, user_request=user_request, model=config.ollamaDefaultModel)
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
            metadatas = search_result["metadatas"][0][0]
            tool_name, tool_schema = metadatas["name"], json.loads(metadatas["parameters"])
            # 3. Parameter Extraction
            if config.developer:
                config.print("extracting parameters ...")
            tool_parameters = CallOllama.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages)
            # 4. Function Execution
            if config.developer:
                config.print("executing function ...")
            tool_response = CallOllama.executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
            # 5. Chat Extension
            if tool_response == "[INVALID]":
                # invalid tool call; return a regular call instead
                return CallOllama.regularCall(messages)
            elif tool_response:
                messages += [
                    {"role": "assistant", "content": json.dumps(tool_parameters)},
                    {"role": "assistant", "content": tool_response},
                ]
                return CallOllama.regularCall(messages)
            else:
                # tool function executed without chat extension
                return None

    @staticmethod
    @check_ollama_errors
    def regularCall(messages: dict):
        return ollama.chat(
            #keep_alive=0,
            model=config.ollamaDefaultModel,
            messages=messages,
            #format="json",
            stream=True,
            options=Options(
                temperature=config.llmTemperature,
                num_ctx=100000,
                num_predict=-1,
            ),
        )

    @staticmethod
    @check_ollama_errors
    def screen_user_request(messages: dict, user_request: str, model: str) -> bool:
        """
        Check if the applied model is able to resolve user request directly or not.
        Assistant delivers a direct answer if the model is capable to resolve the request.
        Look further to extend assistant's capabilities if the requested task exceeds the model's limits.
        """

        # edit user request with a prefix
        prompt_prefix = """Answer either {"answer": "YES"} or {"answer": "NO"} in JSON format, to tell weather you can resolve my request. 
Answer {"answer": "NO"} if you are not provided with adequate context or knowledge base to answer my request.
Answer {"answer": "NO"} if my request requires access to real-time or device information that you are not provided with.
Answer {"answer": "NO"} if you are unable to execute the requested task.
Answer {"answer": "YES"} if you have adequate provided context or knowledge base to provide a direct answer. 

REMEMBER: 
Response with a JSON string that contains a single key only, i.e. "answer", and its value must be either "YES" or "NO". Therefore, your reponse can ONLY be either {"answer": "YES"} or {"answer": "NO"}, without the actual answer or extra information. 

HERE IS MY REQUEST:

"""

        messages[-1]["content"] = prompt_prefix + user_request

        completion = ollama.chat(
            #keep_alive=0,
            model=model,
            messages=messages,
            format="json",
            stream=False,
            options=Options(
                temperature=0.0,
                num_ctx=100000,
                num_predict=10,
            ),
        )
        return True if "yes" in completion["message"]["content"].lower() else False

    @staticmethod
    @check_ollama_errors
    def getResponseDict(messages, **kwargs):
        try:
            completion = ollama.chat(
                #keep_alive=0,
                model=config.ollamaDefaultModel,
                messages=messages,
                format="json",
                stream=False,
                options=Options(
                    temperature=0.0,
                    num_ctx=100000,
                    num_predict=-1,
                ),
                **kwargs,
            )
            jsonOutput = completion["message"]["content"]
            responseDict = json.loads(jsonOutput)
            if config.developer:
                print(responseDict)
            return responseDict
        except:
            print(traceback.format_exc())
            return {}

    @staticmethod
    def extractToolParameters(schema: dict, userInput: str, ongoingMessages: list = []) -> dict:
        """
        Extract action parameters
        """
        def getPrompt(template, parameter, parameterDetails):
            return f"""Use the following template to response in JSON format:

{template}

YOU MUST FOLLOW THESE INSTRUCTIONS CAREFULLY.                                        
<instructions>        
1. Based on my input{" and our ongoing conversation" if ongoingMessages else ""}, fill in the value of the key '{parameter}' in the JSON string.
- description: {parameterDetails['description']}
- type: {parameterDetails['type']}
2. Return the JSON string to me, without additional notes or explanation
</instructions>

Here is my input:

"""
        template = {}
        for parameter in schema:
            parameterDetails = schema[parameter]
            template[parameter] = "" if parameterDetails['type'] == "string" else []
            messages = [
                *ongoingMessages,
                {"role": "user", "content": f"""{getPrompt(template, parameter, parameterDetails)}{userInput}"""},
            ]
            template = CallOllama.getResponseDict(messages)
        return template

    @staticmethod
    def executeToolFunction(func_arguments, function_name):
        def notifyDeveloper(func_name):
            if config.developer:
                #config.print(f"running function '{func_name}' ...")
                print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Running function</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{func_name}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
        if not function_name in config.chatGPTApiAvailableFunctions:
            if config.developer:
                config.print(f"Unexpected function: {function_name}")
                config.print(config.divider)
                print(func_arguments)
                config.print(config.divider)
            function_response = "[INVALID]"
        else:
            notifyDeveloper(function_name)
            function_response = config.chatGPTApiAvailableFunctions[function_name](func_arguments)
        return function_response