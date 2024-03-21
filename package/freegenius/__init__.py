import os
thisFile = os.path.realpath(__file__)
packageFolder = os.path.dirname(thisFile)
package = os.path.basename(packageFolder)
if os.getcwd() != packageFolder:
    os.chdir(packageFolder)
configFile = os.path.join(packageFolder, "config.py")
if not os.path.isfile(configFile):
    open(configFile, "a", encoding="utf-8").close()
from freegenius import config
config.isTermux = True if os.path.isdir("/data/data/com.termux/files/home") else False

import os, geocoder, platform, socket, geocoder, datetime, requests, netifaces, getpass, pendulum, traceback, uuid, re, textwrap, glob
from chromadb.utils import embedding_functions
from pygments.styles import get_style_by_name
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit import print_formatted_text, HTML
from typing import Optional
from vertexai.preview.generative_models import Content, Part
from pathlib import Path


# files

def fileNamesWithoutExtension(dir, ext):
    # Note: pathlib.Path(file).stem does not work with file name containg more than one dot, e.g. "*.db.sqlite"
    files = glob.glob(os.path.join(dir, "*.{0}".format(ext)))
    return sorted([file[len(dir)+1:-(len(ext)+1)] for file in files if os.path.isfile(file)])

def getLocalStorage():
    # config.freeGeniusAIName
    if not hasattr(config, "freeGeniusAIName") or not config.freeGeniusAIName:
        config.freeGeniusAIName = "FreeGenius AI"

    # option 1: config.storagedirectory; user custom folder
    if not hasattr(config, "storagedirectory") or (config.storagedirectory and not os.path.isdir(config.storagedirectory)):
        config.storagedirectory = ""
    if config.storagedirectory:
        return config.storagedirectory
    # option 2: defaultStorageDir; located in user home directory
    defaultStorageDir = os.path.join(os.path.expanduser('~'), config.freeGeniusAIName.split()[0].lower())
    try:
        Path(defaultStorageDir).mkdir(parents=True, exist_ok=True)
    except:
        pass
    if os.path.isdir(defaultStorageDir):
        return defaultStorageDir
    # option 3: directory "files" in app directory; to be deleted on every upgrade
    else:
        return os.path.join(packageFolder, "files")

# call llm

def executeToolFunction(func_arguments: dict, function_name: str):
    def notifyDeveloper(func_name):
        if config.developer:
            #config.print(f"running function '{func_name}' ...")
            print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Running function</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{func_name}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
    if not function_name in config.toolFunctionMethods:
        if config.developer:
            config.print(f"Unexpected function: {function_name}")
            config.print(config.divider)
            print(func_arguments)
            config.print(config.divider)
        function_response = "[INVALID]"
    else:
        notifyDeveloper(function_name)
        function_response = config.toolFunctionMethods[function_name](func_arguments)
    return function_response

def toParameterSchema(schema) -> dict:
    """
    extract parameter schema from full schema
    """
    if "parameters" in schema:
        return schema["parameters"]
    return schema

def toGeminiMessages(messages: dict=[]) -> Optional[list]:
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

# python code

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
            showErrors()
    return False

def isValidPythodCode(code):
    try:
        codeObject = compile(code, '<string>', 'exec')
        return codeObject
    except:
        return None

def extractPythonCode(content):
    if code_only := re.search('```python\n(.+?)```', content, re.DOTALL):
        content = code_only.group(1)
    return content if isValidPythodCode(content) is not None else ""

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

def getPythonFunctionResponse(code):
    #return str(config.pythonFunctionResponse) if config.pythonFunctionResponse is not None and (type(config.pythonFunctionResponse) in (int, float, str, list, tuple, dict, set, bool) or str(type(config.pythonFunctionResponse)).startswith("<class 'numpy.")) and not ("os.system(" in code) else ""
    return "" if config.pythonFunctionResponse is None else str(config.pythonFunctionResponse)

def showRisk(risk):
    if not config.confirmExecution in ("always", "medium_risk_or_above", "high_risk_only", "none"):
        config.confirmExecution = "always"
    config.print(f"[risk level: {risk}]")

def confirmExecution(risk):
    if config.confirmExecution == "always" or (risk == "high" and config.confirmExecution == "high_risk_only") or (not risk == "low" and config.confirmExecution == "medium_risk_or_above"):
        return True
    else:
        return False

# embedding

def getEmbeddingFunction(embeddingModel=None):
    # import statement is placed here to make this file compatible on Android
    embeddingModel = embeddingModel if embeddingModel is not None else config.embeddingModel
    if embeddingModel in ("text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002"):
        return embedding_functions.OpenAIEmbeddingFunction(api_key=config.openaiApiKey, model_name=embeddingModel)
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embeddingModel) # support custom Sentence Transformer Embedding models by modifying config.embeddingModel

# chromadb

def get_or_create_collection(collection_name):
    collection = config.tool_store_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
        embedding_function=getEmbeddingFunction(),
    )
    return collection

def add_vector(collection, text, metadata):
    id = str(uuid.uuid4())
    collection.add(
        documents = [text],
        metadatas = [metadata],
        ids = [id]
    )

def query_vectors(collection, query, n=1):
    return collection.query(
        query_texts=[query],
        n_results = n,
    )

# display information

def getPygmentsStyle():
    theme = config.pygments_style if config.pygments_style else "stata-dark" if not config.terminalResourceLinkColor.startswith("ansibright") else "stata-light"
    return style_from_pygments_cls(get_style_by_name(theme))

def showErrors():
    trace = traceback.format_exc()
    print(trace if config.developer else "Error encountered!")
    return trace

# ip

def get_wan_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        data = response.json()
        return data['ip']
    except:
        return ""

def get_local_ip():
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            for address in addresses[netifaces.AF_INET]:
                ip = address['addr']
                if ip != '127.0.0.1':
                    return ip

# time

def getDayOfWeek():
    if config.isTermux:
        return ""
    else:
        now = pendulum.now() 
        return now.format('dddd')

# device information

def getDeviceInfo(includeIp=False):
    g = geocoder.ip('me')
    if hasattr(config, "thisPlatform"):
        thisPlatform = config.thisPlatform
    else:
        thisPlatform = platform.system()
        if thisPlatform == "Darwin":
            thisPlatform = "macOS"
    if config.includeIpInDeviceInfoTemp or includeIp or (config.includeIpInDeviceInfo and config.includeIpInDeviceInfoTemp):
        wan_ip = get_wan_ip()
        local_ip = get_local_ip()
        ipInfo = f'''Wan ip: {wan_ip}
Local ip: {local_ip}
'''
    else:
        ipInfo = ""
    if config.isTermux:
        dayOfWeek = ""
    else:
        dayOfWeek = getDayOfWeek()
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