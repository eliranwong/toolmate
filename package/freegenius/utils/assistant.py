from freegenius import config, showErrors, getDayOfWeek, getFilenamesWithoutExtension, getStringWidth, stopSpinning, spinning_animation, getLocalStorage, getWebText, getWeather, getCliOutput, getLlamacppServerClient
from freegenius import print1, print2, print3, isCommandInstalled, setChatGPTAPIkey, count_tokens_from_functions, setToolDependence, tokenLimits, toggleinputaudio, toggleoutputaudio, downloadFile
from freegenius import installPipPackage, getDownloadedOllamaModels, getDownloadedGgufModels, extractPythonCode, is_valid_url, getCurrentDateTime, openURL, isExistingPath, is_CJK, exportOllamaModels, runFreeGeniusCommand
from freegenius.utils.call_llm import CallLLM
from freegenius.utils.tool_plugins import ToolStore
import openai, threading, os, traceback, re, subprocess, json, pydoc, shutil, datetime, pprint, sys, copy
from huggingface_hub import hf_hub_download
from pathlib import Path
from freegenius.utils.download import Downloader
from freegenius.utils.ollama_models import ollama_models
#from pygments.lexers.python import PythonLexer
#from pygments.lexers.shell import BashLexer
#from pygments.lexers.markup import MarkdownLexer
#from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from prompt_toolkit.shortcuts import clear, set_title
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit import print_formatted_text, HTML
from freegenius.utils.terminal_mode_dialogs import TerminalModeDialogs
from freegenius.utils.prompts import Prompts
from freegenius.utils.promptValidator import FloatValidator, TokenValidator
from freegenius.utils.get_path_prompt import GetPath
from freegenius.utils.prompt_shared_key_bindings import swapTerminalColors

from freegenius.utils.terminal_system_command_prompt import SystemCommandPrompt
from freegenius.utils.tool_plugins import Plugins
from freegenius.utils.tts_utils import TTSUtil
from freegenius.utils.ttsLanguages import TtsLanguages
from freegenius.utils.streaming_word_wrapper import StreamingWordWrapper
from freegenius.utils.text_utils import TextUtil
from freegenius.utils.sttLanguages import googleSpeeckToTextLanguages, whisperSpeeckToTextLanguages
from freegenius.groqchat import GroqChatbot
from freegenius.chatgpt import ChatGPT
from freegenius.llamacpp import LlamacppChat
from freegenius.llamacppserver import LlamacppServerChat
from freegenius.ollamachat import OllamaChat
if not config.isTermux:
    from freegenius.autobuilder import AutoGenBuilder
    from freegenius.geminipro import GeminiPro
    from freegenius.palm2 import Palm2
    from freegenius.codey import Codey
from elevenlabs.client import ElevenLabs


class FreeGenius:

    def __init__(self):
        #config.letMeDoItAI = self
        self.prompts = Prompts()
        self.dialogs = TerminalModeDialogs(self)
        self.setup()
        Plugins.runPlugins()

    def setup(self):
        config.currentMessages = []
        # set up tool store client
        ToolStore.setupToolStoreClient()

        self.models = list(tokenLimits.keys())
        config.divider = self.divider = "--------------------"
        config.runPython = True
        if not hasattr(config, "accept_default"):
            config.accept_default = False
        if not hasattr(config, "defaultEntry"):
            config.defaultEntry = ""
        config.tempContent = ""
        config.tempChunk = ""
        if not hasattr(config, "predefinedContextTemp"):
            config.predefinedContextTemp = ""
        config.systemCommandPromptEntry = ""
        config.pagerContent = ""
        #self.addPagerContent = False
        # share the following methods in config so that they are accessible via plugins
        config.toggleMultiline = self.toggleMultiline
        config.getWrappedHTMLText = self.getWrappedHTMLText
        config.fineTuneUserInput = self.fineTuneUserInput
        config.launchPager = self.launchPager
        config.addPagerText = self.addPagerText
        config.changeOpenweathermapApi = self.changeOpenweathermapApi
        config.selectedTool = ""
        # env variables
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = config.env_QT_QPA_PLATFORM_PLUGIN_PATH

        # get path
        config.addPathAt = None
        self.getPath = GetPath(
            cancel_entry="",
            promptIndicatorColor=config.terminalPromptIndicatorColor2,
            promptEntryColor=config.terminalCommandEntryColor2,
            subHeadingColor=config.terminalColors[config.terminalPromptIndicatorColor2],
            itemColor=config.terminalColors[config.terminalCommandEntryColor2],
        )

        # hisotry directory
        try:
            historyParentFolder = os.path.join(config.localStorage, "history")
            Path(historyParentFolder).mkdir(parents=True, exist_ok=True)
            for i in ("chats", "paths", "commands"):
                historyFile = os.path.join(historyParentFolder, i)
                if not os.path.isfile(historyFile):
                    open(historyFile, "a", encoding="utf-8").close()
        except:
            print("Failed saving history!")
        config.saveConfig()
        
        # check availability of api keys
        if not config.groqApi_key:
            self.changeGroqApi()
        if not config.openaiApiKey:
            self.changeChatGPTAPIkey()
        if not config.openweathermapApi:
            self.changeOpenweathermapApi()
        if not config.elevenlabsApi:
            self.changeElevenlabsApi()

        # initial completion check at startup
        if config.initialCompletionCheck:
            if config.llmInterface == "llamacppserver":
                runFreeGeniusCommand("customtoolserver")
                if config.useAdditionalChatModel:
                    runFreeGeniusCommand("customchatserver")
            else:
                CallLLM.checkCompletion()

        chat_history = os.path.join(config.localStorage, "history", "chats")
        self.terminal_chat_session = PromptSession(history=FileHistory(chat_history))

        self.actions = {
            ".new": (f"start a new chat {str(config.hotkey_new)}", None),
            ".save": ("save content", lambda: self.saveChat(config.currentMessages)),
            ".export": (f"export content {str(config.hotkey_export)}", lambda: self.exportChat(config.currentMessages)),
            ".context": (f"change chat context {str(config.hotkey_select_context)}", None),
            ".contextintegration": ("change chat context integration", self.setContextIntegration),
            ".model": ("change large language model", self.setLlmModel),
            #".chatmodel": ("change chat-only model", self.setChatbot),
            ".embedding": ("change embedding model", self.setEmbeddingModel),
            ".apikeys": ("change API keys", self.changeAPIkeys),
            #".changeapikey": ("change OpenAI API key", self.changeChatGPTAPIkey),
            #".openweathermapapi": ("change OpenWeatherMap API key", self.changeOpenweathermapApi),
            #".elevenlabsapi": ("change ElevenLabs API key", self.changeElevenlabsApi),
            ".temperature": ("change temperature", self.setTemperature),
            ".maxtokens": ("change maximum output tokens", self.setMaxTokens),
            ".mintokens": ("change minimum output tokens", self.setMinTokens),
            ".dynamictokencount": ("change dynamic token count", self.setDynamicTokenCount),
            ".maxautocorrect": ("change maximum consecutive auto-correction", self.setMaxAutoCorrect),
            ".maxmemorymatches": ("change maximum memory matches", self.setMemoryClosestMatches),
            ".maxchatrecordmatches": ("change maximum chat record matches", self.setChatRecordClosestMatches),
            ".tools": ("change tool selection configurations", self.setToolSelectionConfigs),
            ".plugins": ("change plugins", self.selectPlugins),
            ".functioncall": ("change function call", self.setFunctionCall),
            ".functioncallintegration": ("change function call integration", self.setFunctionResponse),
            ".latestSearches": ("change online searches", self.setLatestSearches),
            ".userconfirmation": ("change code confirmation protocol", self.setUserConfirmation),
            ".codedisplay": ("change code display", self.setCodeDisplay),
            ".pagerview": ("change pager view", self.setPagerView),
            ".assistantname": ("change assistant name", self.setAssistantName),
            ".systemmessage": ("change custom system message", self.setCustomSystemMessage),
            ".ipinfo": ("change ip information integration", self.setIncludeIpInSystemMessage),
            ".storagedirectory": ("change storage directory", self.setStorageDirectory),
            ".voicerecognition": ("change voice recognition", self.setSpeechToTextConfig),
            ".voicegeneration": ("change voice generation", self.setTextToSpeechConfig),
            ".googleapiservice": ("change Google API service", self.selectGoogleAPIs),
            ".autobuilderconfig": ("change auto builder config", self.setAutoGenBuilderConfig),
            ".customtexteditor": ("change custom text editor", self.setCustomTextEditor),
            ".termuxapi": ("change Termux API integration", self.setTermuxApi),
            ".autoupgrade": ("change automatic upgrade", self.setAutoUpgrade),
            ".developer": (f"change developer mode {str(config.hotkey_toggle_developer_mode)}", self.setDeveloperMode),
            ".togglemultiline": (f"toggle multi-line input {str(config.hotkey_toggle_multiline_entry)}", self.toggleMultiline),
            ".togglemousesupport": (f"toogle mouse support {str(config.hotkey_toggle_mouse_support)}", self.toggleMouseSupport),
            ".toggletextbrightness": (f"swap text brightness {str(config.hotkey_swap_text_brightness)}", swapTerminalColors),
            ".togglewordwrap": (f"toggle word wrap {str(config.hotkey_toggle_word_wrap)}", self.toggleWordWrap),
            ".toggleimprovedwriting": (f"toggle improved writing {str(config.hotkey_toggle_writing_improvement)}", self.toggleImprovedWriting),
            ".toggleinputaudio": (f"toggle input audio {str(config.hotkey_toggle_input_audio)}", toggleinputaudio),
            ".toggleoutputaudio": (f"toggle output audio {str(config.hotkey_toggle_response_audio)}", toggleoutputaudio),
            ".code": (f"extract the python code from the last response", self.extractPythonCodeFromLastResponse),
            ".run": (f"run the python code in the last response", self.runPythonCodeInLastResponse),
            ".editresponse": (f"edit the last response {str(config.hotkey_edit_last_response)}", self.editLastResponse),
            ".editconfigs": ("edit configuration settings", self.editConfigs),
            ".install": ("install python package", self.installPythonPackage),
            ".system": (f"open system command prompt {str(config.hotkey_launch_system_prompt)}", lambda: SystemCommandPrompt().run(allowPathChanges=True)),
            ".content": ("display current directory content", self.getPath.displayDirectoryContent),
            ".keys": (f"display key bindings {str(config.hotkey_display_key_combo)}", config.showKeyBindings),
            ".help": ("open LetMeDoIt wiki", lambda: openURL('https://github.com/eliranwong/letmedoit/wiki')),
            ".donate": ("donate and support LetMeDoIt AI", lambda: openURL('https://www.paypal.com/paypalme/letmedoitai')),
        }

        config.actionHelp = f"# Quick Actions\n(entries that start with '.')\n"
        for key, value in self.actions.items():
            config.actionHelp += f"{key}: {value[0]}\n"
        config.actionHelp += "\n## Read more at:\nhttps://github.com/eliranwong/letmedoit/wiki/Action-Menu"

    # Speech-to-Text Language
    def setSpeechToTextLanguage(self):
        # record in history for easy retrieval by moving arrows upwards / downwards
        voice_typing_language_history = os.path.join(config.localStorage, "history", "voice_typing_language")
        voice_typing_language_session = PromptSession(history=FileHistory(voice_typing_language_history))
        # input suggestion for languages
        languages = tuple(googleSpeeckToTextLanguages.keys()) if config.voiceTypingPlatform in ("google", "googlecloud") else whisperSpeeckToTextLanguages
        # default
        default = ""
        for i in languages:
            if config.voiceTypingPlatform in ("google", "googlecloud") and googleSpeeckToTextLanguages[i] == config.voiceTypingLanguage:
                default = i
            elif i == config.voiceTypingLanguage:
                default = i
        if not default:
            default = "English (United States)" if config.voiceTypingPlatform in ("google", "googlecloud") else "english"
        # completer
        completer = FuzzyCompleter(WordCompleter(languages, ignore_case=True))
        print1("Please specify the Speech-to-Text language:")
        language = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=default, promptSession=voice_typing_language_session, completer=completer)
        if language and not language in (config.exit_entry, config.cancel_entry):
            config.voiceTypingLanguage = language
        if not config.voiceTypingLanguage in languages:
            config.voiceTypingLanguage = "en-US" if config.voiceTypingPlatform in ("google", "googlecloud") else "english"
        if config.voiceTypingPlatform in ("google", "googlecloud") and config.voiceTypingLanguage in languages:
            config.voiceTypingLanguage = googleSpeeckToTextLanguages[config.voiceTypingLanguage]

    # Windows built-in tts voice via wsay command
    def setWsayVoice(self):
        print2("Available voices:")
        os.system("wsay --list_voices")
        print2("Use the number provided by '--list_voices' to select a voice:")
        option = self.prompts.simplePrompt(numberOnly=True, style=self.prompts.promptStyle2, default=config.wsay_voice)
        if option and not option in (config.exit_entry, config.cancel_entry):
            config.wsay_voice = option
            TTSUtil.play("Testing")

    def setWsaySpeed(self):
        print2("Specify the voice speed:")
        print1("(from 0 to 100; 50 is the default speed)")
        option = self.prompts.simplePrompt(numberOnly=True, style=self.prompts.promptStyle2, default=config.wsay_speed)
        if option and not option in (config.exit_entry, config.cancel_entry):
            config.wsay_speed = option
            TTSUtil.play("Testing")

    # macOS built-in tts voice
    def setSayVoice(self):
        ps = subprocess.Popen('say -v "?"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, *_ = ps.communicate()
        voices = stdout.decode("utf-8").strip()
        voices = re.sub(" [ ]+?([^ ])", r" \1", voices)
        voices = re.sub(" [ ]*?#.*?$", "", voices, flags=re.M)
        voices = re.sub(" ([A-Za-z_]+?)$", r" [\1]", voices, flags=re.M)
        voices = voices.split("\n")
        voice_history = os.path.join(config.localStorage, "history", "sayVoice")
        voice_session = PromptSession(history=FileHistory(voice_history))
        completer = FuzzyCompleter(WordCompleter(voices, ignore_case=True))
        print2("Please specify a voice:")
        print3("Read: https://github.com/eliranwong/freegenius/wiki/Offline-TTS-%E2%80%90-macOS#download-more-voices")
        print1("(leave it blank to use the default voice)")
        if not config.say_voice in voices:
            config.say_voice = ""
        option = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.say_voice, promptSession=voice_session, completer=completer)
        if option and not option in (config.exit_entry, config.cancel_entry):
            config.say_voice = re.sub(" \[[^\]]*?\]$", "", option)
            TTSUtil.play("Testing")

    def setSaySpeed(self):
        print2("Specify the voice speed:")
        print1("(from 100 to 300; 200 is the default speed)")
        option = self.prompts.simplePrompt(numberOnly=True, style=self.prompts.promptStyle2, default=config.say_speed)
        if option and not option in (config.exit_entry, config.cancel_entry):
            config.say_speed = option
            TTSUtil.play("Testing")

    # Piper-tts Voice
    def setPiperVoice(self):
        # create model directory if it does not exist
        model_dir = os.path.join(config.localStorage, "LLMs", "piper")
        Path(model_dir).mkdir(parents=True, exist_ok=True)
        # record in history for easy retrieval by moving arrows upwards / downwards
        piperVoice_history = os.path.join(config.localStorage, "history", "piperVoice")
        piperVoice_session = PromptSession(history=FileHistory(piperVoice_history))
        completer = FuzzyCompleter(WordCompleter(TtsLanguages.piper, ignore_case=True))
        print2("Please specify a Piper voice model:")
        print3("Details: https://github.com/rhasspy/piper/blob/master/VOICES.md")
        if not config.piper_voice in TtsLanguages.piper:
            config.piper_voice = "en_US-lessac-medium"
        option = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.piper_voice, promptSession=piperVoice_session, completer=completer)
        if option and not option in (config.exit_entry, config.cancel_entry):
            config.piper_voice = option
            TTSUtil.play("Testing")

    # ElevenLabs Text-to-Speech Voice
    def setElevenlabsVoice(self):
        # record in history for easy retrieval by moving arrows upwards / downwards
        elevenlabsVoice_history = os.path.join(config.localStorage, "history", "elevenlabsVoice")
        elevenlabsVoice_session = PromptSession(history=FileHistory(elevenlabsVoice_history))
        # input suggestion for options
        options = {}
        ids = {}
        for voice in list(ElevenLabs(api_key=config.elevenlabsApi).voices.get_all())[0][-1]:
            options[voice.name] = voice.voice_id
            ids[voice.voice_id] = voice.name
        # default
        default = ids[config.elevenlabsVoice] if config.elevenlabsVoice in ids else "Rachel"
        # completer
        completer = FuzzyCompleter(WordCompleter(options.keys(), ignore_case=True))
        print1("Please specify ElevenLabs Text-to-Speech Voice:")
        option = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=default, promptSession=elevenlabsVoice_session, completer=completer)
        if option and not option in (config.exit_entry, config.cancel_entry):
            config.elevenlabsVoice = options[option] if option in options else "21m00Tcm4TlvDq8ikWAM" # Rachel's voice id

    # Google Text-to-Speech (Generic)
    def setGttsLanguage(self):
        # record in history for easy retrieval by moving arrows upwards / downwards
        gtts_language_history = os.path.join(config.localStorage, "history", "gtts_language")
        gtts_language_session = PromptSession(history=FileHistory(gtts_language_history))
        # input suggestion for languages
        languages = tuple(TtsLanguages.gtts.keys())
        # default
        default = ""
        for i in languages:
            if TtsLanguages.gtts[i] == config.gttsLang:
                default = i
        if not default:
            default = "en"
        # completer
        completer = FuzzyCompleter(WordCompleter(languages, ignore_case=True))
        print1("Please specify Google Text-to-Speech language:")
        language = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=default, promptSession=gtts_language_session, completer=completer)
        if language and not language in (config.exit_entry, config.cancel_entry):
            config.gttsLang = language
        if config.gttsLang in languages:
            config.gttsLang = TtsLanguages.gtts[config.gttsLang]
        else:
            config.gttsLang = "en"

    # Google Cloud Text-to-Speech (API)
    def setGcttsLanguage(self):
        # record in history for easy retrieval by moving arrows upwards / downwards
        gctts_language_history = os.path.join(config.localStorage, "history", "gctts_language")
        gctts_language_session = PromptSession(history=FileHistory(gctts_language_history))
        # input suggestion for languages
        languages = tuple(TtsLanguages.gctts.keys())
        # default
        default = ""
        for i in languages:
            if TtsLanguages.gctts[i] == config.gcttsLang:
                default = i
        if not default:
            default = "en-US"
        # completer
        completer = FuzzyCompleter(WordCompleter(languages, ignore_case=True))
        print1("Please specify Google Cloud Text-to-Speech language:")
        language = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=default, promptSession=gctts_language_session, completer=completer)
        if language and not language in (config.exit_entry, config.cancel_entry):
            config.gcttsLang = language
        if config.gcttsLang in languages:
            config.gcttsLang = TtsLanguages.gctts[config.gcttsLang]
        else:
            config.gcttsLang = "en-US"

    def setVlcSpeed(self):
        if config.isVlcPlayerInstalled and not config.usePygame:
            print1("Specify VLC player playback speed:")
            print1("(between 0.1 and 2.0)")
            vlcSpeed = self.prompts.simplePrompt(style=self.prompts.promptStyle2, validator=FloatValidator(), default=str(config.vlcSpeed))
            if vlcSpeed and not vlcSpeed.strip().lower() == config.exit_entry:
                vlcSpeed = float(vlcSpeed)
                if vlcSpeed < 0.1:
                    vlcSpeed = 0.1
                elif vlcSpeed > 2:
                    vlcSpeed = 2
                config.vlcSpeed = round(vlcSpeed, 1)
                print3(f"VLC player playback speed: {vlcSpeed}")

    def setGcttsSpeed(self):
        print1("Specify Google Cloud Text-to-Speech playback speed:")
        print1("(between 0.1 and 2.0)")
        gcttsSpeed = self.prompts.simplePrompt(style=self.prompts.promptStyle2, validator=FloatValidator(), default=str(config.gcttsSpeed))
        if gcttsSpeed and not gcttsSpeed.strip().lower() == config.exit_entry:
            gcttsSpeed = float(gcttsSpeed)
            if gcttsSpeed < 0.1:
                gcttsSpeed = 0.1
            elif gcttsSpeed > 2:
                gcttsSpeed = 2
            config.gcttsSpeed = round(gcttsSpeed, 1)
            print3(f"Google Cloud Text-to-Speech playback speed: {gcttsSpeed}")

    def selectGoogleAPIs(self):
        if os.environ["GOOGLE_APPLICATION_CREDENTIALS"]:
            enabledGoogleAPIs = self.dialogs.getMultipleSelection(
                title="Google Cloud Service",
                text="Select to enable Google Cloud Service in LetMeDoIt AI:",
                options=("Vertex AI", "Speech-to-Text", "Text-to-Speech"),
                default_values=config.enabledGoogleAPIs,
            )
            if enabledGoogleAPIs is not None:
                config.enabledGoogleAPIs = enabledGoogleAPIs
        else:
            config.enabledGoogleAPIs = ["Vertex AI"]
            print1(f"API key json file '{config.google_cloud_credentials_file}' not found!")
            print1("Read https://github.com/eliranwong/letmedoit/wiki/Google-API-Setup for setting up Google API.")
        if "Speech-to-Text" in config.enabledGoogleAPIs:
            if not config.voiceTypingPlatform == "googlecloud":
                config.voiceTypingPlatform = "googlecloud"
                print3("Speech-to-Text platform changed to: Google Text-to-Speech (API)")
            self.setSpeechToTextLanguage()
        if "Text-to-Speech" in config.enabledGoogleAPIs:
            if not config.ttsPlatform == "googlecloud":
                config.ttsPlatform = "googlecloud"
                print3("Text-to-Speech platform changed to: Google Text-to-Speech (API)")
            self.setGcttsLanguage()
            self.setGcttsSpeed()
        config.saveConfig()

    def selectPlugins(self):
        plugins = []
        enabledPlugins = []
        pluginFolder = os.path.join(config.freeGeniusAIFolder, "plugins")
        if config.localStorage:
            customPluginFoler = os.path.join(config.localStorage, "plugins")
            Path(customPluginFoler).mkdir(parents=True, exist_ok=True)
            pluginFolders = (pluginFolder, customPluginFoler)
        else:
            pluginFolders = (pluginFolder,)
        for folder in pluginFolders:
            for plugin in getFilenamesWithoutExtension(folder, "py"):
                plugins.append(plugin)
                if not plugin in config.pluginExcludeList:
                    enabledPlugins.append(plugin)
        enabledPlugins = self.dialogs.getMultipleSelection(
            title="Enable / Disable Plugins",
            text="Select to enable plugin(s):",
            options=plugins,
            default_values=enabledPlugins,
        )
        if enabledPlugins is not None:
            for p in plugins:
                if p in enabledPlugins and p in config.pluginExcludeList:
                    config.pluginExcludeList.remove(p)
                elif not p in enabledPlugins and not p in config.pluginExcludeList:
                    config.pluginExcludeList.append(p)
            Plugins.runPlugins()
            config.saveConfig()
            print1("Plugin selection updated!")

    def fingerprint(self):
        try:
            output = json.loads(getCliOutput("termux-fingerprint"))
            return True if output["auth_result"] == "AUTH_RESULT_SUCCESS" else False
        except:
            return False

    def changeAPIkeys(self):
        self.changeGroqApi()
        self.changeChatGPTAPIkey()
        self.changeOpenweathermapApi()
        self.changeElevenlabsApi()

    def changeChatGPTAPIkey(self):
        if not config.terminalEnableTermuxAPI or (config.terminalEnableTermuxAPI and self.fingerprint()):
            print3("# ChatGPT API Key: allows access to ChatGPT models")
            print1("To set up ChatGPT API Key, read:\nhttps://github.com/eliranwong/letmedoit/wiki/ChatGPT-API-Key#how-to-obtain\n")
            print1("Enter your OpenAI API Key [optional]:")
            apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.openaiApiKey, is_password=True)
            if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
                config.openaiApiKey = apikey
                CallLLM.checkCompletion()
            else:
                config.openaiApiKey = "freegenius"
            #print1("Enter your Organization ID [optional]:")
            #oid = self.prompts.simplePrompt(default=config.openaiApiOrganization, is_password=True)
            #if oid and not oid.strip().lower() in (config.cancel_entry, config.exit_entry):
            #    config.openaiApiOrganization = oid
            config.saveConfig()
            print2("Configurations updated!")
            setChatGPTAPIkey()

    def changeGroqApi(self):
        if not config.terminalEnableTermuxAPI or (config.terminalEnableTermuxAPI and self.fingerprint()):
            print3("# Groq Cloud API Key: allows access to Groq Cloud hosted LLMs")
            print1("To set up Groq Cloud API Key, read:\nhttps://github.com/eliranwong/freegenius/wiki/Set-up-a-Groq-Cloud-API-Key\n")
            print1("Enter a single or a list of multiple Groq Cloud API Key(s) [optional]:")
            print()
            apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=str(config.groqApi_key), is_password=True)
            if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
                try:
                    if isinstance(eval(apikey), list):
                        config.groqApi_key = eval(apikey)
                except:
                    config.groqApi_key = apikey
                CallLLM.checkCompletion()
            else:
                config.groqApi_key = "freegenius"
            config.saveConfig()
            print2("Configurations updated!")

    def changeOpenweathermapApi(self):
        if not config.terminalEnableTermuxAPI or (config.terminalEnableTermuxAPI and self.fingerprint()):
            print3("# OpenWeatherMap API Key: allows access to real-time weather information")
            print1("To set up OpenWeatherMap API Key, read:\nhttps://github.com/eliranwong/letmedoit/wiki/OpenWeatherMap-API-Setup\n")
            print1("Enter your OpenWeatherMap API Key [optional]:")
            print()
            apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.openweathermapApi, is_password=True)
            if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
                config.openweathermapApi = apikey
            if getWeather() is not None:
                print2("Configurations updated!")
            else:
                config.openweathermapApi = "freegenius"
                print2("Invalid API key entered!")
            config.saveConfig()

    def changeElevenlabsApi(self):
        if not config.terminalEnableTermuxAPI or (config.terminalEnableTermuxAPI and self.fingerprint()):
            print3("# ElevenLabs API Key: allows access to voice generation feature offered by ElevenLabs")
            print1("To set up ElevenLabs API Key, read:\nhttps://elevenlabs.io/docs/api-reference/text-to-speech#authentication\n")
            print1("Enter your ElevenLabs API Key [optional]:")
            print()
            apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.elevenlabsApi, is_password=True)
            if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
                config.elevenlabsApi = apikey
            try:
                # testing
                ElevenLabs(api_key=config.elevenlabsApi).generate(
                    #api_key=config.elevenlabsApi, # Defaults to os.getenv(ELEVEN_API_KEY)
                    text="test",
                    voice=config.elevenlabsVoice,
                    model="eleven_multilingual_v2"
                )
                print2("Configurations updated!")
            except:
                config.elevenlabsApi = "freegenius"
                print2("Invalid API key entered!")
            config.saveConfig()

    def exitAction(self):
        message = "closing ..."
        print2(message)
        print1(self.divider)
        return ""

    # update system message
    def updateSystemMessage(self, messages):
        for index, message in enumerate(messages):
            try:
                if message.get("role", "") == "system":
                    # update system mess
                    dayOfWeek = getDayOfWeek()
                    message["content"] = re.sub(
                        """^Current directory: .*?\nCurrent time: .*?\nCurrent day of the week: .*?$""",
                        f"""Current directory: {os.getcwd()}\nCurrent time: {str(datetime.datetime.now())}\nCurrent day of the week: {dayOfWeek}""",
                        message["content"],
                        flags=re.M,
                    )
                    messages[index] = message
                    # in a long conversation, ChatGPT often forgets its system message
                    # move forward if conversation have started, to enhance system message
                    if config.conversationStarted and not index == len(messages) - 1:
                        item = messages.pop(index)
                        messages.append(item)
                    break
            except:
                pass
        return messages

    def getCurrentContext(self):
        if not config.predefinedContext in config.predefinedContexts:
            print2(f"'{config.predefinedContext}' not defined!")
            config.predefinedContext = config.predefinedContextTemp if config.predefinedContextTemp and config.predefinedContextTemp in config.predefinedContexts else "[none]"
            print3(f"Predefined context changed to: {config.predefinedContext}")
        if config.predefinedContext == "[none]":
            # no context
            context = ""
        elif config.predefinedContext == "[custom]":
            # custom input in the settings dialog
            context = config.customPredefinedContext
        else:
            # users can modify config.predefinedContexts via plugins
            context = config.predefinedContexts[config.predefinedContext]
        return context

    def showCurrentContext(self):
        description = self.getCurrentContext()
        if description:
            description = f"\n{description}"
        print1(self.divider)
        print3(f"Context: {config.predefinedContext}{description}")
        print1(self.divider)

    def fineTuneUserInput(self, userInput):
        # customise chat context
        context = self.getCurrentContext()
        if is_valid_url(userInput) and config.predefinedContext in ("Let me Summarize", "Let me Explain"):
            context = context.replace("the following content:\n[NO_TOOL]", "the content in the this web url:\n")
        elif is_valid_url(userInput) and config.predefinedContext == "Let me Translate":
            userInput = getWebText(userInput)
        if context and (not config.conversationStarted or (config.conversationStarted and config.applyPredefinedContextAlways)):
            # context may start with "You will be provided with my input delimited with a pair of XML tags, <input> and </input>. ...
            userInput = re.sub("<content>|<content [^<>]*?>|</content>", "", userInput)
            userInput = f"{context}\n<content>{userInput}</content>" if userInput.strip() else context
        #userInput = SharedUtil.addTimeStamp(userInput)
        return userInput

    def runActions(self, userInput, feature=""):
        query = ""
        featureTemp = feature
        options = tuple(self.actions.keys())
        descriptions = [i[0] for i in self.actions.values()]
        if not feature or not feature in self.actions:
            # filter avilable actions
            if feature.startswith("."):
                query = feature[1:]
            feature = self.dialogs.getValidOptions(
                options=options,
                descriptions=descriptions,
                title=config.freeGeniusAIName,
                default=config.defaultBlankEntryAction,
                text="Select an action or make changes:",
                filter=query,
            )
        if feature:
            if self.actions[feature][-1] is not None:
                self.actions[feature][-1]()
            else:
                # current execeptions are ".new" and ".context"
                userInput = feature
        elif featureTemp:
            # when the entered feature does not match an action
            return featureTemp
        return userInput

    def setAutoUpgrade(self):
        options = ("enable", "disable")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Automatic Upgrade on Startup",
            default="enable" if config.autoUpgrade else "disable",
            text="Select an option below:"
        )
        if option:
            config.autoUpgrade = (option == "enable")
            config.saveConfig()
            print3(f"Automatic Upgrade: {option}d!")

    def setDynamicTokenCount(self):
        options = ("enable", "disable")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Dynamic Token Count",
            default="enable" if config.dynamicTokenCount else "disable",
            text="Perform token count as you type.\nSelect an option below:"
        )
        if option:
            config.dynamicTokenCount = (option == "enable")
            config.saveConfig()
            print3(f"Dynamic token count: {option}d!")
            print3("Note: Changes applicable to 'chatgpt' and 'letmedoit' interfaces only.")

    def setIncludeIpInSystemMessage(self):
        options = ("enable", "disable")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Include IP information",
            default="enable" if config.includeIpInDeviceInfo else "disable",
            text="Include IP information in system message\ncan enhance response about locations.\nSelect an option below:"
        )
        if option:
            config.includeIpInDeviceInfo = (option == "enable")
            config.saveConfig()
            print3(f"Include IP information: {option}d!")

    def setCodeDisplay(self):
        options = ("enable", "disable")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Code Display",
            default="enable" if config.codeDisplay else "disable",
            text="Options to display programming code before execution:"
        )
        if option:
            config.codeDisplay = (option == "enable")
            config.saveConfig()
            print3(f"Code display: {option}d!")

    def setContextIntegration(self):
        options = ("the first input only", "all inputs")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Predefined Context Integration",
            default="all inputs" if config.applyPredefinedContextAlways else "the first input only",
            text="Define below how you want to integrate predefined context\nwith your inputs.\nApply predefined context in ...",
        )
        if option:
            config.applyPredefinedContextAlways = True if option == "all inputs" else False
            config.saveConfig()
            print3(f"Predefined Context Integration: {option}!")

    def setStorageDirectory(self):
        try:
            folder = self.getPath.getFolderPath(
                check_isdir=True,
                display_dir_only=True,
                create_dirs_if_not_exist=True,
                empty_to_cancel=True,
                list_content_on_directory_change=True,
                keep_startup_directory=True,
                message=f"{self.divider}\nSetting a startup directory ...\nEnter a folder name or path below:",
                default=config.storagedirectory,
            )
        except:
            print2(f"Given path not accessible!")
            folder = ""
        if folder and os.path.isdir(folder):
            config.storagedirectory = folder
            config.localStorage = getLocalStorage()
            config.saveConfig()
            print3(f"Startup directory:\n{folder}")

    def setLatestSearches(self):
        options = ("always", "auto", "none")
        descriptions = (
            "always search for latest information",
            "search only when ChatGPT lacks information",
            "do not perform online searches",
        )
        option = self.dialogs.getValidOptions(
            options=options,
            descriptions=descriptions,
            title="Latest Online Searches",
            default=config.loadingInternetSearches,
            text=f"{config.freeGeniusAIName} can perform online searches.\nHow do you want this feature?",
        )
        if option:
            config.loadingInternetSearches = option
            # fine tune
            if config.loadingInternetSearches == "auto":
                config.chatGPTApiFunctionCall = "auto"
                if "integrate google searches" in config.pluginExcludeList:
                    config.pluginExcludeList.remove("integrate google searches")
            elif config.loadingInternetSearches == "none":
                if not "integrate google searches" in config.pluginExcludeList:
                    config.pluginExcludeList.append("integrate google searches")
            # reset plugins
            Plugins.runPlugins()
            # notify
            config.saveConfig()
            print3(f"Latest Online Searches: {option}")

    def setUserConfirmation(self):
        options = ("always", "medium_risk_or_above", "high_risk_only", "none")
        if not config.confirmExecution in options:
            config.confirmExecution = "always"
        descriptions = (
            "always",
            "medium risk or above",
            "high risk only, e.g. file deletion",
            "none",
        )
        option = self.dialogs.getValidOptions(
            options=options,
            descriptions=descriptions,
            title="Command Confirmation Protocol",
            text=f"{config.freeGeniusAIName} is designed to execute commands on your behalf.\nPlease specify when you would prefer\nto receive a confirmation\nbefore commands are executed:\n(Note: Execute commands at your own risk.)",
            default=config.confirmExecution,
        )
        if option:
            config.confirmExecution = option
            config.saveConfig()
            print3(f"Command Confirmation Protocol: {option}")

    def setPagerView(self):
        manuel = f"""manual '{str(config.hotkey_launch_pager_view).replace("'", "")}'"""
        options = ("auto", manuel)
        option = self.dialogs.getValidOptions(
            options=options,
            title="Pager View",
            default="auto" if config.pagerView else manuel,
        )
        if option:
            config.pagerView = (option == "auto")
            config.saveConfig()
            print3(f"Pager View: {option}!")

    def setDeveloperMode(self):
        options = ("enable", "disable")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Developer Mode",
            default="enable" if config.developer else "disable",
            text="Read LetMeDoIt wiki for more information.\nSelect an option below:"
        )
        if option:
            config.developer = (option == "enable")
            config.saveConfig()
            print3(f"Developer Mode: {option}d!")

    def setTermuxApi(self):
        options = ("enable", "disable")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Termux API Integration",
            default="enable" if config.terminalEnableTermuxAPI else "disable",
            text="To learn about Termux API, read:\nhttps://wiki.termux.com/wiki/Termux:API\nSelect an option below:"
        )
        if option:
            config.terminalEnableTermuxAPI = (option == "enable")
            if config.terminalEnableTermuxAPI and not os.path.isdir("/data/data/com.termux/files/home/"):
                config.terminalEnableTermuxAPI = False
                print1("Termux is not installed!")
            if config.terminalEnableTermuxAPI:
                # Check if Termux API package is installed
                result = subprocess.run(['pkg', 'list-installed', 'termux-api'], capture_output=True, text=True)
                # Check if the package is installed
                if not "termux-api" in result.stdout:
                    print1("Termux:API is not installed!")
            # reset plugins
            Plugins.runPlugins()
            config.saveConfig()
            print3(f"""Termux API Integration: {"enable" if config.terminalEnableTermuxAPI else "disable"}d!""")

    def setFunctionCall(self):
        calls = ("auto", "none")
        call = self.dialogs.getValidOptions(
            options=calls,
            title="ChatGPT Function Call",
            default=config.chatGPTApiFunctionCall,
            text="Enabling function call\nto extend ChatGPT capabilities.\nEnable / Disable this feature below:",
        )
        if call:
            config.chatGPTApiFunctionCall = call
            config.saveConfig()
            print3(f"ChaptGPT function call: {'enabled' if config.chatGPTApiFunctionCall == 'auto' else 'disabled'}!")

    def setFunctionResponse(self):
        calls = ("enable", "disable")
        call = self.dialogs.getValidOptions(
            options=calls,
            title="Pass Function Call Response to ChatGPT",
            default="enable" if config.passFunctionCallReturnToChatGPT else "disable",
            text="Enabling this feature allows\npassing function call responses, if any,\nto extend conversation with ChatGPT.\nDisabling this feature allows\nrunning function calls\nwithout generating further responses."
        )
        if call:
            config.passFunctionCallReturnToChatGPT = (call == "enable")
            config.saveConfig()
            print3(f"Pass Function Call Response to ChatGPT: {'enabled' if config.passFunctionCallReturnToChatGPT else 'disabled'}!")

    def editLastResponse(self):
        customTextEditor = config.customTextEditor if config.customTextEditor else f"{sys.executable} {os.path.join(config.freeGeniusAIFolder, 'eTextEdit.py')}"
        pydoc.pipepager(config.pagerContent, cmd=customTextEditor)
        set_title(config.freeGeniusAIName)

    def extractPythonCodeFromLastResponse(self):
        config.defaultEntry = f'''```python
{extractPythonCode(config.pagerContent, keepInvalid=True)}```'''

    def runPythonCodeInLastResponse(self):
        code = extractPythonCode(config.pagerContent)
        if code:
            config.defaultEntry = f'''```python
{code}```'''
            config.accept_default = True
        else:
            config.defaultEntry = extractPythonCode(config.pagerContent, keepInvalid=True)

    # change configs
    def editConfigs(self):
        # file paths
        configFile = os.path.join(config.freeGeniusAIFolder, "config.py")
        backupFile = os.path.join(config.localStorage, "config_backup.py")
        # backup configs
        config.saveConfig()
        shutil.copy(configFile, backupFile)
        # open current configs with built-in text editor
        customTextEditor = config.customTextEditor if config.customTextEditor else f"{sys.executable} {os.path.join(config.freeGeniusAIFolder, 'eTextEdit.py')}"
        os.system(f"{customTextEditor} {configFile}")
        set_title(config.freeGeniusAIName)
        # re-load configs
        try:
            config.loadConfig(configFile)
            print2("Changes loaded!")
        except:
            print2("Failed to load your changes!")
            print(traceback.format_exc())
            try:
                print2("Restoring backup ...")
                config.loadConfig(backupFile)
                shutil.copy(backupFile, configFile)
                print2("Restored!")
            except:
                print2("Failed to restore backup!")

    def installPythonPackage(self):
        print1("Enter a python package name:")
        package = self.prompts.simplePrompt(style=self.prompts.promptStyle2)
        if package:
            print1(f"Installing '{package}' ...")
            installPipPackage(f"--upgrade {package}")

    def setTemperature(self):
        print1("Enter a value between 0.0 and 2.0:")
        print1("(Lower values for temperature result in more consistent outputs, while higher values generate more diverse and creative results. Select a temperature value based on the desired trade-off between coherence and creativity for your specific application.)")
        temperature = self.prompts.simplePrompt(style=self.prompts.promptStyle2, validator=FloatValidator(), default=str(config.llmTemperature))
        if temperature and not temperature.strip().lower() == config.exit_entry:
            temperature = float(temperature)
            if temperature < 0:
                temperature = 0
            elif temperature > 2:
                temperature = 2
            config.llmTemperature = round(temperature, 1)
            config.saveConfig()
            print3(f"LLM Temperature: {temperature}")

    def setToolSelectionConfigs(self):
        print2("# Introduction. FreeGenius AI enhances LLM capabilities by offering tools through plugins. When a user makes a request, FreeGenius AI searches for and selects a suitable tool from its tool store. This search involves finding similarities between the user query and the examples provided in the tool plugins. Users have the flexibility to customize the tool selection process by adjusting three key configurations:")
        print2("""1) tool_dependence
2) tool_auto_selection_threshold
3) tool_selection_max_choices""")
        print2("# Tool Dependence. The value of 'tool_dependence' determines how you want to rely on tools.")
        print1("Acceptable range: 0.0 - 1.0")
        print1("A value of 0.0 indicates that tools are disabled. FreeGenius's responses are totally based on capabilities of the selected LLM.")
        print1("A value of 1.0 indicates that tools always apply for each response.")
        print1("A value between 0.0 and 0.1 indicates that a tool is selected only when tool distance search is less than or equal to its value.")
        print1("Therefore, you are more likely to use tools when you set a higher value.")
        print2("Please enter a value between 0.0 and 1.0 to set its value:")
        tool_dependence = self.prompts.simplePrompt(style=self.prompts.promptStyle2, validator=FloatValidator(), default=str(config.tool_dependence))
        if tool_dependence and not tool_dependence.strip().lower() == config.exit_entry:
            tool_dependence = float(tool_dependence)
            if tool_dependence < 0:
                tool_dependence = 0.0
            elif tool_dependence > 1:
                tool_dependence = 1.0
            config.tool_dependence = tool_dependence
            print3(f"Tool Dependence: {tool_dependence}")
        print2("# Tool Auto Selection Threshold. The value of 'tool_auto_selection_threshold' determines the threshold of automatic tool selection.")
        print1("Acceptable range: 0.0 - [the value of tool_dependence]")
        print1("A value of 0.0 indicates that automatic tool selection is disabled. Users must manually choose a tool from the most relevant options identified in each tool search.")
        print1("A value that is equal to or larger than the value of 'tool_dependence' indicates that tool selection is always automatic.")
        print1("A value between 0.0 and the value of 'tool_dependence' indicates that tool selection is only automatic when its value is larger than or equal to the tool search distance. Users need to choose a tool from the most relevant options in case automatic tool selection is not applied and tool search distance is less than or equal to the value of tool_dependence.")
        print2(f"Please enter a value between 0.0 and {config.tool_dependence} to set its value:")
        tool_auto_selection_threshold = self.prompts.simplePrompt(style=self.prompts.promptStyle2, validator=FloatValidator(), default=str(config.tool_auto_selection_threshold))
        if tool_auto_selection_threshold and not tool_auto_selection_threshold.strip().lower() == config.exit_entry:
            tool_auto_selection_threshold = float(tool_auto_selection_threshold)
            if tool_auto_selection_threshold < 0:
                tool_auto_selection_threshold = 0.0
            elif tool_auto_selection_threshold > config.tool_dependence:
                tool_auto_selection_threshold = config.tool_dependence
            config.tool_auto_selection_threshold = tool_auto_selection_threshold
            print3(f"Tool Auto Selection Threshold: {tool_auto_selection_threshold}")
        print2("# Tool Selection Max Choices. The value of 'tool_selection_max_choices' determines the maximum number of available options for manual tool selection.")
        print1("Default value: 4")
        print2("Please enter a number for this value:")
        tool_selection_max_choices = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.tool_selection_max_choices))
        if tool_selection_max_choices and not tool_selection_max_choices.strip().lower() == config.exit_entry:
            config.tool_selection_max_choices = int(tool_selection_max_choices)
            print3(f"Tool Selection Max Choices: {tool_selection_max_choices}")
        config.saveConfig()

    def selectLlmPlatform(self):
        instruction = "Select a platform:"
        print1(instruction)
        options = {
            "llamacpp": "Llama.cpp",
            "llamacppserver": "Llama.cpp server [advanced]",
            "ollama": "Ollama",
            "groq": "Groq [FREE online service]",
            "gemini": "Google Gemini [Paid online service]",
            "chatgpt": "OpenAI ChatGPT [Paid online service]",
            "letmedoit": "LetMeDoIt Mode (powered by ChatGPT)",
        }
        llmInterface = self.dialogs.getValidOptions(
            options=options.keys(),
            descriptions=list(options.values()),
            title="LLM Interface",
            default=config.llmInterface,
            text=instruction,
        )
        if llmInterface:
            config.llmInterface = llmInterface
            if not config.llmInterface == "llamacpp" and hasattr(config, "llamacppMainModel"):
                config.llamacppMainModel = None

    def setLlmModel(self):
        def askAdditionalChatModel() -> bool:
            options = ("yes", "no")
            question = "Do you want an additional model for running chat-only features?"
            print1(question)
            useAdditionalChatModel = self.dialogs.getValidOptions(
                options=options,
                title="Additional Chat Model",
                default="yes" if config.useAdditionalChatModel else "no",
                text=question,
            )
            if useAdditionalChatModel:
                if useAdditionalChatModel == "yes":
                    config.useAdditionalChatModel = True
                    return True
                else:
                    config.useAdditionalChatModel = False
            return False
        def askIntentScreening() -> bool:
            options = ("yes", "no")
            question = "Do you want to check each request to see if a tool is required?"
            print1(question)
            intent_screening = self.dialogs.getValidOptions(
                options=options,
                title="Intent Screening",
                default="yes" if config.intent_screening else "no",
                text=question,
            )
            if intent_screening:
                if intent_screening == "yes":
                    config.intent_screening = True
                    return True
                else:
                    config.intent_screening = False
            return False

        currentLlmInterface = config.llmInterface
        self.selectLlmPlatform()

        print1("Select models ...")
        if config.llmInterface == "ollama":
            print2("# Main Model - for both task execution and conversation")
            self.setLlmModel_ollama()
            askIntentScreening()
            if askAdditionalChatModel():
                print2("# Chat Model - for conversation only")
                self.setLlmModel_ollama("chat")
        elif config.llmInterface == "llamacpp":
            print2("# Main Model - for both task execution and conversation")
            self.setLlmModel_llamacpp()
            askIntentScreening()
            if askAdditionalChatModel():
                print2("# Chat Model - for conversation only")
                self.setLlmModel_llamacpp("chat")
        elif config.llmInterface == "llamacppserver":
            print2("# Main Server - for both task execution and conversation")
            self.setLlmModel_llamacppserver()
            askIntentScreening()
            if askAdditionalChatModel():
                print2("# Chat Server - for conversation only")
                self.setLlmModel_llamacppserver("chat")
            print2("# Vision Server - for vision only")
            self.setLlmModel_llamacppserver("vision")
        elif config.llmInterface == "groq":
            print2("# Main Model - for both task execution and conversation")
            self.setLlmModel_groq()
            askIntentScreening()
            if askAdditionalChatModel():
                print2("# Chat Model - for conversation only")
                self.setLlmModel_groq("chat")
        elif config.llmInterface == "gemini":
            print3("Model selected: Google Gemini Pro")
            askIntentScreening()
        else:
            if config.llmInterface == "chatgpt":
                # intent screening does not apply to letmedoit mode
                askIntentScreening()
            self.setLlmModel_chatgpt()
        config.saveConfig()
        if not config.llmInterface == currentLlmInterface:
            print2("LLM Interface changed! Starting a new chat session ...")
            config.defaultEntry = ".new"
            config.accept_default = True
        CallLLM.checkCompletion()

    def selectOllamaModel(self, message="Select a model from Ollama Library:", feature="default") -> str:
        # history session
        historyFolder = os.path.join(config.localStorage, "history")
        Path(historyFolder).mkdir(parents=True, exist_ok=True)
        model_history = os.path.join(historyFolder, "ollama_chat" if feature == "chat" else "ollama_default")
        model_session = PromptSession(history=FileHistory(model_history))
        completer = FuzzyCompleter(WordCompleter(sorted(ollama_models), ignore_case=True))
        bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}"""
        default = config.ollamaChatModel if feature == "chat" else config.ollamaMainModel
        if config.llmInterface == "llamacpp":
            if feature == "default" and config.llamacppMainModel_ollama_tag:
                default = config.llamacppMainModel_ollama_tag
            elif feature == "chat" and config.llamacppChatModel_ollama_tag:
                default = config.llamacppChatModel_ollama_tag
        # prompt
        print1(message)
        print1("(For details, visit https://ollama.com/library)")
        model = self.prompts.simplePrompt(style=self.prompts.promptStyle2, promptSession=model_session, bottom_toolbar=bottom_toolbar, default=default, completer=completer)
        if model and not model.lower() == config.exit_entry:
            return model
        return ""

    def setLlmModel_ollama(self, feature="default"):
        model = self.selectOllamaModel(feature=feature)
        if model:
            downloadedOllamaModels = getDownloadedOllamaModels()
            if model in downloadedOllamaModels:
                if feature == "default":
                    config.ollamaMainModel = model
                elif feature == "chat":
                    config.ollamaChatModel = model
            else:
                if shutil.which("ollama"):
                    try:
                        Downloader.downloadOllamaModel(model, True)
                        if feature == "default":
                            config.ollamaMainModel = model
                        elif feature == "chat":
                            config.ollamaChatModel = model
                    except:
                        print2(f"Failed to download '{model}'! Please make sure you enter a valid model name or tag.")
                else:
                    print("Ollama not found! Install Ollama first to use Ollama model library!")
                    print("To install Ollama, visit https://ollama.com")

    def setLlmModel_llamacppserver(self, server="tool"):
        def setTimeout(server=server):
            current_timeout = {
                "tool": config.customToolServer_timeout,
                "chat": config.customChatServer_timeout,
                "vision": config.customVisionServer_timeout,
            }
            timeout = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(current_timeout[server]))
            if timeout and not timeout.strip().lower() == config.exit_entry:
                timeout = int(timeout)
                if server=="chat":
                    config.customChatServer_timeout = timeout
                elif server=="vision":
                    config.customVisionServer_timeout = timeout
                else:
                    config.customToolServer_timeout = timeout
                config.saveConfig()
                print3(f"Custom {server} server timeout: {timeout}")
        def setIp(server=server):
            ips = {
                "tool": config.customToolServer_ip,
                "chat": config.customChatServer_ip,
                "vision": config.customVisionServer_ip,
            }
            ip = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=ips[server])
            if ip and not ip.strip().lower() == config.exit_entry:
                if server=="chat":
                    config.customChatServer_ip = ip
                elif server=="vision":
                    config.customVisionServer_ip = ip
                else:
                    config.customToolServer_ip = ip
        def setPort(server=server):
            ports = {
                "tool": config.customToolServer_port,
                "chat": config.customChatServer_port,
                "vision": config.customVisionServer_port,
            }
            port = self.prompts.simplePrompt(numberOnly=True, style=self.prompts.promptStyle2, default=str(ports[server]))
            if port and not port.strip().lower() == config.exit_entry:
                port = int(port)
                if server=="chat":
                    config.customChatServer_port = port
                elif server=="vision":
                    config.customVisionServer_port = port
                else:
                    config.customToolServer_port = port
        def setCommand(server=server):
            commands = {
                "tool": config.customToolServer_command,
                "chat": config.customChatServer_command,
                "vision": config.customVisionServer_command,
            }
            command = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=commands[server])
            if command == "" or (command and not command.strip().lower() == config.exit_entry):
                # allow empty string to use built-in server
                if server=="chat":
                    config.customChatServer_command = command
                elif server=="vision":
                    config.customVisionServer_command = command
                else:
                    config.customToolServer_command = command
                return command
            return None
        print2(f"Enter full custom {server} server command line below:")
        print1("(or leave it blank to use built-in or remote llama.cpp server)")
        command = setCommand()
        print2(f"Enter custom {server} server IP address below:")
        setIp()
        print2(f"Enter custom {server} server port below:")
        setPort()
        if command:
            # timeout option does not apply to built-in server
            print2(f"Enter custom {server} server read/write timeout in seconds below:")
            setTimeout()
        # try to start server
        if server in ("tool", "chat"):
            runFreeGeniusCommand(f"custom{server}server")

    def setLlmModel_llamacpp(self, feature="default"):
        library = self.dialogs.getValidOptions(
            options=("Downloaded GGUF Files", "Ollama Library", "Custom"),
            title="Model Library",
            default="Downloaded GGUF Files",
            text="Select a model library:",
        )
        if library:
            if library == "Ollama Library":
                model = self.selectOllamaModel(feature=feature)
                if model:
                    downloadedOllamaModels = getDownloadedOllamaModels()
                    if model in downloadedOllamaModels:
                        if feature == "default":
                            config.llamacppMainModel_model_path = downloadedOllamaModels[model]
                        elif feature == "chat":
                            config.llamacppChatModel_model_path = downloadedOllamaModels[model]
                    else:
                        if shutil.which("ollama"):
                            try:
                                Downloader.downloadOllamaModel(model, True)
                                model_name = model.replace(":latest", "")
                                try:
                                    exportOllamaModels([model_name])
                                    llm_directory = os.path.join(config.localStorage, "LLMs", "gguf")
                                    model_path = os.path.join(llm_directory, f"{model_name}.gguf")
                                except:
                                    downloadedOllamaModels = getDownloadedOllamaModels()
                                    model_path = downloadedOllamaModels[model]
                                # refresh download list
                                
                                if feature == "default":
                                    config.llamacppMainModel_model_path = model_path
                                elif feature == "chat":
                                    config.llamacppChatModel_model_path = model_path
                            except:
                                print2(f"Failed to download '{model}'! Please make sure you enter a valid model name or tag.")
                        else:
                            print("Ollama not found! Install Ollama first to use Ollama model library!")
                            print("To install Ollama, visit https://ollama.com")
                    if feature == "default":
                        config.llamacppMainModel_ollama_tag = model
                    elif feature == "chat":
                        config.llamacppChatModel_ollama_tag = model
            elif library == "Downloaded GGUF Files":
                downloadedGgufModels = getDownloadedGgufModels()
                if not downloadedGgufModels:
                    self.setCustomHuggingfaceModel(feature=feature)
                else:
                    model = self.dialogs.getValidOptions(
                        options=list(downloadedGgufModels.keys()) + ["Others ..."],
                        title=library,
                        #default="" if ... else "",
                        text="Select a GGUF model:",
                    )
                    if model:
                        if model == "Others ...":
                            self.setCustomHuggingfaceModel(feature=feature)
                        elif feature == "default":
                            config.llamacppMainModel_model_path = downloadedGgufModels[model]
                        elif feature == "chat":
                            config.llamacppChatModel_model_path = downloadedGgufModels[model]
            elif library == "Custom":
                self.setCustomModelPath(feature=feature)

    def setCustomModelPath(self, feature="default"):
        model_path = self.getPath.getFilePath(
            check_isfile=True,
            empty_to_cancel=True,
            list_content_on_directory_change=True,
            keep_startup_directory=True,
            message="Enter a custom model path:",
            default=config.llamacppChatModel_model_path if feature == "chat" else config.llamacppMainModel_model_path,
        )
        if model_path and os.path.isfile(model_path):
            if feature == "default":
                config.llamacppMainModel_model_path = model_path
            elif feature == "chat":
                config.llamacppChatModel_model_path = model_path

    def setCustomHuggingfaceModel(self, feature="default"):
        historyFolder = os.path.join(config.localStorage, "history")
        Path(historyFolder).mkdir(parents=True, exist_ok=True)
        repo_id_history = os.path.join(historyFolder, "llamacpp_chat_repo_id" if feature == "chat" else "llamacpp_main_repo_id")
        repo_id_session = PromptSession(history=FileHistory(repo_id_history))
        filename_history = os.path.join(historyFolder, "llamacpp_chat_filename" if feature == "chat" else "llamacpp_main_filename")
        filename_session = PromptSession(history=FileHistory(filename_history))
        bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}"""
        print1("Please specify the huggingface repo id of a *.gguf model:")
        repo_id = self.prompts.simplePrompt(style=self.prompts.promptStyle2, promptSession=repo_id_session, bottom_toolbar=bottom_toolbar, default=config.llamacppChatModel_repo_id if feature == "chat" else config.llamacppMainModel_repo_id)
        print2("Please specify a filename or glob pattern to match the model file in the repo:")
        filename = self.prompts.simplePrompt(style=self.prompts.promptStyle2, promptSession=filename_session, bottom_toolbar=bottom_toolbar, default=config.llamacppChatModel_filename if feature == "chat" else config.llamacppMainModel_filename)
        if (repo_id and not repo_id.lower() == config.exit_entry) and (filename and not filename.lower() == config.exit_entry):
            if feature == "default":
                config.llamacppMainModel_repo_id = repo_id
                config.llamacppMainModel_filename = filename
                config.llamacppMainModel_model_path = ""
            elif feature == "chat":
                config.llamacppChatModel_repo_id = repo_id
                config.llamacppChatModel_filename = filename
                config.llamacppChatModel_model_path = ""
            CallLLM.checkCompletion()
        else:
            print2("Action cancelled due to insufficient information!")

    def setLlmModel_groq(self, feature="default"):
        model = self.dialogs.getValidOptions(
            options=(
                "mixtral-8x7b-32768",
                "gemma-7b-it",
                "llama3-8b-8192",
                "llama3-70b-8192",
            ),
            title="Groq Model",
            default=config.groqApi_chat_model if feature == "chat" else config.groqApi_main_model,
            text="Select a function call model:\n(for both chat and task execution)",
        )
        if model:
            if feature == "default":
                config.groqApi_main_model = model
            elif feature == "chat":
                config.groqApi_chat_model = model
            print3(f"Groq model: {model}")

    def setLlmModel_chatgpt(self):
        model = self.dialogs.getValidOptions(
            options=self.models,
            title="ChatGPT Model",
            default=config.chatGPTApiModel if config.chatGPTApiModel in self.models else self.models[0],
            text="Select a function call model:\n(for both chat and task execution)",
        )
        if model:
            config.chatGPTApiModel = model
            print3(f"ChatGPT model: {model}")
            # set max tokens
            config.chatGPTApiMaxTokens = self.getMaxTokens()[-1]
            print3(f"Maximum output tokens: {config.chatGPTApiMaxTokens}")

    def setChatbot(self):
        model = self.dialogs.getValidOptions(
            options=("chatgpt", "geminipro", "palm2", "codey"),
            title="Chat-only model",
            default=config.chatbot,
            text="Select default chat-only model:\n(Default model is loaded when you include '[CHAT]' in your input)",
        )
        if model:
            config.chatbot = model
            print3(f"Chat-only model: {model}")

    def setEmbeddingModel(self):
        oldEmbeddingModel = config.embeddingModel
        model = self.dialogs.getValidOptions(
            options=("text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002", "paraphrase-multilingual-mpnet-base-v2", "all-mpnet-base-v2", "all-MiniLM-L6-v2", "custom"),
            title="Embedding model",
            default=config.embeddingModel,
            text="Select an embedding model:",
        )
        if model:
            if model == "custom":
                print1("Enter OpenAI or Sentence Transformer Embedding model:")
                print1("Read more at: https://www.sbert.net/docs/pretrained_models.html")
                customModel = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.embeddingModel)
                if customModel and not customModel.strip().lower() == config.exit_entry:
                    config.embeddingModel = customModel 
            else:
                config.embeddingModel = model
            print3(f"Embedding model: {model}")
        if not oldEmbeddingModel == config.embeddingModel:
            print1(f"You've change the embedding model from '{oldEmbeddingModel}' to '{config.embeddingModel}'.")
            print1("To work with the newly selected model, previous memory store and retrieved collections need to be deleted.")
            print1("Do you want to delete them now? [y]es / [N]o")
            confirmation = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default="yes")
            if confirmation.lower() in ("y", "yes"):
                memory_store = os.path.join(config.localStorage, "memory")
                retrieved_collections = os.path.join(config.localStorage, "autogen", "retriever")
                for folder in (memory_store, retrieved_collections):
                    shutil.rmtree(folder, ignore_errors=True)
            else:
                print1(f"Do you want to change back the embedding model from '{config.embeddingModel}' to '{oldEmbeddingModel}'? [y]es / [N]o")
                confirmation = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default="yes")
                if not confirmation.lower() in ("y", "yes"):
                    config.embeddingModel = oldEmbeddingModel
                    print3(f"Embedding model: {oldEmbeddingModel}")
        if not oldEmbeddingModel == config.embeddingModel:
            config.saveConfig()

    def setAutoGenBuilderConfig(self):
        if not config.isTermux:
            AutoGenBuilder().promptConfig()

    def setAssistantName(self):
        print1("You may modify my name below:")
        freeGeniusAIName = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.freeGeniusAIName)
        if freeGeniusAIName and not freeGeniusAIName.strip().lower() == config.exit_entry:
            config.freeGeniusAIName = freeGeniusAIName
            config.localStorage = getLocalStorage()
            config.saveConfig()
            print3(f"You have changed my name to: {config.freeGeniusAIName}")

    def setCustomSystemMessage(self):
        print1("You can modify the system message to furnish me with details about my capabilities, constraints, or any pertinent context that may inform our interactions. This will guide me in managing and responding to your requests appropriately.")
        print1("Please note that altering my system message directly affects my functionality. Handle with care.")
        print1("Enter custom system message below:")
        print1(f"(Keep it blank to use {config.freeGeniusAIName} default system message.)")
        message = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.systemMessage_letmedoit)
        if message and not message.strip().lower() == config.exit_entry:
            config.systemMessage_letmedoit = message
            config.saveConfig()
            print3(f"Custom system message: {config.freeGeniusAIName}")

    def setCustomTextEditor(self):
        print1("Please specify custom text editor command below:")
        print1("e.g. 'micro -softwrap true -wordwrap true'")
        print1("Leave it blank to use our built-in text editor 'eTextEdit' by default.")
        customTextEditor = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.customTextEditor)
        if customTextEditor and not customTextEditor.strip().lower() == config.exit_entry:
            textEditor = re.sub(" .*?$", "", customTextEditor)
            if not textEditor or not isCommandInstalled(textEditor):
                print2("Command not found on your device!")
            else:
                config.customTextEditor = customTextEditor
                config.saveConfig()
                print3(f"Custom text editor: {config.customTextEditor}")

    def setChatRecordClosestMatches(self):
        print1("Please specify the number of closest matches in each memory retrieval:")
        chatRecordClosestMatches = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.chatRecordClosestMatches))
        if chatRecordClosestMatches and not chatRecordClosestMatches.strip().lower() == config.exit_entry and int(chatRecordClosestMatches) >= 0:
            config.chatRecordClosestMatches = int(chatRecordClosestMatches)
            config.saveConfig()
            print3(f"Number of memory closest matches: {config.chatRecordClosestMatches}")

    def setMemoryClosestMatches(self):
        print1("Please specify the number of closest matches in each memory retrieval:")
        memoryClosestMatches = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.memoryClosestMatches))
        if memoryClosestMatches and not memoryClosestMatches.strip().lower() == config.exit_entry and int(memoryClosestMatches) >= 0:
            config.memoryClosestMatches = int(memoryClosestMatches)
            config.saveConfig()
            print3(f"Number of memory closest matches: {config.memoryClosestMatches}")

    def setMaxAutoCorrect(self):
        print1(f"The auto-correction feature enables {config.freeGeniusAIName} to automatically fix broken Python code if it was not executed properly.")
        print1("Please specify maximum number of auto-correction attempts below:")
        print1("(Remarks: Enter '0' if you want to disable auto-correction feature)")
        maxAutoCorrect = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.max_consecutive_auto_correction))
        if maxAutoCorrect and not maxAutoCorrect.strip().lower() == config.exit_entry and int(maxAutoCorrect) >= 0:
            config.max_consecutive_auto_correction = int(maxAutoCorrect)
            config.saveConfig()
            print3(f"Maximum consecutive auto-correction: {config.max_consecutive_auto_correction}")

    def setMinTokens(self):
        print1("Please specify minimum output tokens below:")
        print1("(applicable to 'chatgpt' and 'letmedoit' interfaces only)")
        mintokens = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.chatGPTApiMinTokens))
        if mintokens and not mintokens.strip().lower() == config.exit_entry and int(mintokens) > 0:
            config.chatGPTApiMinTokens = int(mintokens)
            if config.chatGPTApiMinTokens > config.chatGPTApiMaxTokens:
                config.chatGPTApiMinTokens = config.chatGPTApiMaxTokens
            config.saveConfig()
            print3(f"Minimum output tokens: {config.chatGPTApiMinTokens}")

    def getMaxTokens(self):
        contextWindowLimit = tokenLimits[config.chatGPTApiModel]
        functionTokens = count_tokens_from_functions(config.toolFunctionSchemas.values())
        maxToken = contextWindowLimit - functionTokens - config.chatGPTApiMinTokens
        if maxToken > 4096 and config.chatGPTApiModel in (
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-4-0125-preview",
            "gpt-4-1106-preview",
            "gpt-3.5-turbo",
        ):
            maxToken = 4096
        return contextWindowLimit, functionTokens, maxToken

    def setMaxTokens_non_chatgpt(self):
        print1("Please specify maximum output tokens below:")
        if config.llmInterface == "gemini":
            default = config.geminipro_max_output_tokens
        elif config.llmInterface == "llamacpp":
            default = config.llamacppMainModel_max_tokens
        elif config.llmInterface == "ollama":
            default = config.ollamaMainModel_num_predict
        elif config.llmInterface == "groq":
            default = config.groqApi_max_tokens
        maxtokens = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(default))
        if maxtokens and not maxtokens.strip().lower() == config.exit_entry and int(maxtokens) > 0:
            maxtokens = int(maxtokens)
            if config.llmInterface == "gemini":
                config.geminipro_max_output_tokens = maxtokens
            elif config.llmInterface == "llamacpp":
                config.llamacppMainModel_max_tokens = maxtokens
            elif config.llmInterface == "ollama":
                config.ollamaMainModel_num_predict = maxtokens
            elif config.llmInterface == "groq":
                config.groqApi_max_tokens = maxtokens
            config.saveConfig()
            print3(f"Maximum output tokens: {maxtokens}")

    def setMaxTokens(self):
        # non-chatgpt settings
        if not config.llmInterface in ("chatgpt", "letmedoit"):
            self.setMaxTokens_non_chatgpt()
            return None
        # chatgpt settings
        contextWindowLimit, functionTokens, tokenLimit = self.getMaxTokens()
        if tokenLimit < config.chatGPTApiMinTokens:
            print2(f"Function tokens [{functionTokens}] exceed {config.chatGPTApiModel} output token limit.")
            print1("Either change to a model with higher token limit or disable unused function-call plguins.")
        else:
            print1(self.divider)
            print1("GPT and embeddings models process text in chunks called tokens. As a rough rule of thumb, 1 token is approximately 4 characters or 0.75 words for English text. One limitation to keep in mind is that for a GPT model the prompt and the generated output combined must be no more than the model's maximum context length.")
            print3(f"Current GPT model: {config.chatGPTApiModel}")
            print3(f"Maximum context length: {contextWindowLimit}")
            print3(f"Current function tokens: {functionTokens}")
            print3(f"Maximum output token allowed (excl. functions): {tokenLimit}")
            print1(self.divider)
            print1("Please specify maximum output tokens below:")
            maxtokens = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.chatGPTApiMaxTokens))
            if maxtokens and not maxtokens.strip().lower() == config.exit_entry and int(maxtokens) > 0:
                config.chatGPTApiMaxTokens = int(maxtokens)
                if config.chatGPTApiMaxTokens > tokenLimit:
                    config.chatGPTApiMaxTokens = tokenLimit
                config.saveConfig()
                print3(f"Maximum output tokens: {config.chatGPTApiMaxTokens}")

    def runSystemCommand(self, command):
        command = command.strip()[1:]
        if "\n" in command:
            command = ";".join(command.split("\n"))
        if config.thisPlatform == "Windows":
            os.system(command)
        else:
            os.system(f"env QT_QPA_PLATFORM_PLUGIN_PATH='{config.env_QT_QPA_PLATFORM_PLUGIN_PATH}' {command}")

    def toggleMultiline(self):
        config.multilineInput = not config.multilineInput
        run_in_terminal(lambda: print1(f"Multi-line input {'enabled' if config.multilineInput else 'disabled'}!"))
        if config.multilineInput:
            run_in_terminal(lambda: print1("Use 'escape + enter' to complete your entry."))

    def isTtsAvailable(self):
        if not config.isVlcPlayerInstalled and not config.isPygameInstalled and not config.ttsCommand and not config.elevenlabsApi:
            print2("Text-to-speech feature is not enabled!")
            print3("Read: https://github.com/eliranwong/letmedoit/wiki/letMeDoIt-Speaks")
            config.tts = False
        else:
            config.tts = True
        return config.tts

    def defineTtsCommand(self):
        print1("Define custom text-to-speech command below:")
        print1("""* on macOS ['say -v "?"' to check voices], e.g.:\n'say' or 'say -r 200 -v Daniel'""")
        print1("* on Ubuntu ['espeak --voices' to check voices], e.g.:\n'espeak' or 'espeak -s 175 -v en-gb'")
        print1("* on Windows, simply enter 'windows' here to use Windows built-in speech engine") # letmedoit.ai will handle the command for Windows users
        print1("remarks: always place the voice option, if any, at the end")
        ttsCommand = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.ttsCommand)
        if ttsCommand:
            print1("Specify command suffix below, if any [leave it blank if N/A]:")
            ttsCommandSuffix = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.ttsCommandSuffix)
            if ttsCommand.lower() == "windows":
                command = f'''PowerShell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('testing');"'''
                ttsCommandSuffix = ""
            else:
                command = f'''{ttsCommand} "testing"{ttsCommandSuffix}'''
            _, stdErr = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            if stdErr:
                showErrors() if config.developer else print1("Entered command invalid!")
            else:
                config.ttsCommand, config.ttsCommandSuffix = ttsCommand, ttsCommandSuffix
                config.saveConfig()
        else:
            config.ttsCommand, config.ttsCommandSuffix = "", ""

    def toggleWordWrap(self):
        config.wrapWords = not config.wrapWords
        config.saveConfig()
        print3(f"Word Wrap: '{'enabled' if config.wrapWords else 'disabled'}'!")

    def toggleMouseSupport(self):
        config.mouseSupport = not config.mouseSupport
        config.saveConfig()
        print3(f"Entry Mouse Support: '{'enabled' if config.mouseSupport else 'disabled'}'!")

    def toggleImprovedWriting(self):
        config.displayImprovedWriting = not config.displayImprovedWriting
        if config.displayImprovedWriting:
            print1("Please specify the writing style below:")
            style = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.improvedWritingSytle)
            if style and not style in (config.exit_entry, config.cancel_entry):
                config.improvedWritingSytle = style
                config.saveConfig()
        print3(f"Improved Writing Display: '{'enabled' if config.displayImprovedWriting else 'disabled'}'!")

    def setAudioPlaybackTool(self):
        playback = self.dialogs.getValidOptions(
            options=("pygame", "vlc"),
            descriptions=("PyGame", f"VLC Player (w/ speed control){' [installation required]' if not config.isVlcPlayerInstalled else ''}"),
            title="Text-to-Speech Playback",
            text="Select a text-to-speech plackback tool:",
            default="vlc" if config.isVlcPlayerInstalled and not config.usePygame else "pygame",
        )
        if playback:
            if playback == "vlc":
                if not config.isVlcPlayerInstalled:
                    print1("VLC player not found! Install it first!")
                    print3("Text-to-Speech Playback changed to: PyGame")
                    config.usePygame = True
                else:
                    config.usePygame = False
            else:
                config.usePygame = True

    def setTextToSpeechConfig(self):
        options = ["google", "googlecloud", "elevenlabs", "custom"]
        descriptions = ["Google Text-to-Speech (Generic)", "Google Text-to-Speech (API)", "ElevenLabs (API)", "Custom Text-to-Speech Command [advanced]"]
        if config.thisPlatform == "Linux":
            options.insert(0, "piper")
            descriptions.insert(0, "Piper (Offline; Linux Only)")
        elif config.thisPlatform == "macOS":
            options.insert(0, "say")
            descriptions.insert(0, "Say (Offline; macOS Only)")
        elif config.thisPlatform == "Windows":
            options.insert(0, "wsay")
            descriptions.insert(0, "Wsay (Offline; Windows Only)")
        ttsPlatform = self.dialogs.getValidOptions(
            options=options,
            descriptions=descriptions,
            title="Voice Generation Configurations",
            text="Select a text-to-speech platform:",
            default=config.ttsPlatform,
        )
        if ttsPlatform:
            if ttsPlatform == "googlecloud" and not (os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Text-to-Speech" in config.enabledGoogleAPIs):
                print2("Google Cloud Text-to-Speech feature is not enabled!")
                print3("Read: https://github.com/eliranwong/letmedoit/wiki/Google-API-Setup")
                print3("Text-to-Speech platform changed to: Google Text-to-Speech (Generic)")
                config.ttsPlatform = "google"
            else:
                config.ttsPlatform = ttsPlatform
        # further options
        if config.ttsPlatform == "google":
            self.setGttsLanguage()
            self.setAudioPlaybackTool()
            self.setVlcSpeed()
        elif config.ttsPlatform == "googlecloud":
            self.setGcttsLanguage()
            self.setGcttsSpeed()
            self.setAudioPlaybackTool()
            self.setVlcSpeed()
        elif config.ttsPlatform == "piper":
            if not shutil.which("piper"):
                try:
                    installPipPackage("piper-tts")
                except:
                    pass
            if shutil.which("piper"):
                self.setPiperVoice()
                self.setAudioPlaybackTool()
                self.setVlcSpeed()
            else:
                print2("Command 'piper' not found!")
                print3("Read: https://github.com/eliranwong/freegenius/wiki/Offline-TTS-%E2%80%90-Linux")
        elif config.ttsPlatform == "say":
            self.setSayVoice()
            self.setSaySpeed()
        elif config.ttsPlatform == "wsay":
            homeWsay = os.path.join(config.localStorage, "wsay.exe")
            isWsayFound = (shutil.which("wsay") or os.path.isfile(homeWsay))
            if not isWsayFound:
                print2("Downloading 'wsay.exe' ...")
                downloadFile("https://github.com/p-groarke/wsay/releases/download/1.6.2/wsay.exe", homeWsay)
                isWsayFound = (shutil.which("wsay") or os.path.isfile(homeWsay))
                print3(f"Saved in: {homeWsay}")
            if isWsayFound:
                self.setWsayVoice()
                self.setWsaySpeed()
            else:
                print2("Command 'wsay' not found!")
                print3("Read: https://github.com/eliranwong/freegenius/wiki/Offline-TTS-%E2%80%90-Windows")
        elif config.ttsPlatform == "elevenlabs":
            if not config.elevenlabsApi:
                self.changeElevenlabsApi()
            if not config.elevenlabsApi:
                print1("ElevenLabs API key not found!")
                print3("Text-to-Speech platform changed to: Google Text-to-Speech (Generic)")
                config.ttsPlatform = "google"
            else:
                self.setElevenlabsVoice()
        elif config.ttsPlatform == "custom":
            self.defineTtsCommand()
        # save configs
        config.saveConfig()

    def getWhispercppModel(self):
        llm_directory = os.path.join(config.localStorage, "LLMs", "whisper")
        Path(llm_directory).mkdir(parents=True, exist_ok=True)

        # models that support non-English languages
        models = [
            "ggml-large-v3-q5_0.bin",
            "ggml-large-v3.bin",
            "ggml-large-v2-q5_0.bin",
            "ggml-large-v2.bin",
            "ggml-large-v1.bin",
        ]
        if config.voiceTypingLanguage in ('english', 'en'):
            # English-only models
            english_models = [
                "ggml-medium.en-q5_0.bin",
                "ggml-medium.en.bin",
                "ggml-small.en-q5_1.bin",
                "ggml-small.en.bin",
                "ggml-base.en-q5_1.bin",
                "ggml-base.en.bin",
                "ggml-tiny.en-q8_0.bin",
                "ggml-tiny.en-q5_1.bin",
                "ggml-tiny.en.bin",
            ]
            models = models + english_models

        whispercpp_model = self.dialogs.getValidOptions(
            options=models,
            title="Whisper Models",
            text="Select a whisper model:",
            default=os.path.basename(config.whispercpp_model),
        )

        if not whispercpp_model:
            whispercpp_model = models[0]

        if whispercpp_model:
            print3(f"Whisper model: {whispercpp_model}")
            whispercpp_model_path = os.path.join(llm_directory, whispercpp_model)
            if os.path.isfile(whispercpp_model_path):
                return whispercpp_model_path
            else:
                try:
                    hf_hub_download(
                        repo_id="ggerganov/whisper.cpp",
                        filename=whispercpp_model,
                        local_dir=llm_directory,
                    )
                    return whispercpp_model_path
                except:
                    print3(f"Failed to download: {whispercpp_model}")
                    return ""
        return ""

    def setWhispercppMain(self):
        try:
            whispercpp_main = self.getPath.getFilePath(
                check_isfile=True,
                empty_to_cancel=True,
                list_content_on_directory_change=True,
                keep_startup_directory=True,
                message=f"{self.divider}\nEnter the path of the whisper.cpp main file:",
                default=config.whispercpp_main,
            )
        except:
            print2(f"Given path not accessible!")
            whispercpp_main = ""
        if whispercpp_main:
            whispercpp_main = os.path.expanduser(whispercpp_main)
            if os.path.isfile(whispercpp_main):
                config.whispercpp_main = whispercpp_main
                print3(f"Whisper.cpp main file: {whispercpp_main}")
            else:
                print2("Given path invalid!")

    def setSpeechToTextConfig(self):
        voiceTypingPlatform = self.dialogs.getValidOptions(
            options=("google", "googlecloud", "whisper", "whispercpp"),
            descriptions=("Google Speech-to-Text (Generic) [online]", "Google Speech-to-Text (API) [online]", "OpenAI Whisper [offline; slower with non-English voices]", "Whisper.cpp [offline; installed separately]"),
            title="Voice Recognition Configurations",
            text="Select a speech-to-text platform:",
            default=config.voiceTypingPlatform,
        )
        if voiceTypingPlatform:
            if voiceTypingPlatform == "googlecloud" and not (os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Speech-to-Text" in config.enabledGoogleAPIs):
                print2("Google Cloud Speech-to-Text feature is not enabled!")
                print3("Read: https://github.com/eliranwong/letmedoit/wiki/Google-API-Setup")
                print3("Speech-to-Text platform changed to: Google Speech-to-Text (Generic)")
                config.voiceTypingPlatform = "google"
            elif voiceTypingPlatform == "whisper" and not isCommandInstalled("ffmpeg"):
                print2("Install 'ffmpeg' first to use offline openai whisper model!")
                print3("Read: https://github.com/openai/whisper#setup")
                print3("Speech-to-Text platform changed to: Google Speech-to-Text (Generic)")
                config.voiceTypingPlatform = "google"
            elif voiceTypingPlatform == "whispercpp":
                # check cli main path
                self.setWhispercppMain()
                if os.path.isfile(config.whispercpp_main):
                    config.voiceTypingPlatform = "whispercpp"
                else:
                    config.voiceTypingPlatform = "google"
            else:
                config.voiceTypingPlatform = voiceTypingPlatform
        # language
        self.setSpeechToTextLanguage()
        # whisper.cpp models
        if config.voiceTypingPlatform == "whispercpp":
            whispercpp_model = self.getWhispercppModel()
            if whispercpp_model:
                config.whispercpp_model = whispercpp_model
            else:
                config.voiceTypingPlatform = "google"
        # configure config.voiceTypingAdjustAmbientNoise
        voiceTypingAdjustAmbientNoise = self.dialogs.getValidOptions(
            options=("Yes", "No"),
            descriptions=("Yes [slower]", "No"),
            title="Adjust Ambient Noise",
            text="Do you want to adjust ambient noise?",
            default="Yes" if config.voiceTypingAdjustAmbientNoise else "No",
        )
        if voiceTypingAdjustAmbientNoise:
            config.voiceTypingAdjustAmbientNoise = True if voiceTypingAdjustAmbientNoise == "Yes" else False
        # audio notification
        voiceTypingNotification = self.dialogs.getValidOptions(
            options=("Yes", "No"),
            title="Audio Notification",
            text="Do you want audio notification when you use microphone?",
            default="Yes" if config.voiceTypingNotification else "No",
        )
        if voiceTypingNotification:
            config.voiceTypingNotification = True if voiceTypingNotification == "Yes" else False
        # auto completion: voiceTypingAutoComplete
        voiceTypingAutoComplete = self.dialogs.getValidOptions(
            options=("Yes", "No"),
            title="Audio Entry Auto Completion",
            text="Do you want to automatically complete your entry when microphone stops?",
            default="Yes" if config.voiceTypingAutoComplete else "No",
        )
        if voiceTypingAutoComplete:
            config.voiceTypingAutoComplete = True if voiceTypingAutoComplete == "Yes" else False
        # notify
        print("")
        print3(f"Speech-to-Text Model: {config.voiceTypingPlatform}")
        print3(f"Speech-to-Text Language: {config.voiceTypingLanguage}")
        print3(f"Ambient Noise Adjustment: {config.voiceTypingAdjustAmbientNoise}")
        print3(f"Audio Notification: {config.voiceTypingNotification}")
        print3(f"Auto Completion: {config.voiceTypingAutoComplete}")
        # save configs
        config.saveConfig()

    def saveChat(self, messages):
        messagesCopy = copy.deepcopy(messages)

        if config.conversationStarted:
            timestamp = getCurrentDateTime()

            if hasattr(config, "save_chat_record"):
                # when plugin "save chat records" is enabled
                messageLength = len(messagesCopy)
                for order, i in enumerate(messagesCopy):
                    isLastItem = (order == (messageLength - 1))
                    if config.llmInterface in ("chatgpt", "letmedoit", "groq", "llamacppserver") and not isLastItem and i.get("role", "") == "user" and "function_call" in messagesCopy[order+1]:
                        i["tool"] = messagesCopy[order+1]["function_call"].get("name", "")
                    config.save_chat_record(timestamp, order, i)

            try:
                folderPath = os.path.join(config.localStorage, "chats", re.sub("^([0-9]+?\-[0-9]+?)\-.*?$", r"\1", timestamp))
                Path(folderPath).mkdir(parents=True, exist_ok=True)
                if os.path.isdir(folderPath):
                    chatFile = os.path.join(folderPath, f"{timestamp}.txt")
                    with open(chatFile, "w", encoding="utf-8") as fileObj:
                        fileObj.write(pprint.pformat(messagesCopy))
            except:
                print2("Failed to save chat!\n")
                showErrors()

    def exportChat(self, messages, openFile=True):
        if config.conversationStarted:
            plainText = ""
            timestamp = getCurrentDateTime()

            for i in messages:
                if i["role"] == "user":
                    content = i["content"]
                    plainText += f">>> {content}"
                if i["role"] == "function":
                    if plainText:
                        plainText += "\n\n"
                    name = i["name"]
                    plainText += f"```\n{name}\n```"
                    content = i["content"]
                    plainText += f"\n\n{content}\n\n"
                elif i["role"] == "assistant":
                    content = i["content"]
                    if content is not None:
                        if plainText:
                            plainText += "\n\n"
                        plainText += f"{content}\n\n"
            plainText = plainText.strip()
            if config.terminalEnableTermuxAPI:
                pydoc.pipepager(plainText, cmd="termux-share -a send")
            else:
                try:
                    folderPath = os.path.join(config.localStorage, "chats", "export")
                    Path(folderPath).mkdir(parents=True, exist_ok=True)
                    if os.path.isdir(folderPath):
                        chatFile = os.path.join(folderPath, f"{timestamp}.txt")
                        with open(chatFile, "w", encoding="utf-8") as fileObj:
                            fileObj.write(plainText)
                        if openFile and os.path.isfile(chatFile):
                            os.system(f'''{config.open} "{chatFile}"''')
                except:
                    print2("Failed to save chat!\n")
                    showErrors()

    def runInstruction(self):
        instructions = list(config.predefinedInstructions.keys())
        instruction = self.dialogs.getValidOptions(
            options=instructions,
            title="Predefined Instructions",
            text="Select an instruction:",
        )
        if instruction:
            config.defaultEntry = config.predefinedInstructions[instruction]
            config.accept_default = True

    def changeContext(self):
        contexts = list(config.predefinedContexts.keys())
        predefinedContext = self.dialogs.getValidOptions(
            options=contexts,
            title="Predefined Contexts",
            default=config.predefinedContext,
            text="Select a context:",
        )
        if predefinedContext:
            config.predefinedContext = predefinedContext
            if config.predefinedContext == "[custom]":
                print1("Edit custom context below:")
                customContext = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.customPredefinedContext)
                if customContext and not customContext.strip().lower() == config.exit_entry:
                    config.customPredefinedContext = customContext.strip()
        else:
            # a way to quickly clean up context
            config.predefinedContext = "[none]"
        config.saveConfig()
        self.showCurrentContext()

    def getDirectoryList(self):
        directoryList = []
        for f in os.listdir('.'):
            if os.path.isdir(f):
                separator = "\\" if config.thisPlatform == "Windows" else "/"
                directoryList.append(f"{f}{separator}")
            elif os.path.isfile(f):
                directoryList.append(f)
        return directoryList

    def showLogo(self):
        appName = config.appName if config.appName else config.freeGeniusAIName.split()[0].upper()
        terminal_width = shutil.get_terminal_size().columns
        try:
            from art import text2art
            if terminal_width >= 32:
                logo = text2art(appName, font=config.text2art_font1)
            elif terminal_width >= 20:
                logo = text2art(" ".join(appName) + " ", font=config.text2art_font2)
            else:
                logo = config.freeGeniusAIName
            logo = logo[:-1] # remove the linebreak at the end
        except:
            logo = config.freeGeniusAIName
        print_formatted_text(HTML(f"<{config.terminalCommandEntryColor2}>{logo}</{config.terminalCommandEntryColor2}>"))

    def runPythonScript(self, script):
        script = script.strip()[3:-3]
        try:
            exec(script, globals())
        except:
            trace = traceback.format_exc()
            print(trace if config.developer else "Error encountered!")
            print1(config.divider)
            if config.max_consecutive_auto_correction > 0:
                CallLLM.autoCorrectPythonCode(script, trace)

    def startChats(self):
        tokenValidator = TokenValidator()
        def getDynamicToolBar():
            return config.dynamicToolBarText
        def startChat():
            clear()
            print1(self.divider)
            self.showLogo()
            self.showCurrentContext()
            # go to startup directory
            storagedirectory = config.localStorage
            os.chdir(storagedirectory)
            messages = CallLLM.resetMessages()
            #print1(f"startup directory:\n{storagedirectory}")
            print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Directory:</{config.terminalPromptIndicatorColor2}> {storagedirectory}"))
            print1(self.divider)

            config.conversationStarted = False
            return (storagedirectory, messages)
        storagedirectory, config.currentMessages = startChat()
        config.multilineInput = False
        featuresLower = list(self.actions.keys()) + ["..."]
        # input suggestions
        config.inputSuggestions += featuresLower
        completer = FuzzyCompleter(WordCompleter(config.inputSuggestions, ignore_case=True)) if config.inputSuggestions else None
        completer_developer = FuzzyCompleter(WordCompleter(config.inputSuggestions[:] + [f"config.{i}" for i in dir(config) if not i.startswith("__")] + self.getDirectoryList(), ignore_case=True))
        while True:
            # default toolbar text
            config.dynamicToolBarText = f""" {str(config.hotkey_exit).replace("'", "")} exit {str(config.hotkey_display_key_combo).replace("'", "")} shortcuts """
            # display current directory if changed
            currentDirectory = os.getcwd()
            if not currentDirectory == storagedirectory:
                #print1(self.divider)
                print3(f"Current directory: {currentDirectory}")
                print1(self.divider)
                storagedirectory = currentDirectory
            # default input entry
            accept_default = config.accept_default
            config.accept_default = False
            defaultEntry = config.defaultEntry
            if os.path.isfile(defaultEntry):
                defaultEntry = f'File: "{defaultEntry}"\n'
            elif os.path.isdir(defaultEntry):
                defaultEntry = f'Folder: "{defaultEntry}"\n'
            config.defaultEntry = ""

            # user input
            userInput = self.prompts.simplePrompt(promptSession=self.terminal_chat_session, completer=completer_developer if config.developer else completer, default=defaultEntry, accept_default=accept_default, validator=tokenValidator, bottom_toolbar=getDynamicToolBar)
            
            # update system message when user enter a new input
            config.currentMessages = self.updateSystemMessage(config.currentMessages)
            
            # display options when empty string is entered
            userInputLower = userInput.lower()
            if config.addPathAt is not None:
                prefix = userInput[:config.addPathAt]
                prefixSplit = prefix.rsplit(" ", 1)
                if len(prefixSplit) > 1:
                    default = prefixSplit[-1]
                    prefix = f"{prefixSplit[0]} "
                else:
                    default = prefix
                    prefix = ""
                suffix = userInput[config.addPathAt:]
                config.addPathAt = None
                if not default:
                    default = os.getcwd()
                userPath = self.getPath.getPath(message=f"{prefix}<{config.terminalCommandEntryColor2}>[add a path here]</{config.terminalCommandEntryColor2}>{suffix}", promptIndicator=">>> ", empty_to_cancel=True, default=default)
                config.defaultEntry = f"{prefix}{userPath}{suffix}"
                userInput = ""
            elif not userInputLower:
                userInput = config.blankEntryAction
            if userInput == "...":
                userInput = userInputLower = self.runActions(userInput)
            #elif userInputLower in tuple(self.actions.keys()):
            elif userInputLower.startswith(".") and not userInputLower in (config.exit_entry, config.cancel_entry, ".new", ".context"):
                userInput = userInputLower = self.runActions("...", userInput)

            if setToolDependence(userInput):
                continue

            # replace alias, if any, with full entry
            for alias, fullEntry in config.aliases.items():
                #userInput = re.sub(alias, fullEntry, userInput) # error on Windows coz of Windows path
                userInput = userInput.replace(alias, fullEntry)

            # open file / directory directly
            docs_path = isExistingPath(userInput)
            if os.path.isfile(docs_path):
                os.system(f"{config.open} {docs_path}")
                continue
            elif os.path.isdir(docs_path):
                try:
                    os.chdir(docs_path)
                    print3(f"Directory changed to: {docs_path}")
                    self.getPath.displayDirectoryContent()
                    continue
                except:
                    pass

            # try eval
            if config.developer and not userInput == "...":
                try:
                    value = eval(userInput) # it solve simple math, e.g. 1+1, or read variables, e.g. dir(config)
                    if value is not None:
                        #print(value)
                        pprint.pprint(value)
                        print("")
                        continue
                    elif re.search("^print\([^\)\)]+?\)$", userInput):
                        print("")
                        continue
                except:
                    pass
            # try to run as a python script first
            if config.developer:
                try:
                    exec(userInput, globals())
                    print("")
                    continue
                except:
                    pass

            if userInput.startswith("!"):
                self.runSystemCommand(userInput)
                print("")
            elif config.developer and userInput.startswith("```") and userInput.endswith("```") and not userInput == "``````":
                userInput = re.sub("```python", "```", userInput)
                self.runPythonScript(userInput)
                print("")
            elif userInputLower == config.exit_entry:
                self.saveChat(config.currentMessages)
                return self.exitAction()
            elif userInputLower == config.cancel_entry:
                pass
            elif userInputLower == ".context":
                self.changeContext()
                if not config.applyPredefinedContextAlways:
                    if config.conversationStarted:
                        self.saveChat(config.currentMessages)
                    storagedirectory, config.currentMessages = startChat()
            elif userInputLower == ".new":
                self.saveChat(config.currentMessages)
                storagedirectory, config.currentMessages = startChat()
            elif userInput and not userInputLower in featuresLower:
                try:
                    if userInput and config.ttsInput:
                        TTSUtil.play(userInput)
                    # Feature: improve writing:
                    specialEntryPattern = "\[TOOL_[^\[\]]*?\]|\[NO_TOOL\]|\[NO_SCREENING\]"
                    specialEntry = re.search(specialEntryPattern, userInput)
                    specialEntry = specialEntry.group(0) if specialEntry else ""
                    userInput = re.sub(specialEntryPattern, "", userInput) # remove special entry temporarily
                    if userInput and config.displayImprovedWriting:
                        userInput = re.sub("\n\[Current time: [^\n]*?$", "", userInput)
                        if config.isTermux:
                            day_of_week = ""
                        else:
                            day_of_week = f"today is {getDayOfWeek()} and "
                        improvedVersion = CallLLM.getSingleChatResponse(f"""Improve the following writing, according to {config.improvedWritingSytle}
In addition, I would like you to help me with converting relative dates and times, if any, into exact dates and times based on the reference that {day_of_week}current datetime is {str(datetime.datetime.now())}.
Remember, provide me with the improved writing only, enclosed in triple quotes ``` and without any additional information or comments.
My writing:
{userInput}""")
                        if improvedVersion and improvedVersion.startswith("```") and improvedVersion.endswith("```"):
                            print1(improvedVersion)
                            userInput = improvedVersion[3:-3]
                            if config.ttsOutput:
                                TTSUtil.play(userInput)
                    if specialEntry:
                        userInput = f"{userInput}{specialEntry}"
                    # refine messages before running completion
                    fineTunedUserInput = self.fineTuneUserInput(userInput)
                    # in case of translation
                    if config.predefinedContext == "Let me Translate" and fineTunedUserInput.startswith("Assist me by acting as a translator.\nPlease translate"):
                        print1("Please specify below the language you would like the content to be translated into:")
                        language = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.translateToLanguage)
                        if language and not language.strip().lower() in (config.cancel_entry, config.exit_entry):
                            fineTunedUserInput = f"{fineTunedUserInput}\n\nPlease translate the content into <language>{language}</language>."
                            config.translateToLanguage = language
                        else:
                            continue
                    # clear config.predefinedContextTemp if any
                    if config.predefinedContextTemp:
                        config.predefinedContext = config.predefinedContextTemp
                        config.predefinedContextTemp = ""
                    # empty config.pagerContent
                    config.pagerContent = ""

                    # check special entries
                    # if user call a chatbot without function calling
                    if "[CHAT]" in fineTunedUserInput:
                        chatbot = config.llmInterface
                    elif callChatBot := re.search("\[CHAT_([^\[\]]+?)\]", fineTunedUserInput):
                        chatbot = callChatBot.group(1).lower() if callChatBot and callChatBot.group(1).lower() in ("chatgpt", "geminipro", "palm2", "codey") else ""
                    else:
                        chatbot = ""
                    if chatbot:
                        # call the spcified chatbot to continue the conversation
                        fineTunedUserInput = re.sub("\[CHAT\]|\[CHAT_[^\[\]]+?\]", "", fineTunedUserInput)
                        self.launchChatbot(chatbot, fineTunedUserInput)
                        continue
                    # when user don't want a function call
                    noFunctionCall = ("[NO_TOOL]" in fineTunedUserInput)
                    # when user want to call a particular function
                    checkCallSpecificFunction = re.search("\[TOOL_([^\[\]]+?)\]", fineTunedUserInput)
                    config.selectedTool = checkCallSpecificFunction.group(1) if checkCallSpecificFunction and checkCallSpecificFunction.group(1) in config.toolFunctionMethods else ""
                    if config.developer and config.selectedTool:
                        #print1(f"calling function '{config.selectedTool}' ...")
                        print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Calling function</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{config.selectedTool}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
                    fineTunedUserInput = re.sub(specialEntryPattern, "", fineTunedUserInput)
                    config.currentMessages.append({"role": "user", "content": fineTunedUserInput})

                    # start spinning
                    config.stop_event = threading.Event()
                    config.spinner_thread = threading.Thread(target=spinning_animation, args=(config.stop_event,))
                    config.spinner_thread.start()

                    # force loading internet searches
                    if config.loadingInternetSearches == "always":
                        try:
                            config.currentMessages = CallLLM.runSingleFunctionCall(config.currentMessages, "integrate_google_searches")
                        except:
                            print1("Unable to load internet resources.")
                            showErrors()

                    completion = CallLLM.runGeniusCall(config.currentMessages, noFunctionCall)
                    
                    # stop spinning
                    config.runPython = True
                    stopSpinning()

                    if completion is not None:
                        # Create a new thread for the streaming task
                        streamingWordWrapper = StreamingWordWrapper()
                        streaming_event = threading.Event()
                        self.streaming_thread = threading.Thread(target=streamingWordWrapper.streamOutputs, args=(streaming_event, completion, True if config.llmInterface in ("chatgpt", "letmedoit", "groq", "llamacppserver") else False))
                        # Start the streaming thread
                        self.streaming_thread.start()

                        # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+z' to stop the streaming
                        streamingWordWrapper.keyToStopStreaming(streaming_event)

                        # when streaming is done or when user press "ctrl+q"
                        self.streaming_thread.join()

                # error codes: https://platform.openai.com/docs/guides/error-codes/python-library-error-types
                except openai.APIError as e:
                    stopSpinning()
                    #Handle API error here, e.g. retry or log
                    print1(f"OpenAI API returned an API Error: {e}")
                except openai.APIConnectionError as e:
                    stopSpinning()
                    #Handle connection error here
                    print1(f"Failed to connect to OpenAI API: {e}")
                except openai.RateLimitError as e:
                    stopSpinning()
                    #Handle rate limit error (we recommend using exponential backoff)
                    print1(f"OpenAI API request exceeded rate limit: {e}")
                except:
                    stopSpinning()
                    trace = traceback.format_exc()
                    if "Please reduce the length of the messages or completion" in trace:
                        print1("Maximum tokens reached!")
                    elif config.developer:
                        print1(self.divider)
                        print1(trace)
                        print1(self.divider)
                    else:
                        print1("Error encountered!")

                    config.defaultEntry = userInput
                    print1("starting a new chat!")
                    self.saveChat(config.currentMessages)
                    storagedirectory, config.currentMessages = startChat()

    def launchChatbot(self, chatbot, fineTunedUserInput):
        if not chatbot:
            chatbot = config.llmInterface
        if config.isTermux:
            #chatbot = "chatgpt"
            ...
        chatbots = {
            "llamacpp": lambda: LlamacppChat(model=None if config.useAdditionalChatModel else config.llamacppMainModel).run(fineTunedUserInput),
            "llamacppserver": lambda: LlamacppServerChat().run(fineTunedUserInput),
            "ollama": lambda: OllamaChat().run(fineTunedUserInput, model=config.ollamaChatModel if config.useAdditionalChatModel else config.ollamaMainModel),
            "groq": lambda: GroqChatbot().run(fineTunedUserInput),
            "chatgpt": lambda: ChatGPT().run(fineTunedUserInput),
            "letmedoit": lambda: ChatGPT().run(fineTunedUserInput),
            "gemini": lambda: GeminiPro(temperature=config.llmTemperature).run(fineTunedUserInput),
            "geminipro": lambda: GeminiPro(temperature=config.llmTemperature).run(fineTunedUserInput),
            "palm2": lambda: Palm2().run(fineTunedUserInput, temperature=config.llmTemperature),
            "codey": lambda: Codey().run(fineTunedUserInput, temperature=config.llmTemperature),
        }
        if chatbot in chatbots:
            chatbots[chatbot]()

    def addPagerText(self, text, wrapWords=False):
        if wrapWords:
            text = self.getWrappedHTMLText(text)
        config.pagerContent += f"{text}\n"

    def launchPager(self, pagerContent=None):
        if pagerContent is None:
            pagerContent = config.pagerContent
        if pagerContent:
            try:
                if shutil.which("bat"):
                    # Windows users can install bat command with scoop
                    # read: https://github.com/ScoopInstaller/Scoop
                    # > iwr -useb get.scoop.sh | iex
                    # > scoop install aria2 bat
                    if re.search("<[^<>]+?>", pagerContent):
                        pagerContent = TextUtil.convertHtmlTagToColorama(pagerContent)
                    language = "Python" if "```python" in pagerContent else "Markdown"
                    pydoc.pipepager(pagerContent, cmd=f"bat -l {language} --paging always")
                elif shutil.which("less"):
                    # Windows users can install less command with scoop
                    # read: https://github.com/ScoopInstaller/Scoop
                    # > iwr -useb get.scoop.sh | iex
                    # > scoop install aria2 less
                    if re.search("<[^<>]+?>", pagerContent):
                        pagerContent = TextUtil.convertHtmlTagToColorama(pagerContent)
                    pydoc.pipepager(pagerContent, cmd='less -R')
                else:
                    pydoc.pager(pagerContent)
            except:
                config.pagerView = False
                showErrors()

    # wrap html text at spaces
    def getWrappedHTMLText(self, text, terminal_width=None):
        if not " " in text:
            return text
        if terminal_width is None:
            terminal_width = shutil.get_terminal_size().columns
        self.wrappedText = ""
        self.lineWidth = 0

        def addWords(words):
            words = words.split(" ")
            for index, item in enumerate(words):
                isLastItem = (len(words) - index == 1)
                if is_CJK(item):
                    for iIndex, i in enumerate(item):
                        isSpaceItem = (not isLastItem and (len(item) - iIndex == 1))
                        iWidth = getStringWidth(i)
                        if isSpaceItem:
                            newLineWidth = self.lineWidth + iWidth + 1
                        else:
                            newLineWidth = self.lineWidth + iWidth
                        if newLineWidth > terminal_width:
                            self.wrappedText += f"\n{i} " if isSpaceItem else f"\n{i}"
                            self.lineWidth = iWidth + 1 if isSpaceItem else iWidth
                        else:
                            self.wrappedText += f"{i} " if isSpaceItem else i
                            self.lineWidth += iWidth + 1 if isSpaceItem else iWidth
                else:
                    itemWidth = getStringWidth(item)
                    if isLastItem:
                        newLineWidth = self.lineWidth + itemWidth
                    else:
                        newLineWidth = self.lineWidth + itemWidth + 1
                    if newLineWidth > terminal_width:
                        self.wrappedText += f"\n{item}" if isLastItem else f"\n{item} "
                        self.lineWidth = itemWidth if isLastItem else itemWidth + 1
                    else:
                        self.wrappedText += item if isLastItem else f"{item} "
                        self.lineWidth += itemWidth if isLastItem else itemWidth + 1

        def processLine(lineText):
            if re.search("<[^<>]+?>", lineText):
                # handle html/xml tags
                chunks = lineText.split(">")
                totalChunks = len(chunks)
                for index, chunk in enumerate(chunks):
                    isLastChunk = (totalChunks - index == 1)
                    if isLastChunk:
                        addWords(chunk)
                    else:
                        tag = True if "<" in chunk else False
                        if tag:
                            nonTag, tagContent = chunk.rsplit("<", 1)
                            addWords(nonTag)
                            self.wrappedText += f"<{tagContent}>"
                        else:
                            addWords(f"{chunk}>")
            else:
                addWords(lineText)

        lines = text.split("\n")
        totalLines = len(lines)
        for index, line in enumerate(lines):
            isLastLine = (totalLines - index == 1)
            processLine(line)
            if not isLastLine:
                self.wrappedText += "\n"
                self.lineWidth = 0

        return self.wrappedText
