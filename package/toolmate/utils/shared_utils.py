from toolmate import config
from toolmate.utils.terminal_mode_dialogs import TerminalModeDialogs
import sys, os, html, geocoder, platform, socket, geocoder, datetime, requests, getpass, pkg_resources, webbrowser, unicodedata
import traceback, uuid, re, textwrap, signal, wcwidth, shutil, threading, time, subprocess, json, base64, html2text, pydoc, codecs, psutil
from packaging import version
import importlib.resources
import pygments
from pygments.lexers.python import PythonLexer
from pygments.styles import get_style_by_name
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit import prompt
from typing import Optional, Any
from pathlib import Path
from PIL import Image
from bs4 import BeautifulSoup
from urllib.parse import quote
from typing import Union
from groq import Groq
from ollama import Client
import speech_recognition as sr
import zipfile
from openai import OpenAI
import tiktoken
if not config.isTermux:
    from llama_cpp import Llama
    from vertexai.generative_models import Content, Part
    from tavily import TavilyClient
    import chromadb, pendulum
    from chromadb.utils.embedding_functions import OllamaEmbeddingFunction, OpenAIEmbeddingFunction, SentenceTransformerEmbeddingFunction
    from chromadb.config import Settings
    from langchain_ollama import OllamaEmbeddings
    from langchain_openai import OpenAIEmbeddings
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_unstructured import UnstructuredLoader
    from autogen.retrieve_utils import TEXT_FORMATS
    from huggingface_hub import hf_hub_download
    import vosk
    import sounddevice, soundfile # it is important to import sounddevice on Linux, to resolve ALSA error display


# voice typing

def playAudio(audioFile):
    if config.isTermux and config.terminalEnableTermuxAPI:
        os.system(f'''termux-media-player play "{audioFile}"''')
    else:
        sounddevice.play(*soundfile.read(audioFile)) 
        sounddevice.wait()

def voiceTyping():
    # reference: https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py
    # import sounddevice to solve alsa error display: https://github.com/Uberi/speech_recognition/issues/182#issuecomment-1426939447
    r = sr.Recognizer()
    with sr.Microphone() as source:
        if config.voiceTypingNotification:
            playAudio(os.path.join(config.toolMateAIFolder, "audio", "notification1_mild.mp3"))
        #run_in_terminal(lambda: print2("Listensing to your voice ..."))
        if config.voiceTypingAdjustAmbientNoise:
            r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    if config.voiceTypingNotification:
        playAudio(os.path.join(config.toolMateAIFolder, "audio", "notification2_mild.mp3"))
    #run_in_terminal(lambda: print2("Processing to your voice ..."))
    if config.voiceTypingPlatform == "google":
        # recognize speech using Google Speech Recognition
        try:
            # check google.recognize_legacy in SpeechRecognition package
            # check available languages at: https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
            # config.voiceTypingLanguage should be code list in column BCP-47 at https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
            return r.recognize_google(audio, language=config.voiceTypingLanguage)
        except sr.UnknownValueError:
            #return "[Speech unrecognized!]"
            return ""
        except sr.RequestError as e:
            return "[Error: {0}]".format(e)
    elif config.voiceTypingPlatform == "googlecloud" and os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Speech-to-Text" in config.enabledGoogleAPIs:
        # recognize speech using Google Cloud Speech
        try:
            # check availabl languages at: https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
            # config.voiceTypingLanguage should be code list in column BCP-47 at https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
            return r.recognize_google_cloud(audio, language=config.voiceTypingLanguage, credentials_json=config.google_cloud_credentials)
        except sr.UnknownValueError:
            #return "[Speech unrecognized!]"
            return ""
        except sr.RequestError as e:
            return "[Error: {0}]".format(e)
    elif config.voiceTypingPlatform == "whisper":
        # recognize speech using whisper
        try:
            # check availabl languages at: https://github.com/openai/whisper/blob/main/whisper/tokenizer.py
            # config.voiceTypingLanguage should be uncapitalized full language name like "english" or "chinese"
            return r.recognize_whisper(audio, model=config.voiceTypingWhisperEnglishModel if config.voiceTypingLanguage == "english" else "large", language=config.voiceTypingLanguage)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            return "[Error]"
    elif config.voiceTypingPlatform == "whispercpp":
        #from speech_recognition.audio import AudioData
        #assert isinstance(audio, AudioData), "Data must be audio data"
        wav_bytes_data = audio.get_wav_data(
            convert_rate=16000,  # audio samples must be 8kHz or 16 kHz
            convert_width=2  # audio samples should be 16-bit
        )
        wav_file = os.path.join(config.toolMateAIFolder, "temp", "voice.wav")
        with open(wav_file, "wb") as fileObj:
            fileObj.write(wav_bytes_data)
        # Example of cli: ./main -np -nt -l auto -t 12 -m ggml-large-v3-q5_0.bin -f ~/Desktop/voice.wav
        # *.bin model files available at: https://huggingface.co/ggerganov/whisper.cpp/tree/main
        if not os.path.isfile(config.whispercpp_main) or not os.path.isfile(config.whispercpp_model):
            return "[Error]"
        cli = f'''"{config.whispercpp_main}" -np -nt -l {'en' if config.voiceTypingLanguage.lower() in ('english', 'en') else 'auto'} -t {getCpuThreads()} -m "{config.whispercpp_model}" -f "{wav_file}" {config.whispercpp_additional_options}'''
        process = subprocess.Popen(cli.rstrip(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return "[Error]" if stderr and not stdout else stdout.decode("utf-8").strip()
    elif config.voiceTypingPlatform == "vosk" and not config.isTermux:
        # disable log
        vosk.SetLogLevel(-1)
        # Load the Vosk model
        model = vosk.Model(model_name=config.voskModel)
        # Initialize the recognizer with the model
        recognizer = vosk.KaldiRecognizer(model, 16000)
        recognizer.AcceptWaveform(audio.get_raw_data(convert_rate=16000, convert_width=2))
        # Get the final recognized result
        try:
            result = json.loads(recognizer.FinalResult())["text"]
            #print(result)
            return result
        except:
            return "[Error]"

# transformers

def classify(user_input, candidate_labels):
    from transformers import pipeline
    classifier = pipeline(task="zero-shot-classification", model=config.zero_shot_classification_model)
    response = classifier(
        user_input,
        candidate_labels=candidate_labels,
    )
    labels = response["labels"]
    return labels[0]

def isToolRequired(user_input) -> bool:
    tool = True
    print2("```screening")
    # check the kind of input
    kind = classify(user_input, config.labels_kind)
    print3(f"Kind: {kind}")
    if kind in config.labels_kind_chat_only_options:
        tool = False
    elif kind in config.labels_kind_information_options:
        # check the nature of the requested information
        information = classify(user_input, config.labels_information)
        print3(f"Information: {information}")
        if information in config.labels_information_chat_only_options:
            tool = False
    else:
        # check the nature of the requested response
        action = classify(user_input, config.labels_action)
        print3(f"Action: {action}")
        if action in config.labels_action_chat_only_options:
            tool = False
    print3(f"""Comment: Tool may {"" if tool else "not "}be required.""")
    print2("```")
    return tool

# guidance

def screening(lm, user_input) -> bool:
    from guidance import select

    tool = False

    print2("```screening")
    thought = "Question: Is the given request formulated like a greeting, a question, a command, a statement, an issue, a description?"
    print3(thought)
    lm += f"""<|im_start|>user
Please answer my questions with regards to the following request:
<request>{user_input}</request>
<|im_end|>
<|im_start|>assistant
Certainly! Please provide me with the questions.
<|im_end|>
<|im_start|>user
{thought}
Answer: The given request is formulated like {select(["a question", "a command", "a statement", "an issue", "a description"], name="question")}.
<|im_end|>
"""
    question = lm.get("question")
    print3(f"""Answer: The given request is formulated like {question}.""")
    if question in ("a greeting", "a question", "an issue", "a description"):
        thought = "Question: What is the request about?"
        print3(thought)
        lm += f"""<|im_start|>assistant
{thought}
<|im_end|>
<|im_start|>user
Answer: The request is about {select(["greeting", "common knowledge", "math", "published content", "trained knowledge", "historical records", "programming knowledge", "religious knowledge", "insights obtainable from literature", "textbook content", "evolving data", "recent updates", "latest information", "current time", "current weather", "up-to-date news", "information specific to your device", "information unknown to me"], name="information")}.
<|im_end|>
"""
        information = lm.get("information")
        print3(f"""Answer: The request is about {information}.""")
        if information in ("evolving data", "recent updates", "latest information", "current time", "current weather", "up-to-date news", "information specific to your device", "information unknown to me"):
            tool = True
    else:
        thought = "Question: Does the given request ask for generating a text-response or carrying out a task on your device?"
        print3(thought)
        lm += f"""<|im_start|>assistant
{thought}
<|im_end|>
<|im_start|>user
Answer: The given request asks for {select(["greeting", "calculation", "translation", "writing a text-response", "carrying out a task on your device"], name="action")}.
<|im_end|>
"""
        action = lm.get("action")
        print3(f"""Answer: The given request asks for {action}.""")
        if action in ("carrying out a task on your device",):
            tool = True

    print3(f"""Comment: Tool may {"" if tool else "not "}be required.""")
    print2("```")

    return tool

def outputStructuredData(lm, schema: dict, json_output: bool=False, messages: list = [], use_system_message: bool=True, request: str="", temperature: Optional[float]=None, max_tokens: Optional[int]=None, **kwargs) -> Union[dict, str]:
    from guidance import select, gen

    properties = toParameterSchema(schema)["properties"]
    request = f", particularly related to the following request:\n{request}" if request else "."
    lm += toChatml(messages, use_system_message=use_system_message).rstrip()
    lm += f"""<|im_start|>assistant.
I am answering your questions based on the content in our conversation given above{request}
<|im_end|>
"""
    for key, value in properties.items():
        description = value["description"].replace("\n", " ")
        if "enum" in value:
            options = value["enum"]
            options_str = "', '".join(value["enum"])
            description += f" Its value must be one of these options: '{options_str}'"
        lm += f'''<|im_start|>user
Question: {description}
<|im_end|>
<|im_start|>assistant
Answer: {select(options, name=key) if "enum" in value else gen(name=key, stop="<")}
<|im_end|>
'''

    response = {}
    for i in properties:
        response[i] = codecs.decode(lm.get(i, "").rstrip(), "unicode_escape")
    return json.dumps(response) if json_output else response

def select_tool(lm, user_input):
    from guidance import select, gen

    tool_names = list(config.toolFunctionSchemas.keys())
    tools = {i:config.toolFunctionSchemas[i]["description"] for i in config.toolFunctionSchemas}

    lm += f"""<|im_start|>user
Select an action to resolve the request as best you can. You have access only to the following tools:

{tools}

Use the following format:

Request: the input request you must resolve
Thought: you should always think about what to do
Action: the action to take, has to be one of {tool_names}<|im_end|>
<|im_start|>assistant
Request: {user_input}
Thought: {gen(stop=".")}.
Action: {select(tool_names, name="tool")}"""
    
    return lm.get("tool")

# llm

def getOpenweathermapApi_key():
    '''
    support multiple open weather map api keys
    '''
    if config.openweathermapApi:
        if isinstance(config.openweathermapApi, str):
            return config.openweathermapApi
        elif isinstance(config.openweathermapApi, list):
            if len(config.openweathermapApi) > 1:
                # rotate multiple api keys
                config.openweathermapApi = config.openweathermapApi[1:] + [config.openweathermapApi[0]]
            return config.openweathermapApi[0]
        else:
            return ""
    else:
        return ""

def getElevenlabsApi_key():
    '''
    support multiple eleven api keys
    User can manually edit config to change the value of config.tavilyApi_key to a list of multiple api keys instead of a string of a single api key
    '''
    if config.elevenlabsApi:
        if isinstance(config.elevenlabsApi, str):
            return config.elevenlabsApi
        elif isinstance(config.elevenlabsApi, list):
            if len(config.elevenlabsApi) > 1:
                # rotate multiple api keys
                config.elevenlabsApi = config.elevenlabsApi[1:] + [config.elevenlabsApi[0]]
            return config.elevenlabsApi[0]
        else:
            return ""
    else:
        return ""

def getTavilyApi_key():
    '''
    support multiple tavily api keys
    User can manually edit config to change the value of config.tavilyApi_key to a list of multiple api keys instead of a string of a single api key
    '''
    if config.tavilyApi_key:
        if isinstance(config.tavilyApi_key, str):
            return config.tavilyApi_key
        elif isinstance(config.tavilyApi_key, list):
            if len(config.tavilyApi_key) > 1:
                # rotate multiple api keys
                config.tavilyApi_key = config.tavilyApi_key[1:] + [config.tavilyApi_key[0]]
            return config.tavilyApi_key[0]
        else:
            return ""
    else:
        return ""

def getTavilyClient():
    return TavilyClient(api_key=getTavilyApi_key())

def getGroqApi_key():
    '''
    support multiple grop api keys
    User can manually edit config to change the value of config.groqApi_key to a list of multiple api keys instead of a string of a single api key
    '''
    if config.groqApi_key:
        if isinstance(config.groqApi_key, str):
            return config.groqApi_key
        elif isinstance(config.groqApi_key, list):
            if len(config.groqApi_key) > 1:
                # rotate multiple api keys
                config.groqApi_key = config.groqApi_key[1:] + [config.groqApi_key[0]]
            return config.groqApi_key[0]
        else:
            return ""
    else:
        return ""

def getGroqClient():
    return Groq(api_key=getGroqApi_key())

def downloadStableDiffusionFiles():
    # llm directory
    llm_directory = os.path.join(config.localStorage, "LLMs", "stable_diffusion")
    Path(llm_directory).mkdir(parents=True, exist_ok=True)
    filename = "v1-5-pruned-emaonly.safetensors"
    stableDiffusion_model_path = os.path.join(llm_directory, filename)
    if not config.stableDiffusion_model_path or not os.path.isfile(config.stableDiffusion_model_path):
        config.stableDiffusion_model_path = stableDiffusion_model_path

    if not os.path.isfile(config.stableDiffusion_model_path):
        print2("Downloading stable-diffusion model ...")
        hf_hub_download(
            repo_id="Syimbiote/v1-5-pruned-emaonly",
            filename=filename,
            local_dir=llm_directory,
            #local_dir_use_symlinks=False,
        )
        stableDiffusion_model_path = os.path.join(llm_directory, filename)
        if os.path.isfile(stableDiffusion_model_path):
            config.stableDiffusion_model_path = stableDiffusion_model_path
            config.saveConfig()

    lora_model_dir = os.path.join(llm_directory, "lora")
    Path(lora_model_dir).mkdir(parents=True, exist_ok=True)
    filename = "pytorch_lora_weights.safetensors"
    lora_file = os.path.join(lora_model_dir, filename)
    if not os.path.isfile(lora_file):
        print2("Downloading stable-diffusion LCM-LoRA ...")
        hf_hub_download(
            repo_id="latent-consistency/lcm-lora-sdv1-5",
            filename=filename,
            local_dir=lora_model_dir,
            #local_dir_use_symlinks=False,
        )

def startAutogenstudioServer():
    try:
        if not hasattr(config, "autogenstudioServer") or config.autogenstudioServer is None:
            config.autogenstudioServer = None
            print2("Running Autogen Studio server ...")
            cmd = f"""{sys.executable} -m autogenstudio.cli ui --host 127.0.0.1 --port {config.autogenstudio_server_port}"""
            config.autogenstudioServer = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
            while not isServerAlive("127.0.0.1", config.autogenstudio_server_port):
                # wait til the server is up
                ...
    except:
        print2(f'''Failed to run Autogen Studio server at "localhost:{config.autogenstudio_server_port}"!''')
        config.autogenstudioServer = None
    webbrowser.open(f"http://127.0.0.1:{config.autogenstudio_server_port}")

def stopAutogenstudioServer():
    if hasattr(config, "autogenstudioServer") and config.autogenstudioServer is not None:
        if isServerAlive("127.0.0.1", config.autogenstudio_server_port):
            print2("Stopping Autogen Studio server ...")
            os.killpg(os.getpgid(config.autogenstudioServer.pid), signal.SIGTERM)
        config.autogenstudioServer = None

def getOllamaServerClient(server="main"):
    return Client(host=f"http://{config.ollamaChatServer_ip if server=='chat' else config.ollamaToolServer_ip}:{config.ollamaChatServer_port if server=='chat' else config.ollamaToolServer_port}")

def loadLlamacppChatModel():
    cpuThreads = getCpuThreads()
    return Llama(
        model_path=config.llamacppChatModel_model_path,
        chat_format="chatml",
        n_ctx=config.llamacppChatModel_n_ctx,
        n_batch=config.llamacppChatModel_n_batch,
        verbose=config.llamacppChatModel_verbose,
        n_threads=cpuThreads,
        n_threads_batch=cpuThreads,
        n_gpu_layers=config.llamacppChatModel_n_gpu_layers,
        **config.llamacppChatModel_additional_model_options,
    )

def getLlamacppServerClient(server="tool"):
    def getNewClient():
        ips = {
            "tool": config.customToolServer_ip,
            "chat": config.customChatServer_ip,
            "vision": config.customVisionServer_ip,
        }
        ports = {
            "tool": config.customToolServer_port,
            "chat": config.customChatServer_port,
            "vision": config.customVisionServer_port,
        }
        return OpenAI(
            base_url=f"http://{ips[server]}:{ports[server]}/v1",
            api_key = "toolmate",
        )
    if server == "tool":
        if (not hasattr(config, "llamacppserver_tool_client")) or (hasattr(config, "llamacppserver_tool_client") and config.llamacppserver_tool_client is None):
            config.llamacppserver_tool_client = getNewClient()
        return config.llamacppserver_tool_client
    elif server == "chat":
        if (not hasattr(config, "llamacppserver_chat_client")) or (hasattr(config, "llamacppserver_chat_client") and config.llamacppserver_chat_client is None):
            config.llamacppserver_chat_client = getNewClient()
        return config.llamacppserver_chat_client
    else:
        return getNewClient()

def startLlamacppServer():
    try:
        if not hasattr(config, "llamacppServer") or config.llamacppServer is None:
            config.llamacppServer = None
            print2("Running llama.cpp tool server ...")
            cpuThreads = getCpuThreads()
            cmd = f"""{sys.executable} -m llama_cpp.server --port {config.llamacppToolModel_server_port} --model "{config.llamacppToolModel_model_path}" --verbose {config.llamacppToolModel_verbose} --chat_format chatml --n_ctx {config.llamacppToolModel_n_ctx} --n_gpu_layers {config.llamacppToolModel_n_gpu_layers} --n_batch {config.llamacppToolModel_n_batch} --n_threads {cpuThreads} --n_threads_batch {cpuThreads} {config.llamacppToolModel_additional_server_options}"""
            config.llamacppServer = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
            while not isServerAlive("127.0.0.1", config.llamacppToolModel_server_port):
                # wait til the server is up
                ...
    except:
        print2(f'''Failed to run llama.cpp server at "localhost:{config.llamacppToolModel_server_port}"!''')
        config.llamacppServer = None
    webbrowser.open(f"http://127.0.0.1:{config.llamacppToolModel_server_port}/docs")

def stopLlamacppServer():
    if hasattr(config, "llamacppServer") and config.llamacppServer is not None:
        if isServerAlive("127.0.0.1", config.llamacppToolModel_server_port):
            print2("Stopping llama.cpp tool server ...")
            os.killpg(os.getpgid(config.llamacppServer.pid), signal.SIGTERM)
        config.llamacppServer = None

def startLlamacppChatServer():
    try:
        if not hasattr(config, "llamacppChatServer") or config.llamacppChatServer is None:
            config.llamacppChatServer = None
            print2("Running llama.cpp chat server ...")
            cpuThreads = getCpuThreads()
            cmd = f"""{sys.executable} -m llama_cpp.server --port {config.llamacppChatModel_server_port} --model "{config.llamacppChatModel_model_path}" --verbose {config.llamacppChatModel_verbose} --chat_format chatml --n_ctx {config.llamacppChatModel_n_ctx} --n_gpu_layers {config.llamacppChatModel_n_gpu_layers} --n_batch {config.llamacppChatModel_n_batch} --n_threads {cpuThreads} --n_threads_batch {cpuThreads} {config.llamacppChatModel_additional_server_options}"""
            config.llamacppChatServer = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
            while not isServerAlive("127.0.0.1", config.llamacppChatModel_server_port):
                # wait til the server is up
                ...
    except:
        print2(f'''Failed to run llama.cpp server at "localhost:{config.llamacppChatModel_server_port}"!''')
        config.llamacppChatServer = None
    webbrowser.open(f"http://127.0.0.1:{config.llamacppChatModel_server_port}/docs")

def stopLlamacppChatServer():
    if hasattr(config, "llamacppChatServer") and config.llamacppChatServer is not None:
        if isServerAlive("127.0.0.1", config.llamacppChatModel_server_port):
            print2("Stopping llama.cpp chat server ...")
            os.killpg(os.getpgid(config.llamacppChatServer.pid), signal.SIGTERM)
        config.llamacppChatServer = None

def startLlamacppVisionServer():
    try:
        if not hasattr(config, "llamacppVisionServer") or config.llamacppVisionServer is None:
            if os.path.isfile(config.llamacppVisionModel_model_path) and os.path.isfile(config.llamacppVisionModel_clip_model_path):
                config.llamacppVisionServer = None
                print2("Running llama.cpp vision server ...")
                cpuThreads = getCpuThreads()
                cmd = f"""{sys.executable} -m llama_cpp.server --port {config.llamacppVisionModel_server_port} --model "{config.llamacppVisionModel_model_path}" --clip_model_path {config.llamacppVisionModel_clip_model_path} --verbose {config.llamacppVisionModel_verbose} --chat_format llava-1-5 --n_ctx {config.llamacppVisionModel_n_ctx} --n_gpu_layers {config.llamacppVisionModel_n_gpu_layers} --n_batch {config.llamacppVisionModel_n_batch} --n_threads {cpuThreads} --n_threads_batch {cpuThreads} {config.llamacppVisionModel_additional_server_options}"""
                config.llamacppVisionServer = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
                while not isServerAlive("127.0.0.1", config.llamacppVisionModel_server_port):
                    # wait til the server is up
                    ...
            else:
                print1("Error! Clip model or vision model is missing!")
    except:
        print2(f'''Failed to run llama.cpp server at "localhost:{config.llamacppVisionModel_server_port}"!''')
        config.llamacppVisionServer = None
    webbrowser.open(f"http://127.0.0.1:{config.llamacppVisionModel_server_port}/docs")

def stopLlamacppVisionServer():
    if hasattr(config, "llamacppVisionServer") and config.llamacppVisionServer is not None:
        if isServerAlive("127.0.0.1", config.llamacppVisionModel_server_port):
            print2("Stopping llama.cpp vision server ...")
            os.killpg(os.getpgid(config.llamacppVisionServer.pid), signal.SIGTERM)
        config.llamacppVisionServer = None

def getOllamaModelDir():
    # read https://github.com/ollama/ollama/blob/main/docs/faq.md#where-are-models-stored
    OLLAMA_MODELS = os.getenv("OLLAMA_MODELS")
    if not OLLAMA_MODELS or (OLLAMA_MODELS and not os.path.isdir(OLLAMA_MODELS)):
        os.environ['OLLAMA_MODELS'] = ""

    if os.environ['OLLAMA_MODELS']:
        return os.environ['OLLAMA_MODELS']
    elif config.thisPlatform == "Windows":
        modelDir = os.path.expanduser(r"~\.ollama\models")
    elif config.thisPlatform == "macOS":
        modelDir = os.path.expanduser("~/.ollama/models")
    elif config.thisPlatform == "Linux":
        modelDir = "/usr/share/ollama/.ollama/models"
    
    if os.path.isdir(modelDir):
        return modelDir
    return ""

def getDownloadedOllamaModels() -> dict:
    models = {}
    if modelDir := getOllamaModelDir():
        library = os.path.join(modelDir, "manifests", "registry.ollama.ai", "library")
        if os.path.isdir(library):
            for d in os.listdir(library):
                model_dir = os.path.join(library, d)
                if os.path.isdir(model_dir):
                    for f in os.listdir(model_dir):
                        manifest = os.path.join(model_dir, f)
                        if os.path.isfile(manifest):
                            try:
                                with open(manifest, "r", encoding="utf-8") as fileObj:
                                    content = fileObj.read()
                                model_file = re.search('''vnd.ollama.image.model","digest":"(.*?)"''', content)
                                if model_file:
                                    model_file = os.path.join(modelDir, "blobs", model_file.group(1))
                                    if not os.path.isfile(model_file):
                                        model_file = model_file.replace(":", "-")
                                    if os.path.isfile(model_file):
                                        model_tag = f"{d}:{f}"
                                        models[model_tag] = model_file
                                        if f == "latest":
                                            models[d] = model_file
                            except:
                                pass
    return models

def exportOllamaModels(selection: list=[]) -> None:
    llm_directory = os.path.join(config.localStorage, "LLMs", "gguf")
    Path(llm_directory).mkdir(parents=True, exist_ok=True)
    models = getDownloadedOllamaModels()
    for model, originalpath in models.items():
        filename = model.replace(":", "_")
        exportpath = os.path.join(llm_directory, f"{filename}.gguf")
        if not os.path.isfile(exportpath) and not model.endswith(":latest") and ((not selection) or (model in selection)):
            print3(f"Model: {model}")
            shutil.copy2(originalpath, exportpath)
            print3(f"Exported: {exportpath}")

def getDownloadedGgufModels() -> dict:
    llm_directory = os.path.join(config.localStorage, "LLMs", "gguf")
    Path(llm_directory).mkdir(parents=True, exist_ok=True)
    models = {}
    for f in getFilenamesWithoutExtension(llm_directory, "gguf"):
        models[f] = os.path.join(llm_directory, f"{f}.gguf")
    return models

# text

def plainTextToUrl(text):
    # https://wiki.python.org/moin/EscapingHtml
    text = html.escape(text)
    searchReplace = (
        (" ", "%20"),
        ("\n", "%0D%0A"),
    )
    for search, replace in searchReplace:
        text = text.replace(search, replace)
    return text

def removeDuplicatedListItems(lst):
    # remove duplicates and matain order
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

def displayLoadedMessages(messages):
    # display loaded messages
    for index, i in enumerate(messages):
        role = i.get("role", "")
        content = i.get("content", "")
        if role and role in ("user", "assistant") and content:
            if role == "user":
                print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor1}>>>> </{config.terminalPromptIndicatorColor1}><{config.terminalCommandEntryColor1}>{content}</{config.terminalCommandEntryColor1}>"))
            else:
                print1(content)
            if role == 'assistant' and not index == len(messages) - 2:
                print("")
    print("")

def refinePath(docs_path):
    docs_path = docs_path.strip()
    docs_path = re.sub("^'(.*?)'$", r"\1", docs_path)
    if "\\ " in docs_path or r"\(" in docs_path:
        docs_path = docs_path.replace("\\ ", " ")
        docs_path = docs_path.replace(r"\(", "(")
    return os.path.expanduser(docs_path)

def readTextFile(textFile: str) -> str:
    with open(textFile, 'r', encoding='utf8') as fileObj:
        content = fileObj.read()
    return content if content else ""

def writeTextFile(textFile: str, textContent: str) -> None:
    with open(textFile, "w", encoding="utf-8") as fileObj:
        fileObj.write(textContent)

def is_CJK(text):
    for char in text:
        if 'CJK' in unicodedata.name(char):
            return True
    return False

def getAssistantPreviousResponse():
    index = 0
    content = ""
    for order, item in enumerate(reversed(config.currentMessages)):
        if item.get("role", "") == "assistant":
            content = item.get("content", "").strip()
            if content:
                index = (order + 1)*-1
                break
    if not content:
        print2("Previous response not found! Action cancelled!")
    return (content, index)

def getUserPreviousRequest():
    index = 0
    content = ""
    for order, item in enumerate(reversed(config.currentMessages)):
        if item.get("role", "") == "user":
            content = item.get("content", "").strip()
            if content:
                index = (order + 1)*-1
                break
    if not content:
        print2("Previous request not found! Action cancelled!")
    return (content, index)

# Function to convert HTML to Markdown
def convert_html_to_markdown(html_string):
    # Create an instance of the HTML2Text converter
    converter = html2text.HTML2Text()
    # Convert the HTML string to Markdown
    markdown_string = converter.handle(html_string)
    # Return the Markdown string
    return markdown_string

# system command

def checkPath():
    currentPath = os.getenv('PATH')
    shimsPath = os.path.expanduser("~/.pyenv/shims/")
    envPath = os.path.dirname(sys.executable)
    if os.path.isdir(shimsPath) and not shimsPath in currentPath:
        os.environ["PATH"] = f"{shimsPath}:{os.environ['PATH']}"
    if os.path.isdir(envPath) and not envPath in currentPath:
        os.environ["PATH"] = f"{envPath}:{os.environ['PATH']}"

def getCpuThreads():
    if config.cpu_threads and isinstance(config.cpu_threads, int):
        return config.cpu_threads
    physical_cpu_core = psutil.cpu_count(logical=False)
    return physical_cpu_core if physical_cpu_core and physical_cpu_core > 1 else 1

def getCliOutput(cli):
    try:
        process = subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, *_ = process.communicate()
        return stdout.decode("utf-8")
    except:
        return ""

def textTool(tool="", content=""):
    command = re.sub(" .*?$", "", tool.strip())
    if command and isCommandInstalled(command):
        pydoc.pipepager(content, cmd=tool)
        if isCommandInstalled("pkill"):
            os.system(f"pkill {command}")
    return ""

def getHideOutputSuffix():
    return f" > {'nul' if config.thisPlatform == 'Windows' else '/dev/null'} 2>&1"

def getAlias(alias):
    findAlias = f"/bin/bash -ic 'alias {alias}'"
    aliasOutput, *_ = subprocess.Popen(findAlias, shell=True, stdout=subprocess.PIPE, text=True).communicate()
    return re.sub("^.*?=.(.*?).$", r"\1", aliasOutput.strip())

def runToolMateCommand(command):
    def createShortcutFile(filePath, content):
        with open(filePath, "w", encoding="utf-8") as fileObj:
            fileObj.write(content)

    iconFile = os.path.join(config.toolMateAIFolder, "icons", "ai.png")

    shortcut_dir = os.path.join(config.toolMateAIFolder, "shortcuts")
    Path(shortcut_dir).mkdir(parents=True, exist_ok=True)

    args = command.split()
    firstArg = args[0]
    fullCommand = shutil.which(firstArg)
    if not fullCommand and config.thisPlatform in ("macOS", "Linux"):
        fullCommand = getAlias(firstArg)
    if not fullCommand:
        return
    fullCommand += f" {' '.join(args[1:])}" if args[1:] else ""

    if config.thisPlatform == "Windows":
        envCommandPath = os.path.join(os.path.dirname(sys.executable), f"{firstArg}.exe")
        opencommand = ""
        filePath = os.path.join(shortcut_dir, f"{command}.bat")
        if not os.path.isfile(filePath):
            # use 'powershell.exe -NoExit -Command' or 'cmd.exe /c' to launch console
            content = f'''powershell.exe -NoExit -Command "{envCommandPath if os.path.isfile(envCommandPath) else fullCommand}"'''
            createShortcutFile(filePath, content)
        os.startfile(f'''"{filePath}"''')
    elif config.thisPlatform == "macOS":
        opencommand = "open"
        filePath = os.path.join(shortcut_dir, f"{command}.command")
        if not os.path.isfile(filePath):
            content = f"""#!/bin/bash
{fullCommand}"""
            createShortcutFile(filePath, content)
            os.chmod(filePath, 0o755)
    elif config.thisPlatform == "Linux":
        opencommand = ""
        for i in ("gio launch", "dex", "exo-open", "xdg-open"):
            # Remarks:
            # 'exo-open' comes with 'exo-utils'
            # 'gio' comes with 'glib2'
            if shutil.which(i.split(" ", 1)[0]):
                opencommand = i
                break
        filePath = os.path.join(shortcut_dir, f"{command}.desktop")
        if not os.path.isfile(filePath):
            content = f"""[Desktop Entry]
Version=1.0
Type=Application
Terminal=true
Path={config.toolMateAIFolder}
Exec={fullCommand}
Icon={iconFile}
Name={command}"""
            createShortcutFile(filePath, content)
    if opencommand:
        os.system(f'''{opencommand} "{filePath}"''')

# tool selection

def selectTool(recommended_tools) -> Optional[str]:
    if config.auto_tool_selection:
        # auto
        return recommended_tools[0]
    else:
        # manual
        tool_options = []
        tool_descriptions = []
        for i in recommended_tools:
            tool_options.append(i)
            tool_descriptions.append(i.replace("_", " "))
        if not "chat" in recommended_tools:
            tool_options.append("chat")
            tool_descriptions.append("chat only")
        tool_options.append("xxxmorexxx")
        tool_descriptions.append("more ...")
        stopSpinning()
        tool = TerminalModeDialogs(None).getValidOptions(
            title="Tool Selection",
            text="Select a tool:",
            options=tool_options,
            descriptions=tool_descriptions,
            default=tool_options[0],
        )
        if tool:
            return selectEnabledTool() if tool == "xxxmorexxx" else tool
    return None

def selectEnabledTool() -> Optional[str]:
    tool_options = []
    tool_descriptions = []
    for name in config.allEnabledTools:
        tool_options.append(name)
        tool_descriptions.append(name.replace("_", " "))
    stopSpinning()
    tool = TerminalModeDialogs(None).getValidOptions(
        title="Tool Selection",
        text="Select a tool:",
        options=tool_options,
        descriptions=tool_descriptions,
        default=tool_options[0],
    )
    return tool if tool else None

# connectivity

def isServerAlive(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)  # Timeout in case of server not responding
    try:
        sock.connect((ip, port))
        sock.close()
        return True
    except socket.error:
        return False

def isUrlAlive(url):
    #print(urllib.request.urlopen("https://letmedoit.ai").getcode())
    try:
        request = requests.get(url, timeout=5)
    except:
        return False
    return True if request.status_code == 200 else False

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

# files

import glob
import os

def find_last_added_file(folder_path, ext=".mp3"):
    """
    Finds the filename of the last added .mp3 file in a folder.
    Args:
        folder_path: The path to the folder containing the MP3 files.
    Returns:
        The filename of the last added .mp3 file, or None if no such file is found.
    """
    files = glob.glob(os.path.join(folder_path, f'*{ext}'))
    if not files:
        return None

    # Sort files by creation time (oldest to newest)
    files.sort(key=os.path.getctime)
    return os.path.basename(files[-1])

def getFileSizeInMB(file_path):
    # Get the file size in bytes
    file_size = os.path.getsize(file_path)
    # Convert bytes to megabytes
    return file_size / (1024 * 1024)

def isExistingPath(docs_path):
    # handle document path dragged to the terminal
    docs_path = docs_path.strip()
    search_replace = (
        ("^'(.*?)'$", r"\1"),
        ('^(File|Folder): "(.*?)"$', r"\2"),
    )
    for search, replace in search_replace:
        docs_path = re.sub(search, replace, docs_path)
    if "\\ " in docs_path or r"\(" in docs_path:
        search_replace = (
            ("\\ ", " "),
            (r"\(", "("),
        )
        for search, replace in search_replace:
            docs_path = docs_path.replace(search, replace)
    return docs_path if os.path.exists(os.path.expanduser(docs_path)) else ""

def getUnstructuredFiles(dir_path: str) -> list:
    full_paths = []
    for dirpath, _, files in os.walk(dir_path):
        for filename in files:
            _, file_extension = os.path.splitext(filename)
            if file_extension[1:] in TEXT_FORMATS:
                filepath = os.path.join(dirpath, filename)
                full_paths.append(filepath)
    return full_paths

def getFilenamesWithoutExtension(dir, ext):
    # Note: pathlib.Path(file).stem does not work with file name containg more than one dot, e.g. "*.db.sqlite"
    #files = glob.glob(os.path.join(dir, "*.{0}".format(ext)))
    #return sorted([file[len(dir)+1:-(len(ext)+1)] for file in files if os.path.isfile(file)])
    return sorted([f[:-(len(ext)+1)] for f in os.listdir(dir) if f.lower().endswith(f".{ext}") and os.path.isfile(os.path.join(dir, f))])

def getLocalStorage():
    # migration
    old_storage = os.path.join(os.path.expanduser('~'), "freegenius")
    new_storage = os.path.join(os.path.expanduser('~'), "toolmate")
    if os.path.isdir(old_storage) and not os.path.isdir(new_storage):
        try:
            os.rename(old_storage, new_storage)
        except:
            pass
    # config.toolMateAIName
    if not hasattr(config, "toolMateAIName") or not config.toolMateAIName:
        config.toolMateAIName = "ToolMate AI"

    # option 1: config.storagedirectory; user custom folder
    if not hasattr(config, "storagedirectory") or (config.storagedirectory and not os.path.isdir(config.storagedirectory)):
        config.storagedirectory = ""
    if config.storagedirectory:
        return config.storagedirectory
    # option 2: defaultStorageDir; located in user home directory
    defaultStorageDir = os.path.join(os.path.expanduser('~'), config.toolMateAIName.split()[0].lower())
    try:
        Path(defaultStorageDir).mkdir(parents=True, exist_ok=True)
    except:
        pass
    if os.path.isdir(defaultStorageDir):
        return defaultStorageDir
    # option 3: directory "files" in app directory; to be deleted on every upgrade
    else:
        return os.path.join(config.toolMateAIFolder, "files")

# image

def encode_image(image_path, size_limit_in_MB=None):
    if size_limit_in_MB is not None and getFileSizeInMB(image_path) > size_limit_in_MB:
        return None
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    ext = os.path.splitext(os.path.basename(image_path))[1][1:]
    return f"data:image/{ext};base64,{base64_image}"

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

# call llm

def executeToolFunction(func_arguments: dict, function_name: str):
    def notifyDeveloper(func_name):
        if config.developer:
            #print1(f"running tool '{func_name}' ...")
            print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Running tool</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{func_name}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
    if not function_name in config.toolFunctionMethods:
        if config.developer:
            print1(f"Unexpected function: {function_name}")
            print1(config.divider)
            print(func_arguments)
            print1(config.divider)
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

def toChatml(messages: dict=[], use_system_message=True) -> str:
    messages_str = ""
    roles = {
        "user": "<|im_start|>user\n{content}\n<|im_end|>\n",
        "assistant": "<|im_start|>assistant\n{content}\n<|im_end|>\n",
    }
    if use_system_message:
        roles["system"] = "<|im_start|>system\n{content}\n<|im_end|>\n"
    for message in messages:
        role, content = message.get("role", ""), message.get("content", "")
        if role and role in roles and content:
            messages_str += roles[role].format(content=content)
    return messages_str.rstrip()

def useChatSystemMessage(messages: dict) -> dict:
    for i in messages:
        if i.get("role", "") == "system":
            if config.tempChatSystemMessage:
                i["content"] = config.tempChatSystemMessage
                config.tempChatSystemMessage = ""
            elif config.llmInterface == "ollama":
                i["content"] = config.systemMessage_ollama
            elif config.llmInterface == "groq":
                i["content"] = config.systemMessage_groq
            elif config.llmInterface == "llamacppserver":
                i["content"] = config.systemMessage_llamacppserver
            elif config.llmInterface == "llamacpp":
                i["content"] = config.systemMessage_llamacpp
            elif config.llmInterface == "gemini":
                i["content"] = config.systemMessage_gemini
            elif config.llmInterface == "chatgpt":
                i["content"] = config.systemMessage_chatgpt
            # assume only one system message in the message chain
            break
    return messages

def toGeminiMessages(messages: dict=[]) -> Optional[list]:
    systemMessage = ""
    lastUserMessage = ""
    if messages:
        history = []
        for i in messages:
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

def displayPythonCode(python_code):
    print1("```python")
    tokens = list(pygments.lex(python_code, lexer=PythonLexer()))
    print_formatted_text(PygmentsTokens(tokens), style=getPygmentsStyle())
    print1("```")

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
            print1("Failed to run '{0}'!".format(os.path.basename(script)))
            showErrors()
    return False

def isValidPythodCode(code):
    try:
        codeObject = compile(code, '<string>', 'exec')
        return codeObject
    except:
        return None

def extractPythonCode(content, keepInvalid=False):
    content = content.replace("<python>", "")
    content = content.replace("</python>", "")
    content = content.replace(r"<\/python>", "")
    content = re.sub("^python[ ]*\n", "", content).strip()
    content = re.sub(r"^[\d\D]*?```.*?\n", "", content, flags=re.M).strip()
    content = re.sub("\n```.*?$", "", content, flags=re.M).strip()
    if code_only := re.search('```python[ ]*\n(.+?)```', content, re.DOTALL):
        content = code_only.group(1).strip()
    elif code_only := re.search('```[ ]*\n(.+?)```', content, re.DOTALL):
        content = code_only.group(1).strip()
    content = re.sub("\n```[^\n]*?$", "", content, flags=re.M)
    content = re.sub("^<[^<>]*?>", "", content)
    content = re.sub("<[^<>]*?>$", "", content)
    return content if keepInvalid or isValidPythodCode(content) is not None else ""

def fineTunePythonCode(code):
    # dedent
    code = textwrap.dedent(code).rstrip()
    code = re.sub("^python[ ]*\n", "", code)
    # extract from code block, if any
    if code_only := re.search('```python\n(.+?)```', code, re.DOTALL):
        code = code_only.group(1).strip()
    # make sure it is run as main program
    if "\nif __name__ == '__main__':\n" in code:
        code, main = code.split("\nif __name__ == '__main__':\n", 1)
        code = code.strip()
        main = "\n" + textwrap.dedent(main)
    elif '\nif __name__ == "__main__":\n' in code:
        code, main = code.split('\nif __name__ == "__main__":\n', 1)
        code = code.strip()
        main = "\n" + textwrap.dedent(main)
    else:
        main = ""
    # capture print output
    config.pythonFunctionResponse = ""
    insert_string = "from toolmate import config\nconfig.pythonFunctionResponse = "
    code = re.sub("^!(.*?)$", r'import os\nos.system(""" \1 """)', code, flags=re.M)
    if "\n" in code:
        substrings = code.rsplit("\n", 1)
        lastLine = re.sub(r"print\((.*)\)", r"\1", substrings[-1])
        if lastLine.startswith(" "):
            lastLine = re.sub("^([ ]+?)([^ ].*?)$", r"\1config.pythonFunctionResponse = \2", lastLine)
            code = f"from toolmate import config\n{substrings[0]}\n{lastLine}"
        else:
            lastLine = f"{insert_string}{lastLine}"
            code = f"{substrings[0]}\n{lastLine}"
    else:
        code = f"{insert_string}{code}"
    return f"{code}{main}"

def getPythonFunctionResponse(code):
    #return str(config.pythonFunctionResponse) if config.pythonFunctionResponse is not None and (type(config.pythonFunctionResponse) in (int, float, str, list, tuple, dict, set, bool) or str(type(config.pythonFunctionResponse)).startswith("<class 'numpy.")) and not ("os.system(" in code) else ""
    return "" if config.pythonFunctionResponse is None else str(config.pythonFunctionResponse)

def showRisk(risk):
    if not config.confirmExecution in ("always", "medium_risk_or_above", "high_risk_only", "none"):
        config.confirmExecution = "always"
    print1(f"[risk level: {risk}]")

def confirmExecution(risk):
    if config.confirmExecution == "always" or (risk == "high" and config.confirmExecution == "high_risk_only") or (not risk == "low" and config.confirmExecution == "medium_risk_or_above"):
        return True
    else:
        return False

# spinning

def spinning_animation(stop_event):
    while not stop_event.is_set():
        for symbol in "|/-\\":
            print(symbol, end="\r")
            time.sleep(0.1)

def startSpinning():
    config.stop_event = threading.Event()
    config.spinner_thread = threading.Thread(target=spinning_animation, args=(config.stop_event,))
    config.spinner_thread.start()

def stopSpinning():
    try:
        config.stop_event.set()
        config.spinner_thread.join()
    except:
        pass

# display information

def wrapText(content, terminal_width=None):
    if terminal_width is None:
        terminal_width = shutil.get_terminal_size().columns
    return "\n".join([textwrap.fill(line, width=terminal_width) for line in content.split("\n")])

def transformText(text):
    for transformer in config.outputTransformers:
            text = transformer(text)
    return text

def print1(content):
    content = transformText(content)
    if config.wrapWords:
        # wrap words to fit terminal width
        terminal_width = shutil.get_terminal_size().columns
        print(wrapText(content, terminal_width))
        # remarks: 'fold' or 'fmt' does not work on Windows
        # pydoc.pipepager(f"{content}\n", cmd=f"fold -s -w {terminal_width}")
        # pydoc.pipepager(f"{content}\n", cmd=f"fmt -w {terminal_width}")
    else:
        print(content)

def print2(content):
    try:
        print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>{content}</{config.terminalPromptIndicatorColor2}>"))
    except:
        print(content)

def print3(content):
    try:
        splittedContent = content.split(": ", 1)
        if len(splittedContent) == 2:
            key, value = splittedContent
            print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>{key}:</{config.terminalPromptIndicatorColor2}> {value}"))
        else:
            print2(splittedContent)
    except:
        print(content)

def print4(content):
    try:
        splittedContent = content.split(") ", 1)
        if len(splittedContent) == 2:
            key, value = splittedContent
            print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>{key})</{config.terminalPromptIndicatorColor2}> {value}"))
        else:
            print2(splittedContent)
    except:
        print(content)

def getStringWidth(text):
    width = 0
    for character in text:
        width += wcwidth.wcwidth(character)
    return width

def getPygmentsStyle():
    theme = config.pygments_style if config.pygments_style else "stata-dark" if not config.terminalResourceLinkColor.startswith("ansibright") else "stata-light"
    return style_from_pygments_cls(get_style_by_name(theme))

def showErrors():
    trace = traceback.format_exc()
    print(trace if config.developer else "Error encountered!")
    return trace

def check_llm_errors(func):
    """A decorator that handles llm exceptions for the function it wraps."""
    def wrapper(*args, **kwargs):
        def finishError():
            config.stopSpinning()
            return "[INVALID]"
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = f"An error occurred in {func.__name__}: {e}"
            error_traceback = traceback.format_exc()
            print(error_message)
            print(error_traceback)

            return finishError()
    return wrapper

# online

def get_wan_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        data = response.json()
        return data['ip']
    except:
        return ""

"""
import netifaces
def get_local_ip_old(): # It does not work in some cases
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            for address in addresses[netifaces.AF_INET]:
                ip = address['addr']
                if ip != '127.0.0.1':
                    return ip"""

def get_local_ip():
  """
  Gets the local IP address of the machine.

  Returns:
    str: The local IP address.
  """
  try:
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Connect to a known external server (e.g., Google's DNS server)
    s.connect(("8.8.8.8", 80))
    # Get the local IP address assigned to the socket
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address
  except Exception as e:
    print(f"Error getting local IP address: {e}")
    return None

def runSystemCommand(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout  # Captured standard output
    error = result.stderr  # Captured standard error
    response = ""
    response += f"# Output:\n{output}"
    if error.strip():
        response += f"\n# Error:\n{error}"
    return response

def openURL(url):
    config.stopSpinning()
    if config.terminalEnableTermuxAPI:
        command = f'''termux-open-url "{url}"'''
        runSystemCommand(command)
    else:
        webbrowser.open(url)

def getWebText(url):
    try:
        # Download webpage content
        response = requests.get(url, timeout=30)
        # Parse the HTML content to extract text
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except:
        return ""

def downloadFile(url, localpath, timeout=60):
    response = requests.get(url, timeout=timeout)
    with open(localpath, 'wb') as fileObj:
        fileObj.write(response.content)

def downloadWebContent(url, timeout=60, folder="", ignoreKind=False):
    print2("Downloading web content ...")
    hasExt = re.search(r"\.([^\./]+?)$", url)
    supported_documents = TEXT_FORMATS[:]
    supported_documents.remove("org")

    response = requests.get(url, timeout=timeout)
    folder = folder if folder and os.path.isdir(folder) else os.path.join(config.toolMateAIFolder, "temp")
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
            print3(f"Downloaded at: {filename}")
            return ("any", filename)
        elif hasExt and hasExt.group(1) in supported_documents:
            return ("document", downloadBinary())
        elif is_valid_image_url(url):
            return ("image", downloadBinary())
        else:
            # download content as text
            # Save the content to a html file
            return ("text", downloadHTML())
    except:
        showErrors()
        return ("", "")

# time

def getCurrentDateTime():
    current_datetime = datetime.datetime.now()
    return current_datetime.strftime("%Y-%m-%d_%H_%M_%S")

def addTimeStamp(content):
    time = re.sub(r"\.[^\.]+?$", "", str(datetime.datetime.now()))
    return f"{content}\n[Current time: {time}]"

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

# token management

# token limit
# reference: https://platform.openai.com/docs/models/gpt-4
tokenLimits = {
    #"o1-preview": 128000,
    #"o1-mini": 128000,
    "gpt-4o": 128000,
    "gpt-4o-mini": 128000,
    "gpt-4-turbo": 128000, # Returns a maximum of 4,096 output tokens.
    "gpt-4": 8192,
    #"gpt-4-turbo-preview": 128000, # Returns a maximum of 4,096 output tokens.
    #"gpt-4-0125-preview": 128000, # Returns a maximum of 4,096 output tokens.
    #"gpt-4-1106-preview": 128000, # Returns a maximum of 4,096 output tokens.
    "gpt-3.5-turbo": 16385, # Returns a maximum of 4,096 output tokens.
    #"gpt-3.5-turbo-16k": 16385,
    #"gpt-4-32k": 32768,
}

def getDynamicTokens(messages, functionSignatures=None):
    if functionSignatures is None:
        functionTokens = 0
    else:
        functionTokens = count_tokens_from_functions(functionSignatures)
    tokenLimit = tokenLimits[config.chatGPTApiModel]
    currentMessagesTokens = count_tokens_from_messages(messages) + functionTokens
    availableTokens = tokenLimit - currentMessagesTokens
    if availableTokens >= config.chatGPTApiMaxTokens:
        return config.chatGPTApiMaxTokens
    elif (config.chatGPTApiMaxTokens > availableTokens > config.chatGPTApiMinTokens):
        return availableTokens
    return config.chatGPTApiMinTokens

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
            "o1-preview",
            "o1-mini",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0125",
            "gpt-3.5-turbo-1106",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-turbo",
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
        return count_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        #print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return count_tokens_from_messages(messages, model="gpt-4-0613")
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

# API keys / credentials

def changeChatGPTAPIkey():
    print("Enter your OpenAI API Key [optional]:")
    apikey = prompt(default=config.openaiApiKey, is_password=True)
    if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
        config.openaiApiKey = apikey
    else:
        config.openaiApiKey = "toolmate"
    setChatGPTAPIkey()

def setChatGPTAPIkey():
    # instantiate a client that can shared with plugins
    os.environ["OPENAI_API_KEY"] = config.openaiApiKey
    config.oai_client = OpenAI()
    # set variable 'OAI_CONFIG_LIST' to work with pyautogen
    oai_config_list = []
    for model in tokenLimits.keys():
        oai_config_list.append({"model": model, "api_key": config.openaiApiKey})
    os.environ["OAI_CONFIG_LIST"] = json.dumps(oai_config_list)

def setGoogleCredentials():
    config.google_cloud_credentials_file = os.path.join(config.localStorage, "credentials_google_cloud.json") # default path
    if config.google_cloud_credentials and os.path.isfile(config.google_cloud_credentials):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.google_cloud_credentials
    else:
        gccfile2 = os.path.join(config.localStorage, "credentials_googleaistudio.json")
        gccfile3 = os.path.join(config.localStorage, "credentials_googletts.json")

        if os.path.isfile(config.google_cloud_credentials_file):
            config.google_cloud_credentials = config.google_cloud_credentials_file
        elif os.path.isfile(gccfile2):
            config.google_cloud_credentials = gccfile2
        elif os.path.isfile(gccfile3):
            config.google_cloud_credentials = gccfile3
        else:
            config.google_cloud_credentials = ""
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.google_cloud_credentials if config.google_cloud_credentials else ""

# real-time information

def getWeather(latlng=""):
    # get current weather information
    # Reference: https://openweathermap.org/api/one-call-3

    if not config.openweathermapApi or config.openweathermapApi == "toolmate":
        return None

    # latitude, longitude
    if not latlng:
        latlng = geocoder.ip('me').latlng

    try:
        latitude, longitude = latlng
        # Build the URL for the weather API
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={getOpenweathermapApi_key()}&units=metric"
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

# package management

def isCommandInstalled(package):
    return True if shutil.which(package.split(" ", 1)[0]) else False

def getPackageInstalledVersion(package):
    try:
        installed_version = pkg_resources.get_distribution(package).version
        return version.parse(installed_version)
    except pkg_resources.DistributionNotFound:
        return None

def getPackageLatestVersion(package):
    try:
        response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=10)
        latest_version = response.json()['info']['version']
        return version.parse(latest_version)
    except:
        return None

def restartApp():
    print(f"Restarting {config.toolMateAIName} ...")
    os.system(f"{sys.executable} {config.toolMateAIFile}")
    exit(0)

def updateApp():
    if isServerAlive("8.8.8.8", 53):
        try:
            ubaPath = str(importlib.resources.files("uniquebible"))
            bible = True if ubaPath else False
        except:
            bible = False
        package = os.path.basename(config.toolMateAIFolder)
        thisPackage = f"{package}_android" if config.isTermux else package
        print(f"Checking '{thisPackage}' version ...")
        installed_version = getPackageInstalledVersion(thisPackage)
        if installed_version is None:
            print("Installed version information is not accessible!")
        else:
            print(f"Installed version: {installed_version}")
        latest_version = getPackageLatestVersion(thisPackage)
        if latest_version is None:
            print("Latest version information is not accessible at the moment!")
        elif installed_version is not None:
            print(f"Latest version: {latest_version}")
            if latest_version > installed_version:
                if config.thisPlatform == "Windows":
                    print("Automatic upgrade feature is yet to be supported on Windows!")
                    print(f"Run 'pip install --upgrade {thisPackage}' to manually upgrade this app!")
                else:
                    try:
                        # upgrade package
                        installPipPackage(f"--upgrade {thisPackage}{'[bible]' if bible else ''}")
                        restartApp()
                    except:
                        if config.developer:
                            print(traceback.format_exc())
                        print(f"Failed to upgrade '{thisPackage}'!")

def installPipPackage(module, update=True):
    #executablePath = os.path.dirname(sys.executable)
    #pippath = os.path.join(executablePath, "pip")
    #pip = pippath if os.path.isfile(pippath) else "pip"
    #pip3path = os.path.join(executablePath, "pip3")
    #pip3 = pip3path if os.path.isfile(pip3path) else "pip3"

    if isCommandInstalled("pip"):
        pipInstallCommand = f"{sys.executable} -m pip install"

        if update:
            if not config.isPipUpdated:
                pipFailedUpdated = "pip tool failed to be updated!"
                try:
                    # Update pip tool in case it is too old
                    updatePip = subprocess.Popen(f"{pipInstallCommand} --upgrade pip", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    *_, stderr = updatePip.communicate()
                    if not stderr:
                        print("pip tool updated!")
                    else:
                        print(pipFailedUpdated)
                except:
                    print(pipFailedUpdated)
                config.isPipUpdated = True
        try:
            upgrade = (module.startswith("-U ") or module.startswith("--upgrade "))
            if upgrade:
                moduleName = re.sub("^[^ ]+? (.+?)$", r"\1", module)
            else:
                moduleName = module
            print(f"{'Upgrading' if upgrade else 'Installing'} '{moduleName}' ...")
            installNewModule = subprocess.Popen(f"{pipInstallCommand} {module}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            *_, stderr = installNewModule.communicate()
            if not stderr:
                print(f"Package '{moduleName}' {'upgraded' if upgrade else 'installed'}!")
            else:
                print(f"Failed {'upgrading' if upgrade else 'installing'} package '{moduleName}'!")
                if config.developer:
                    print(stderr)
            return True
        except:
            return False

    else:
        print("pip command is not found!")
        return False

# config

def toggleinputaudio():
    #if self.isTtsAvailable:
    config.ttsInput = not config.ttsInput
    config.saveConfig()
    print3(f"Input Audio: '{'enabled' if config.ttsInput else 'disabled'}'!")

def toggleoutputaudio():
    #if self.isTtsAvailable:
    config.ttsOutput = not config.ttsOutput
    config.saveConfig()
    print3(f"Output Audio: '{'enabled' if config.ttsOutput else 'disabled'}'!")

# embedding

def getEmbeddingFunction(embeddingModel=None):
    # import statement is placed here to make this file compatible on Android
    embeddingModel = embeddingModel if embeddingModel is not None else config.embeddingModel
    if embeddingModel in ("text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002"):
        return OpenAIEmbeddingFunction(api_key=config.openaiApiKey, model_name=embeddingModel)
    elif embeddingModel.startswith("_ollama_"):
        return OllamaEmbeddingFunction(model_name=embeddingModel[8:], url="http://localhost:11434/api/embeddings",)
    return SentenceTransformerEmbeddingFunction(model_name=embeddingModel) # support custom Sentence Transformer Embedding models by modifying config.embeddingModel

# chromadb

def get_or_create_collection(client, collection_name, embeddingModel=None):
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
        embedding_function=getEmbeddingFunction(embeddingModel=embeddingModel),
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

# rag
# references:
# https://python.langchain.com/docs/integrations/providers/unstructured/
# https://python.langchain.com/docs/integrations/document_loaders/unstructured_file/
# https://python.langchain.com/docs/tutorials/rag/

def ragRefineDocsPath(docs_path) -> Optional[list]:
    if not os.path.exists(docs_path):
        print2("Invalid path!")
        return None

    rag = os.path.join(config.localStorage, "rag")
    Path(rag).mkdir(parents=True, exist_ok=True)

    _, file_extension = os.path.splitext(docs_path)
    if file_extension.lower() == ".zip":
        # support zip file; unzip zip file, if any
        currentTime = re.sub(r"[\. :]", "_", str(datetime.datetime.now()))
        extract_to_path = os.path.join(rag, "unpacked", currentTime)
        print3(f"Unpacking content to: {extract_to_path}")
        if not os.path.isdir(extract_to_path):
            Path(rag).mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(docs_path) as zip_ref:
            zip_ref.extractall(extract_to_path)
        docs_path = extract_to_path
    # check if file format is supported
    if os.path.isfile(docs_path):
        if file_extension[1:] in TEXT_FORMATS:
            docs_path = [docs_path]
        else:
            print2("File format not supported!")
            return None
    elif os.path.isdir(docs_path):
        docs_path = getUnstructuredFiles(docs_path)
        if not docs_path:
            print2("Support files not found!")
            return None
    else:
        print2("Document path invalid!")
        return None
    # return refined paths
    return docs_path

def ragGetSplits(docs_path, chunk_size=1000, chunk_overlap=200):
    # https://python.langchain.com/docs/integrations/providers/unstructured
    loader = UnstructuredLoader(docs_path) # file_path: Union[str, List[str]]
    doc = loader.load()
    for i in doc:
        languages = i.metadata['languages']
        if isinstance(languages, list):
            i.metadata['languages'] = languages[0]
    #print(doc)

    #chunk it
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True)
    splits = text_splitter.split_documents(doc)
    #print(splits)
    return splits

def ragSearchContext(splits, query) -> Optional[dict]:
    for i in splits:
        i.metadata["source"] = i.metadata["source"][0]
    # https://python.langchain.com/docs/integrations/text_embedding/sentence_transformers
    #embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    #embedding = OpenAIEmbeddings(model=config.embeddingModel) if config.embeddingModel in ("text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002") else SentenceTransformerEmbeddings(model_name=config.embeddingModel)
    if config.embeddingModel in ("text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002"):
        embedding = OpenAIEmbeddings(model=config.embeddingModel)
    elif config.embeddingModel.startswith("_ollama_"):
        embedding = OllamaEmbeddings(model=config.embeddingModel[8:])
    else:
        embedding = HuggingFaceEmbeddings(model_name=config.embeddingModel)
    # https://python.langchain.com/docs/integrations/vectorstores/chroma
    # https://github.com/langchain-ai/langchain/issues/7804
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedding,
        client_settings=Settings(anonymized_telemetry=False),
    )
    # reference: https://python.langchain.com/docs/modules/data_connection/retrievers/vectorstore
    # Create the retriever
    #retriever_settings = {"search_type": "similarity_score_threshold", "search_kwargs": {"score_threshold": 0.5}}
    #retriever_settings = {"search_type": "mmr"}
    if config.rag_retrieverSettings: # default: {'search_kwargs': {'k': 5}}
        # align setting with config.rag_closestMatches
        if not "search_kwargs" in config.rag_retrieverSettings:
            config.rag_retrieverSettings["search_kwargs"] = {"k": 5}
        elif "search_kwargs" in config.rag_retrieverSettings and (not "k" in config.rag_retrieverSettings["search_kwargs"] or ("k" in config.rag_retrieverSettings["search_kwargs"] and not config.rag_retrieverSettings["search_kwargs"]["k"] == config.rag_closestMatches)):
                config.rag_retrieverSettings["search_kwargs"]["k"] = config.rag_closestMatches
        retriever = vectorstore.as_retriever(**config.rag_retrieverSettings)
    else:
        retriever = vectorstore.as_retriever()
    # retrieve document
    retrieved_docs = retriever.invoke(query)
    if not retrieved_docs:
        return None
    else:
        formatted_context = {f"information_{index}": item.page_content for index, item in enumerate(retrieved_docs)}
    return formatted_context

"""
Note: run embedding with GPU, e.g. HuggingFaceEmbeddings

model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
hf = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

Chromadb
https://cookbook.chromadb.dev/embeddings/gpu-support/
"""

def getRagPrompt(query, retrievedContext):
    return f"""Question:
<question>
{query}
</question>

Context:
<context>
{retrievedContext}
</context>

Please answer my question, based on the context given above."""

#from toolmate import config, get_or_create_collection, add_vector, ragRefineDocsPath, ragGetSplits
#from pathlib import Path
#from chromadb.config import Settings
#import chromadb

def getHelpCollection(vectorStore=None):
    vectorStore = vectorStore if vectorStore else os.path.join(config.toolMateAIFolder, "help")
    Path(vectorStore).mkdir(parents=True, exist_ok=True)
    chroma_client = chromadb.PersistentClient(vectorStore, Settings(anonymized_telemetry=False))
    return get_or_create_collection(chroma_client, "help", embeddingModel="all-mpnet-base-v2")

def buildHelpStore():
    # source ../../../../bin/activate
    # python3 -c "from toolmate import buildHelpStore; buildHelpStore()"
    helpStore = os.path.join(config.toolMateAIFolder, "help")
    if os.path.isdir(helpStore):
        shutil.rmtree(helpStore)
        print2("Old help store removed!")
    collection = getHelpCollection()
    docs_path = ragRefineDocsPath(os.path.join(config.toolMateAIFolder, "docs"))
    splits = ragGetSplits(docs_path)
    for i in splits:
        add_vector(collection, i.page_content, metadata={"source": i.metadata.get("source")[0]})
