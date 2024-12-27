from toolmate import config, showErrors, getDayOfWeek, getFilenamesWithoutExtension, getStringWidth, stopSpinning, spinning_animation, getLocalStorage, getWebText, getWeather, getCliOutput, refinePath, displayLoadedMessages, removeDuplicatedListItems, getElevenlabsApi_key, getLlms, getFabricPatterns, getFabricPatternSystem
from toolmate import print1, print2, print3, isCommandInstalled, setChatGPTAPIkey, count_tokens_from_functions, chatgptTokenLimits, toggleinputaudio, toggleoutputaudio, downloadFile, getUserPreviousRequest, getAssistantPreviousResponse, readTextFile, writeTextFile, wrapText, refineToolTextOutput, getPromptExecutionMessage
from toolmate import installPipPackage, exportOllamaModels, getDownloadedGgufModels, extractSystemCommand, extractPythonCode, is_valid_url, getCurrentDateTime, openURL, isExistingPath, is_CJK, exportOllamaModels, runToolMateCommand, displayPythonCode, selectTool, showRisk, confirmExecution, getPythonFunctionResponse
from toolmate.utils.call_llm import CallLLM
import threading, os, traceback, re, subprocess, json, pydoc, shutil, datetime, pprint, copy
import edge_tts, asyncio, requests
import io, sys
from io import StringIO
from flashtext import KeywordProcessor
from typing import Optional
from pathlib import Path
from toolmate.utils.download import Downloader
from toolmate.utils.ollama_models import ollama_models
#from pygments.lexers.python import PythonLexer
#from pygments.lexers.shell import BashLexer
#from pygments.lexers.markup import MarkdownLexer
#from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter, NestedCompleter, ThreadedCompleter
from prompt_toolkit.shortcuts import clear, set_title
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit import print_formatted_text, HTML
from toolmate.utils.terminal_mode_dialogs import TerminalModeDialogs
from toolmate.utils.prompts import Prompts
from toolmate.utils.prompt_validator import FloatValidator, TokenValidator
from toolmate.utils.get_path_prompt import GetPath
from toolmate.utils.prompt_shared_key_bindings import swapTerminalColors

from toolmate.utils.terminal_system_command_prompt import SystemCommandPrompt
from toolmate.utils.tool_plugins import Plugins
from toolmate.utils.tts_utils import TTSUtil
from toolmate.utils.tts_languages import TtsLanguages
from toolmate.utils.streaming_word_wrapper import StreamingWordWrapper
from toolmate.utils.text_utils import TextUtil
from toolmate.utils.sttLanguages import googleSpeeckToTextLanguages, whisperSpeeckToTextLanguages
from toolmate.groqchat import GroqChatbot
from toolmate.mistralchat import MistralChatbot
from toolmate.ollamachat import OllamaChat
from elevenlabs.client import ElevenLabs
if not config.isLite:
    from toolmate.chatgpt import ChatGPT
    from toolmate.llamacpp import LlamacppChat
    from toolmate.llamacppserver import LlamacppServerChat
    from toolmate.autobuild import AutoGenBuilder
    from toolmate.geminipro import GeminiPro
    from toolmate.palm2 import Palm2
    from toolmate.codey import Codey
    from huggingface_hub import hf_hub_download
    if hasattr(config, "desktopAssistant"):
        from toolmate.gui.worker import QtResponseStreamer


class ToolMate:

    def __init__(self, plugins=True):
        #config.letMeDoItAI = self
        self.prompts = Prompts()
        self.dialogs = TerminalModeDialogs(self)
        self.setup()
        if plugins:
            Plugins.runPlugins()

    def resetMessages(self):
        self.workflow = []
        config.conversationStarted = False
        return CallLLM.resetMessages()

    def loadMessages(self, chatfile: str):
        if chatfile and os.path.isfile(chatfile):
            try:
                config.conversationStarted = True
                unwanted = r"""\|
/
-
\\
"""
                messages = eval(re.sub(f"^{unwanted}", "", readTextFile(chatfile)))
                currentMessages = []
                if isinstance(messages, list):
                    for i in messages:
                        try:
                            role = i.get("role")
                            #content = i.get("content")
                            if role in ("user", "assistant"):
                                currentMessages.append(i)
                        except:
                            pass
            except:
                currentMessages = []
        else:
            currentMessages = []
        return self.resetMessages() + currentMessages

    def setup(self):
        config.currentMessages = self.resetMessages()
        # set up tool store client
        config.divider = self.divider = "--------------------"
        config.runPython = True
        if not hasattr(config, "accept_default"):
            config.accept_default = False
        if not hasattr(config, "defaultEntry"):
            config.defaultEntry = ""
        config.toolTextOutput = "" # temporary placeholder for text content; generated by tool plugin; to be recorded in assistant response in config.currentMessages
        config.tempChatSystemMessage = "" # temporary chat system message
        config.llmTextChunk = "" # temporary placeholder for text chunk; directly generated by LLM; to be read out by TTS utility
        if not hasattr(config, "predefinedContextTemp"):
            config.predefinedContextTemp = ""
        config.systemCommandPromptEntry = ""
        # share the following methods in config so that they are accessible via plugins
        config.toggleMultiline = self.toggleMultiline
        config.getWrappedHTMLText = self.getWrappedHTMLText
        config.addPredefinedContext = self.addPredefinedContext
        config.improveWriting = self.improveWriting
        config.generateSystemCommand = self.generateSystemCommand
        config.convertRelativeDateTime = self.convertRelativeDateTime
        config.launchPager = self.launchPager
        config.changeOpenweathermapApi = self.changeOpenweathermapApi
        config.autoCorrectPythonCode = CallLLM.autoCorrectPythonCode
        config.selectedTool = ""
        config.addToolAt = None
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
        
        if not config.llmInterface or not config.llmInterface in getLlms():
            self.setLlmModel()
        if not config.llmInterface:
            config.llmInterface = "llamacpppython"
            config.saveConfig()

        # check availability of api keys
        if not config.openaiApiKey:
            self.changeChatGPTAPIkey()
        if not config.githubApi_key:
            self.changeGithubAPIkey()
        if not config.azureApi_key:
            self.changeAzureAPIkey()
        if not config.anthropicApi_key:
            self.changeAnthropicAPIkey()
        if not config.googleaiApi_key:
            self.changeGoogleaiApikey()
        if not config.xaiApi_key:
            self.changeXaiApikey()
        if not config.groqApi_key:
            self.changeGroqApi()
        if not config.mistralApi_key:
            self.changeMistralApi()
        if not config.bing_api_key:
            self.changeBingApi()
        if not config.rapid_api_key:
            self.changeRapidApi()
        if not config.openweathermapApi:
            self.changeOpenweathermapApi()
        if not config.elevenlabsApi:
            self.changeElevenlabsApi()
        if not config.tavilyApi_key and not config.isLite:
            self.changeTavilyApi()

        # initial completion check at startup
        if config.initialCompletionCheck:
            if config.llmInterface == "llamacppserver":
                runToolMateCommand("customtoolserver")
                if config.useAdditionalChatModel:
                    runToolMateCommand("customchatserver")
            else:
                CallLLM.checkCompletion()

        chat_history = os.path.join(config.localStorage, "history", "chats")
        self.terminal_chat_session = PromptSession(history=FileHistory(chat_history))

        self.actions = {
            # session
            ".new": (f"start a new conversation {str(config.hotkey_new)}", None),
            ".open": (f"open a saved conversation {str(config.hotkey_open_chat_records)}", None),
            ".last": (f"open previous conversation {str(config.hotkey_open_last_conversation)}", None),
            ".read": (f"read current conversation {str(config.hotkey_read_conversation)}", self.readCurrentMessages),
            ".edit": (f"edit current conversation {str(config.hotkey_edit_last_response)}", self.editCurrentConversation),
            ".trim": (f"trim current conversation", self.trimCurrentConversation),
            ".save": ("save current conversation", lambda: self.saveChat(config.currentMessages)),
            ".saveas": ("save current conversation as ...", lambda: self.saveAsChat(config.currentMessages)),
            ".export": (f"export current conversation {str(config.hotkey_export)}", lambda: self.exportChat(config.currentMessages)),
            
            ".apikeys": ("change API keys", self.changeAPIkeys),
            ".model": ("change AI backends and models", self.setLlmModel),
            #".embedding": ("change embedding model", self.setEmbeddingModel), # joined ".model"
            # inference
            ".contextwindow": ("change context window size", self.setContextWindowSize),
            ".maxtokens": ("change maximum output tokens", self.setMaxTokens),
            #".mintokens": ("change minimum output tokens", self.setMinTokens), # for chatgp and letmedoit only
            #".dynamictokencount": ("change dynamic token count", self.setDynamicTokenCount), # for chatgp and letmedoit only
            ".temperature": ("change output temperature", self.setTemperature),

            ".plugins": ("change plugins", self.selectPlugins),
            ".tools": ("configure tool selection agent", self.setToolSelectionConfigs),
            #".maxautocorrect": ("change maximum consecutive auto-correction", self.setMaxAutoCorrect), # joined ".tools"
            ".managerisk": ("manage code execution risk", self.manageCodeExecutionRisk), # joined ".tools"

            ".context": ("select a predefined context", None),
            #".context": (f"change default context {str(config.hotkey_select_context)}", None),
            #".contextintegration": ("change chat context integration", self.setContextIntegration), # joined ".context"
            ".workflow": ("display current workflow", self.displayCurrentWorkflow),

            #".changeapikey": ("change OpenAI API key", self.changeChatGPTAPIkey), # joined ".apikeys"
            #".openweathermapapi": ("change OpenWeatherMap API key", self.changeOpenweathermapApi), # joined ".apikeys"
            #".elevenlabsapi": ("change ElevenLabs API key", self.changeElevenlabsApi), # joined ".apikeys"
            #".googleapiservice": ("change Google API service", self.selectGoogleAPIs), # joined ".apikeys"
            #".autobuilderconfig": ("change auto builder config", self.setAutoGenConfig), ".apikeys"
            #".termuxapi": ("change Termux API integration", self.setTermuxApi), # joined ".apikeys"
            #".functioncall": ("change function call", self.setFunctionCall),
            #".functioncallintegration": ("change function call integration", self.setFunctionResponse),

            # integration
            ".autogen": ("change autogen configurations", self.setAutoGenConfig),
            ".fabric": ("change fabric configurations", self.setFabricPatternsDirectory),

            # tweak searches
            ".searches": ("change search-related settings", self.changeSearchSettings),
            #".maxmemorymatches": ("change maximum memory matches", self.setMemoryClosestMatches),
            #".maxchatrecordmatches": ("change maximum chat record matches", self.setChatRecordClosestMatches),
            #".maxonlinesearches": ("change maximum online search results", self.setMaximumInternetSearchResults),
            
            # tweak input information
            #".ipinfo": ("change ip information integration", self.setIncludeIpInSystemMessage),
            #".latestSearches": ("change online searches", self.setLatestSearches),
            # tweak output display
            ".codedisplay": ("change code display", self.setCodeDisplay),
            ".pagerview": ("change pager view", self.setPagerView),
            # speech
            ".speechrecognition": ("change sppech recognition", self.setSpeechToTextConfig),
            ".speechgeneration": ("change sppech generation", self.setTextToSpeechConfig),
            # toggle
            ".toggledeveloper": (f"toggle developer mode {str(config.hotkey_toggle_developer_mode)}", self.toggleDeveloperMode),
            ".togglemultiline": (f"toggle multi-line input {str(config.hotkey_toggle_multiline_entry)}", self.toggleMultiline),
            ".togglemousesupport": (f"toogle mouse support {str(config.hotkey_toggle_mouse_support)}", self.toggleMouseSupport),
            ".togglewordwrap": (f"toggle word wrap {str(config.hotkey_toggle_word_wrap)}", self.toggleWordWrap),
            ".toggleinputimprovement": (f"toggle input improvement {str(config.hotkey_toggle_input_improvement)}", self.toggleInputImprovement),
            ".toggleinputaudio": (f"toggle input audio {str(config.hotkey_toggle_input_audio)}", toggleinputaudio),
            ".toggleoutputaudio": (f"toggle output audio {str(config.hotkey_toggle_response_audio)}", toggleoutputaudio),
            ".toggletextbrightness": (f"toggle text brightness", swapTerminalColors),
            #".toggletextbrightness": (f"toggle text brightness {str(config.hotkey_swap_text_brightness)}", swapTerminalColors),
            # editor
            ".editor": ("change custom text editor", self.setCustomTextEditor),
            ".editconfigs": ("edit configuration settings", self.editConfigs),
            # app settings
            ".autoupgrade": ("change automatic upgrade", self.setAutoUpgrade),
            ".favourite": ("change my favourites", self.changeMyFavouries),
            ".assistantname": ("change assistant name", self.setAssistantName),
            #".storagedirectory": ("change storage directory", self.setStorageDirectory),
            ".systemmessage": ("change system messages", self.setCustomSystemMessage),
            # miscellaneous
            ".tms": ("change tms commands", self.setTmsMessages),
            ".tmt": ("change tmt commands", self.setTmtTools),
            ".xonsh": (f"run xonsh {str(config.hotkey_launch_xonsh)}", lambda: os.system("xonsh")),
            #".system": (f"open system command prompt {str(config.hotkey_launch_system_prompt)}", lambda: SystemCommandPrompt().run(allowPathChanges=True)),
            #".install": ("install python package", self.installPythonPackage), # changed to a tool
            ".keys": (f"learn about key entries and bindings {str(config.hotkey_display_key_combo)}", config.showKeyBindings),
            ".help": ("open documentations", lambda: openURL('https://github.com/eliranwong/toolmate/wiki')),
            ".donate": ("donate and support ToolMate AI", lambda: openURL('https://www.paypal.com/paypalme/letmedoitai')),
        }
        if config.terminalEnableTermuxAPI:
            self.actions[".timer"] = ("set timer", lambda: subprocess.Popen("am start -a android.intent.action.SET_TIMER", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
            self.actions[".alarm"] = ("set alarm", lambda: subprocess.Popen("am start -a android.intent.action.SET_ALARM", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
            self.actions[".shareworkflow"] = ("share current workflow", self.shareCurrentWorkflow)

        self.setupItems = [".model", ".systemmessage", ".editconfigs", ".apikeys", ".maxtokens", ".plugins", ".speechgeneration", ".speechrecognition", ".temperature", ".tools", ".managerisk", ".contextwindow", ".editor", ".autogen", ".fabric", ".toggledeveloper", ".togglewordwrap", ".searches", ".tms", ".tmt"]

        config.actionHelp = f"# Quick Actions\n(entries that start with '.')\n"
        for key, value in self.actions.items():
            config.actionHelp += f"{key}: {value[0]}\n"
        config.actionHelp += "\n"
        # action keys
        config.actionKeys = list(self.actions.keys()) + ["..."]

    def changeSearchSettings(self):
        self.setMaximumInternetSearchResults()
        self.setChatRecordClosestMatches()
        self.setMemoryClosestMatches()

    def displayCurrentWorkflow(self):
        for action, description in self.workflow:
            print(f'''@{action} {description}''')

    def getCurrentWorkflow(self):
        workflow = [f'''@{action} {description}''' for action, description in self.workflow]
        return "\n".join(workflow)

    def shareCurrentWorkflow(self):
        pydoc.pipepager(self.getCurrentWorkflow(), cmd="termux-share -a send")

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
        print3("Read: https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Offline%20TTS%20-%20macOS.md#download-more-voices")
        print1("(leave it blank to use the default voice)")
        if not config.say_voice in voices:
            config.say_voice = ""
        option = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.say_voice, promptSession=voice_session, completer=completer)
        if option and not option in (config.exit_entry, config.cancel_entry):
            config.say_voice = re.sub(r" \[[^\]]*?\]$", "", option)
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

    def setVoskModel(self):
        voskModel_history = os.path.join(config.localStorage, "history", "voskModel")
        voskModel_session = PromptSession(history=FileHistory(voskModel_history))
        response = requests.get("https://alphacephei.com/vosk/models/model-list.json", timeout=10)
        models = [model["name"] for model in response.json()]
        completer = FuzzyCompleter(WordCompleter(models, ignore_case=True))
        print1("Please specify a Vosk Model:")
        print1("(Read https://alphacephei.com/vosk/models)")
        option = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.voskModel, promptSession=voskModel_session, completer=completer)
        if option and not option in (config.exit_entry, config.cancel_entry) and option in models:
            config.voskModel = option

    def setAndroidTtsVoice(self):
        # language
        self.setGcttsLanguage()
        # rate
        print1("Please specify the speech rate:")
        androidttsRate = self.prompts.simplePrompt(style=self.prompts.promptStyle2, validator=FloatValidator(), default=str(config.androidttsRate))
        if androidttsRate and not androidttsRate.strip().lower() == config.exit_entry:
            androidttsRate = float(androidttsRate)
            if androidttsRate < 0.1:
                androidttsRate = 0.1
            elif androidttsRate > 2:
                androidttsRate = 2
            config.androidttsRate = round(androidttsRate, 1)

    def setEdgeTtsVoice(self):
        edgettsVoice_history = os.path.join(config.localStorage, "history", "edgettsVoice")
        edgettsVoice_session = PromptSession(history=FileHistory(edgettsVoice_history))
        async def getVoices():
            voices = await edge_tts.list_voices()
            return voices
        voices = asyncio.run(getVoices())
        voices = [voice["ShortName"] for voice in voices if "ShortName" in voice]
        completer = FuzzyCompleter(WordCompleter(voices, ignore_case=True))
        print1("Please specify a Microsoft Server Speech Text to Speech Voice:")
        option = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.edgettsVoice, promptSession=edgettsVoice_session, completer=completer)
        if option and not option in (config.exit_entry, config.cancel_entry) and option in voices:
            config.edgettsVoice = option
        # rate
        print1("Please specify the speech rate:")
        edgettsRate = self.prompts.simplePrompt(style=self.prompts.promptStyle2, validator=FloatValidator(), default=str(config.edgettsRate))
        if edgettsRate and not edgettsRate.strip().lower() == config.exit_entry:
            edgettsRate = float(edgettsRate)
            if edgettsRate < 0.1:
                edgettsRate = 0.1
            elif edgettsRate > 2:
                edgettsRate = 2
            config.edgettsRate = round(edgettsRate, 1)

    # ElevenLabs Text-to-Speech Voice
    def setElevenlabsVoice(self):
        # record in history for easy retrieval by moving arrows upwards / downwards
        elevenlabsVoice_history = os.path.join(config.localStorage, "history", "elevenlabsVoice")
        elevenlabsVoice_session = PromptSession(history=FileHistory(elevenlabsVoice_history))
        # input suggestion for options
        options = {}
        ids = {}
        for voice in list(ElevenLabs(api_key=getElevenlabsApi_key()).voices.get_all())[0][-1]:
            options[voice.name] = voice.voice_id
            ids[voice.voice_id] = voice.name
        # default
        default = ids[config.elevenlabsVoice] if config.elevenlabsVoice in ids else "Rachel"
        # completer
        completer = FuzzyCompleter(WordCompleter(options.keys(), ignore_case=True))
        print1("Please specify a ElevenLabs Text-to-Speech Voice:")
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
        print1("Please specify Text-to-Speech language:")
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

    def setGoogleCredentialsPath(self) -> bool:
        print2("# Google Vertex AI configurations ...")
        print1("Enter your project id below:")
        project_id = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.vertexai_project_id)
        if project_id and not project_id.strip().lower() == config.exit_entry:
            config.genai_project_id = config.vertexai_project_id = project_id
        print1("Enter your service location below:")
        service_location = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.vertexai_service_location)
        if service_location and not service_location.strip().lower() == config.exit_entry:
            config.genai_service_location = config.vertexai_service_location = service_location
        filePath = self.getPath.getFilePath(
            empty_to_cancel=True,
            list_content_on_directory_change=True,
            keep_startup_directory=True,
            message=f"{self.divider}\nEnter the file path of your Google Cloud Credentials:\n(Default: {config.google_cloud_credentials_file})",
            default=config.google_cloud_credentials,
        )
        if filePath and os.path.isfile(filePath):
            config.google_cloud_credentials = filePath
            isCredentialGiven= True
        else:
            print2("Invalid file path given!")
            isCredentialGiven = False
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.google_cloud_credentials if config.google_cloud_credentials and os.path.isfile(config.google_cloud_credentials) else ""
        return isCredentialGiven


    def selectGoogleAPIs(self):
        #if not os.environ["GOOGLE_APPLICATION_CREDENTIALS"]:
        if not self.setGoogleCredentialsPath():
            return None

        if os.environ["GOOGLE_APPLICATION_CREDENTIALS"]:
            enabledGoogleAPIs = self.dialogs.getMultipleSelection(
                title="Google Cloud Service",
                text="Select to enable Google Cloud Service:",
                options=("Vertex AI", "Speech-to-Text", "Text-to-Speech"),
                default_values=config.enabledGoogleAPIs,
            )
            if enabledGoogleAPIs is not None:
                config.enabledGoogleAPIs = enabledGoogleAPIs
        else:
            config.enabledGoogleAPIs = ["Vertex AI"]
            print1(f"API key json file '{config.google_cloud_credentials_file}' not found!")
            print1("Read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Google%20Cloud%20Service%20Credential%20Setup.md for setting up Google API.")
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
        pluginFolder = os.path.join(config.toolMateAIFolder, "plugins")
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
        self.changeMistralApi()
        self.changeGoogleaiApikey()
        self.changeXaiApikey()
        self.changeAnthropicAPIkey()
        self.changeChatGPTAPIkey()
        self.changeGithubAPIkey()
        self.changeAzureAPIkey()
        if not config.isLite:
            self.setAutoGenConfig()
        self.changeBingApi()
        self.changeRapidApi()
        self.changeOpenweathermapApi()
        self.changeElevenlabsApi()
        if not config.isLite:
            self.changeTavilyApi()
            self.selectGoogleAPIs()

    def changeGoogleaiApikey(self):
        print3("# Google AI API Key: allows access to Google AI Studio models")
        print1("To set up Google AI API Key, read:\nhttps://aistudio.google.com/apikey\n")
        print1("Enter your Google AI API Key [optional]:")
        apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.googleaiApi_key, is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            config.googleaiApi_key = config.genaiApi_key = apikey
            CallLLM.checkCompletion("googleai")
        else:
            config.googleaiApi_key = config.genaiApi_key = "toolmate"
        config.saveConfig()
        print2("Configurations updated!")

    def changeXaiApikey(self):
        print3("# X AI API Key: allows access to X AI Studio models")
        print1("To set up X AI API Key, read:\nhttps://x.ai/api\n")
        print1("Enter your X AI API Key [optional]:")
        apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.xaiApi_key, is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            config.xaiApi_key = apikey
            CallLLM.checkCompletion("xai")
        else:
            config.xaiApi_key = "toolmate"
        config.saveConfig()
        print2("Configurations updated!")

    def changeAnthropicAPIkey(self):
        print3("# Anthropic API Key: allows access to Claude models")
        print1("To set up Anthropic API Key, read:\nhttps://www.anthropic.com/api\n")
        print1("Enter your Anthropic API Key [optional]:")
        apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.anthropicApi_key, is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            config.anthropicApi_key = apikey
            CallLLM.checkCompletion("anthropic")
            os.environ["ANTHROPIC_API_KEY"] = config.anthropicApi_key
        else:
            config.anthropicApi_key = "toolmate"
        config.saveConfig()
        print2("Configurations updated!")

    def changeChatGPTAPIkey(self):
        print3("# ChatGPT API Key: allows access to OpenAI models")
        print1("To set up ChatGPT API Key, read:\nhttps://github.com/eliranwong/letmedoit/wiki/ChatGPT-API-Key#how-to-obtain\n")
        print1("Enter your OpenAI API Key [optional]:")
        apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.openaiApiKey, is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            config.openaiApiKey = apikey
            CallLLM.checkCompletion("openai")
        else:
            config.openaiApiKey = "toolmate"
        config.saveConfig()
        print2("Configurations updated!")
        setChatGPTAPIkey()

    def changeGithubAPIkey(self):
        print3("# Github API Key: allows access to OpenAI models via Github service")
        print1("To set up Github API Key, read:\nhttps://github.com/marketplace/models\n")
        print1("Enter a single or a list of multiple Github API Key(s) [optional]:")
        print1("(To enter multiple keys, use the following format: ['api_key_1', 'api_key_2', 'api_key_3'])")
        print()
        apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=str(config.githubApi_key), is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            try:
                if isinstance(eval(apikey), list):
                    config.githubApi_key = eval(apikey)
            except:
                config.githubApi_key = apikey
            CallLLM.checkCompletion("github")
        else:
            config.githubApi_key = "toolmate"
        config.saveConfig()
        print2("Configurations updated!")

    def changeAzureAPIkey(self):
        print3("# Azure API Key: allows access to OpenAI models via Azure service")
        print1("To set up Azure API Key, read:\nhttps://github.com/marketplace/models\n")
        print1("Enter your Azure API Key [optional]:")
        apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.azureApi_key, is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            config.azureApi_key = apikey
        else:
            config.azureApi_key = "toolmate"
        # endpoint
        if config.azureApi_key and not config.azureApi_key == "toolmate":
            print3("# Azure endpoint url [Optional]")
            print1("Enter Azure endpoint url below:")
            endpoint = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.azureBaseUrl)
            if endpoint and not endpoint.strip().lower() in (config.cancel_entry, config.exit_entry):
                config.azureBaseUrl = endpoint
            try:
                CallLLM.checkCompletion("azure")
                config.saveConfig()
                print2("Configurations updated!")
            except:
                print2("Failed to connect!")

    def changeTavilyApi(self):
        print3("# Tavily API Key: allows access to Tavily hosted LLMs")
        print1("To set up Tavily API Key, read:\nhttps://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Tavily%20API%20Setup.md\n")
        print1("Enter a single or a list of multiple Tavily API Key(s) [optional]:")
        print1("(To enter multiple keys, use the following format: ['api_key_1', 'api_key_2', 'api_key_3'])")
        print()
        apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=str(config.tavilyApi_key), is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            try:
                if isinstance(eval(apikey), list):
                    config.tavilyApi_key = eval(apikey)
            except:
                config.tavilyApi_key = apikey
        else:
            config.tavilyApi_key = "toolmate"
        config.saveConfig()
        print2("Configurations updated!")

    def changeGroqApi(self):
        print3("# Groq Cloud API Key: allows access to Groq Cloud hosted LLMs")
        print1("To set up Groq Cloud API Key, read:\nhttps://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Groq%20API%20Setup.md\n")
        print1("Enter a single or a list of multiple Groq Cloud API Key(s) [optional]:")
        print1("(To enter multiple keys, use the following format: ['api_key_1', 'api_key_2', 'api_key_3'])")
        print()
        apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=str(config.groqApi_key), is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            try:
                if isinstance(eval(apikey), list):
                    config.groqApi_key = eval(apikey)
            except:
                config.groqApi_key = apikey
            CallLLM.checkCompletion("groq")
        else:
            config.groqApi_key = "toolmate"
        config.saveConfig()
        print2("Configurations updated!")

    def changeMistralApi(self):
        print3("# Mistral AI API Key: allows access to Mistral AI hosted LLMs")
        print1("To set up Mistral AI API Key, visit:\nhttps://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Mistral%20API%20Setup.md\n")
        print1("Enter a single or a list of multiple Mistral AI API Key(s) [optional]:")
        print1("(To enter multiple keys, use the following format: ['api_key_1', 'api_key_2', 'api_key_3'])")
        print()
        apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=str(config.mistralApi_key), is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            try:
                if isinstance(eval(apikey), list):
                    config.mistralApi_key = eval(apikey)
            except:
                config.mistralApi_key = apikey
            CallLLM.checkCompletion("mistral")
        else:
            config.mistralApi_key = "toolmate"
        config.saveConfig()
        print2("Configurations updated!")

    def changeBingApi(self):
        print3("# Bing Search API Key [Optional]")
        print1("Enter Bing Search API key below:")
        apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.bing_api_key, is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            config.bing_api_key = apikey
        elif not config.bing_api_key:
            config.bing_api_key = "toolmate"
        config.saveConfig()

    def changeRapidApi(self):
        print3("# Rapid API Key [Optional]")
        print1("Enter Rapid API key below:")
        apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.rapid_api_key, is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            config.rapid_api_key = apikey
        elif not config.rapid_api_key:
            config.rapid_api_key = "toolmate"
        config.saveConfig()

    def changeOpenweathermapApi(self):
        print3("# OpenWeatherMap API Key: allows access to real-time weather information")
        print1("To set up OpenWeatherMap API Key, read:\nhttps://github.com/eliranwong/letmedoit/wiki/OpenWeatherMap-API-Setup\n")
        print1("Enter a single or a list of multiple OpenWeatherMap API Key(s) [optional]:")
        print1("(To enter multiple keys, use the following format: ['api_key_1', 'api_key_2', 'api_key_3'])")
        print()
        apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=str(config.openweathermapApi), is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            try:
                if isinstance(eval(apikey), list):
                    config.openweathermapApi = eval(apikey)
            except:
                config.openweathermapApi = apikey
        if getWeather() is not None:
            print2("Configurations updated!")
        else:
            config.openweathermapApi = "toolmate"
            print2("Invalid API key entered!")
        config.saveConfig()

    def changeElevenlabsApi(self):
        print3("# ElevenLabs API Key: allows access to voice generation feature offered by ElevenLabs")
        print1("To set up ElevenLabs API Key, read:\nhttps://elevenlabs.io/docs/api-reference/text-to-speech#authentication\n")
        print1("Enter a single or a list of multiple ElevenLabs API Key(s) [optional]:")
        print1("(To enter multiple keys, use the following format: ['api_key_1', 'api_key_2', 'api_key_3'])")
        print()
        apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=str(config.elevenlabsApi), is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            try:
                if isinstance(eval(apikey), list):
                    config.elevenlabsApi = eval(apikey)
            except:
                config.elevenlabsApi = apikey
        try:
            # testing
            ElevenLabs(api_key=getElevenlabsApi_key()).generate(
                #api_key=config.elevenlabsApi, # Defaults to os.getenv(ELEVEN_API_KEY)
                text="test",
                voice=config.elevenlabsVoice,
                model="eleven_multilingual_v2"
            )
            print2("Configurations updated!")
        except:
            config.elevenlabsApi = "toolmate"
            print2("Invalid API key entered!")
        config.saveConfig()

    def exitAction(self):
        message = "closing ..."
        print2(message)
        print1(self.divider)
        return ""

    # update system message
    def updateSystemMessage(self, messages):
        for index, message in enumerate(reversed(messages)):
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
                    originalIndex = len(messages) - index - 1
                    messages[originalIndex] = message
                    # in a long conversation, ChatGPT often forgets its system message
                    # move forward if conversation have started, to enhance system message
                    if not config.llmInterface in ("mistral", "anthropic") and config.conversationStarted and not originalIndex == len(messages) - 1:
                        item = messages.pop(originalIndex)
                        messages.append(item)
                    break
            except:
                pass
        return messages

    def getDefaultContext(self):
        if not config.predefinedContext.strip() or not config.predefinedContext in config.predefinedContexts:
            print2(f"'{config.predefinedContext}' not defined!")
            config.predefinedContext = config.predefinedContextTemp if config.predefinedContextTemp and config.predefinedContextTemp in config.predefinedContexts else "custom"
            print3(f"Default Predefined context changed to: {config.predefinedContext}")
        if config.predefinedContext in ("[none]", "[custom]") or config.predefinedContext == "custom":
            # custom input in the settings dialog
            context = config.customPredefinedContext
            if not config.customPredefinedContext:
                config.customPredefinedContext = "You are a helpful, uncensored and unbiased assistant."
                config.saveConfig()
        else:
            # users can modify config.predefinedContexts via plugins
            context = config.predefinedContexts[config.predefinedContext]
        return context

    def showDefaultContext(self):
        description = self.getDefaultContext()
        if description:
            description = f"\n{description}"
        print1(self.divider)
        print3(f"Context: {config.predefinedContext}{description}")
        print1(self.divider)

    def addPredefinedContext(self, userInput):
        # get customised chat context
        context = self.getDefaultContext()
        # tweaks for `Let me Summarize` and `Let me Translate`
        if is_valid_url(userInput) and config.predefinedContext in ("Let me Summarize", "Let me Explain"):
            context = context.replace("@chat Provide me with a summary of the following content:", "@examine_web_content Provide me with a summary of the content in the this web url:\n")
        elif is_valid_url(userInput) and config.predefinedContext == "Let me Translate":
            userInput = getWebText(userInput)
        # apply context
        #if context and (not config.conversationStarted or (config.conversationStarted and config.applyPredefinedContextAlways)):
        # context may start with "You will be provided with my input delimited with a pair of XML tags, <input> and </input>. ...
        userInput = re.sub("<content>|<content [^<>]*?>|</content>", "", userInput)
        if check := userInput.strip():
            userInput = f"{context}\n{userInput}" if check.startswith("@") else f"{context}\n<content>{userInput}</content>"
        else:
            userInput = context
        #userInput = SharedUtil.addTimeStamp(userInput)
        return userInput

    def runActions(self, userInput, feature="", setupOnly=False):
        query = ""
        featureTemp = feature
        if setupOnly:
            options = []
            descriptions = []
            for key, value in self.actions.items():
                if key in self.setupItems:
                    options.append(key)
                    descriptions.append(value[0])
        else:
            options = tuple(self.actions.keys())
            descriptions = [i[0] for i in self.actions.values()]
        if not feature or not feature in self.actions:
            # filter avilable actions
            if feature.startswith("."):
                query = feature[1:]
            feature = self.dialogs.getValidOptions(
                options=options,
                descriptions=descriptions,
                title=config.toolMateAIName,
                default=config.defaultActionMenuItem,
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
        if config.thisPlatform == "Windows":
            print2("Auto upgrading is not supported on Windows!")
            return None
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
            print3("Note: Changes applicable to 'openai', 'github', 'azure' and 'letmedoit' interfaces only.")

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

    def setFabricPatternsDirectory(self):
        print2("# Setting up fabric integration")
        print1("Read more about fabric at https://github.com/danielmiessler/fabric")

        print2("Enter fabric command or its full path below:")
        fabricPath = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.fabricPath)
        if fabricPath and not fabricPath.strip().lower() in (config.cancel_entry, config.exit_entry) and (os.path.isfile(os.path.expanduser(fabricPath)) or shutil.which(fabricPath)):
            config.fabricPath = fabricPath
            config.saveConfig()
            print3(f"Fabric command: {fabricPath}")
        else:
            print2("Fabric not found! Read https://github.com/danielmiessler/fabric for installation!")

        print2("Enter the path of fabric patterns directory below:")
        folder = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.fabricPatterns if os.path.isfile(os.path.expanduser(config.fabricPatterns)) else os.path.join(os.path.expanduser("~"), ".config", "fabric", "patterns"))
        if folder and os.path.isdir(os.path.expanduser(folder)):
            config.fabricPatterns = folder
            config.saveConfig()
            print3(f"Fabric patterns directory: {folder}")
        else:
            print2("Invalid path given!")

    def setLatestSearches(self):
        options = ("always", "auto", "none")
        descriptions = (
            "always search for latest information",
            "search only when LLM lacks information",
            "do not perform online searches",
        )
        option = self.dialogs.getValidOptions(
            options=options,
            descriptions=descriptions,
            title="Latest Online Searches",
            default=config.loadingInternetSearches,
            text=f"{config.toolMateAIName} can perform online searches.\nHow do you want this feature?",
        )
        if option:
            config.loadingInternetSearches = option
            # fine tune
            if config.loadingInternetSearches == "auto":
                config.chatGPTApiFunctionCall = "auto"
                if "search google" in config.pluginExcludeList:
                    config.pluginExcludeList.remove("search google")
            elif config.loadingInternetSearches == "none":
                if not "search google" in config.pluginExcludeList:
                    config.pluginExcludeList.append("search google")
            # reset plugins
            Plugins.runPlugins()
            # notify
            config.saveConfig()
            print3(f"Latest Online Searches: {option}")

    def manageCodeExecutionRisk(self):
        options = ("0", "1", "2", "3")
        if not str(config.riskThreshold) in options:
            config.riskThreshold = 0
        descriptions = (
            "always",
            "medium risk or above",
            "high risk only, e.g. file deletion",
            "none",
        )
        option = self.dialogs.getValidOptions(
            options=options,
            descriptions=descriptions,
            title="Configure Risk Threshold",
            text=f"To fulfill your requests, our built-in tools can generate and execute codes or commands. To protect you from running generated codes that may pose a risk to your system, such as file deletion, ToolMate AI has a built-in risk management agent. This agent assesses the risk level of generated code and prompts you for confirmation before execution. You can specify the risk threshold below, determining the level at which you will be asked for confirmation. (Note: Confirming code execution is done at your own risk.)",
            default=config.riskThreshold,
        )
        if option:
            config.riskThreshold = int(option)
            config.saveConfig()
            print3(f"Risk threshold: {option}")

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
            text="Enabling this feature allows\npassing tool call responses, if any,\nto extend conversation with ChatGPT.\nDisabling this feature allows\nrunning tool calls\nwithout generating further responses."
        )
        if call:
            config.passFunctionCallReturnToChatGPT = (call == "enable")
            config.saveConfig()
            print3(f"Pass Function Call Response to ChatGPT: {'enabled' if config.passFunctionCallReturnToChatGPT else 'disabled'}!")

    def extractPythonCodeFromLastResponse(self):
        config.defaultEntry = f'''```python
{extractPythonCode(getAssistantPreviousResponse()[0], keepInvalid=True)}```'''

    def runPythonCodeInLastResponse(self):
        previousResponse = getAssistantPreviousResponse()[0]
        code = extractPythonCode(previousResponse)
        if code:
            config.defaultEntry = f'''```python
{code}```'''
            config.accept_default = True
        else:
            config.defaultEntry = extractPythonCode(previousResponse, keepInvalid=True)

    def readLastResponse(self):
        previousResponse, _ = getAssistantPreviousResponse()
        if previousResponse:
            TTSUtil.play(re.sub(config.tts_doNotReadPattern, "", previousResponse))

    def readCurrentMessages(self):
        editableContent, _ = self.getCurrentMessagesItem()
        if editableContent:
            TTSUtil.play(re.sub(config.tts_doNotReadPattern, "", editableContent))

    def trimCurrentConversation(self):
        def getEditableContent(role, item):
            content = item.get("content", "")
            editableContent = f"[{role}] {content}"
            if len(editableContent) > 50:
                editableContent = editableContent[:50] + " ..."
            return editableContent
        editable = {}
        lastUserItem = 0
        editableContent = ""
        for index, item in enumerate(config.currentMessages):
            role = item.get("role", "")
            if role == "user":
                editableContent = getEditableContent(role, item)
                lastUserItem = index
            elif role == "assistant":
                editableContent += " " + getEditableContent(role, item)
                editable[f"{lastUserItem}.{index}"] = editableContent
        if editable:
            selectedItems = self.dialogs.getMultipleSelection(
                title="Trim Current Conversation",
                text="Select the items to be removed:",
                options=editable.keys(),
                descriptions=list(editable.values()),
                default_values=[],
            )
            if selectedItems is not None:
                for i in selectedItems:
                    user, assistant = i.split(".")
                    del config.currentMessages[int(assistant)]
                    del config.currentMessages[int(user)]
                clear()
                print2("Reloading conversation ...")
                print()
                displayLoadedMessages(config.currentMessages)
        else:
            print2("No editable item found!")

    def editCurrentConversation(self):
        editableContent, editItemIndex = self.getCurrentMessagesItem(instruction="Select the item to be edited:")
        if editItemIndex is not None:
            tempTextFile = os.path.join(config.toolMateAIFolder, "temp", "editableItem.txt")
            # write previous response in a temp file
            writeTextFile(tempTextFile, editableContent)
            # editing
            customTextEditor = config.customTextEditor if config.customTextEditor else f"{sys.executable} {os.path.join(config.toolMateAIFolder, 'eTextEdit.py')}"
            os.system(f"{customTextEditor} {tempTextFile}")
            set_title(config.toolMateAIName)
            # read edited response
            editedContent = readTextFile(tempTextFile)
            # save changes
            if not (editableContent == editedContent):
                config.currentMessages[editItemIndex]["content"] = editedContent
                #self.saveChat(config.currentMessages)
                clear()
                print2("Reloading conversation ...")
                print()
                displayLoadedMessages(config.currentMessages)

    def getCurrentMessagesItem(self, instruction="Select an item:"):
        editable = {}
        lastItem = 0
        for index, item in enumerate(config.currentMessages):
            role = item.get("role", "")
            if role in ("user", "assistant"):
                content = item.get("content", "")
                editableContent = f"[{role}] {content}"
                if len(editableContent) > 50:
                    editableContent = editableContent[:50] + " ..."
                editable[str(index)] = editableContent
                lastItem = index
        if editable:
            editItem = self.dialogs.getValidOptions(
                options=editable.keys(),
                descriptions=list(editable.values()),
                title="Edit Current Conversation",
                default=str(lastItem),
                text=instruction,
            )
            if editItem:
                editItemIndex = int(editItem)
                editableContent = config.currentMessages[editItemIndex]["content"]
                return editableContent, editItemIndex
        else:
            print2("No editable item found!")
        return None, None

    # change configs
    def editConfigs(self):
        # file paths
        configFile = os.path.join(config.toolMateAIFolder, "config.py")
        backupFile = os.path.join(config.localStorage, "config_lite_backup.py" if config.isLite else "config_backup.py")
        # backup configs
        config.saveConfig()
        shutil.copy(configFile, backupFile)
        # open current configs with built-in text editor
        customTextEditor = config.customTextEditor if config.customTextEditor else f"{sys.executable} {os.path.join(config.toolMateAIFolder, 'eTextEdit.py')}"
        os.system(f"{customTextEditor} {configFile}")
        set_title(config.toolMateAIName)
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

    def setTemperature(self, temperature=None):
        if temperature is None:
            print1("Enter a value between 0.0 and 2.0:")
            print1("(Lower values for temperature result in more consistent outputs, while higher values generate more diverse and creative results. Select a temperature value based on the desired trade-off between coherence and creativity for your specific application.)")
            temperature = self.prompts.simplePrompt(style=self.prompts.promptStyle2, validator=FloatValidator(), default=str(config.llmTemperature))
        else:
            temperature = str(temperature)
        if temperature and not temperature.strip().lower() == config.exit_entry:
            temperature = float(temperature)
            if temperature < 0:
                temperature = 0
            elif temperature > 2:
                temperature = 2
            config.llmTemperature = round(temperature, 1)
            if temperature is None:
                config.saveConfig()
                print3(f"LLM Temperature: {temperature}")

    def configureToolSelectionAgent(self) -> bool:
        options = ("yes", "no")
        question = "Would you like our built-in tool selection agent to choose the appropriate tools for resolving your requests?\nRemarks:\n* Enabling this option consumes more tokens.\n* You can manually call a specific tool at any time by entering a tool name prefixed with `@`."
        print1(question)
        tool_selection_agent = self.dialogs.getValidOptions(
            options=options,
            title="Enable Tool Selection Agent",
            default="yes" if config.tool_selection_agent else "no",
            text=question,
        )
        if tool_selection_agent:
            if tool_selection_agent == "yes":
                config.tool_selection_agent = True
                return True
            else:
                config.tool_selection_agent = False
        return False

    def configureToolSelectionRequirements(self) -> bool:
        options = ("yes", "no")
        question = "Would you like to inform the Tool Selection Agent of each tool's requirements? Doing so could improve the selection outcome, but it will consume more tokens and processing power."
        print1(question)
        tool_selection_requirements = self.dialogs.getValidOptions(
            options=options,
            title="Include Tool Requirements",
            default="yes" if config.tool_selection_requirements else "no",
            text=question,
        )
        if tool_selection_requirements:
            if tool_selection_requirements == "yes":
                config.tool_selection_requirements = True
                return True
            else:
                config.tool_selection_requirements = False
        return False

    def configureAutoToolSelection(self) -> bool:
        options = ("yes", "no")
        question = "Would you like to automatically use the first recommended tool suggested by our built-in tool selection agent?"
        print1(question)
        auto_tool_selection = self.dialogs.getValidOptions(
            options=options,
            title="Enable Automatic Tool Selection",
            default="yes" if config.auto_tool_selection else "no",
            text=question,
        )
        if auto_tool_selection:
            if auto_tool_selection == "yes":
                config.auto_tool_selection = True
                return True
            else:
                config.auto_tool_selection = False
        return False

    def setToolSelectionConfigs(self):
        tool_selection_agent = config.tool_selection_agent
        self.configureToolSelectionAgent()
        if config.tool_selection_agent:
            self.configureToolSelectionRequirements()
            self.configureAutoToolSelection()
        else:
            self.setDefaultTool()
        if not tool_selection_agent == config.tool_selection_agent:
            # reload plugins as some plugins changes with config.tool_selection_agent value
            Plugins.runPlugins()

    def selectLlmPlatform(self):
        instruction = "Select an AI Backend:"
        print1(instruction)
        options = {
            "llamacppserver": "Llama.cpp [FREE]",
            "llamacpppython": "Llama-cpp-python [FREE]",
            "ollama": "Ollama [FREE]",
            "groq": "Groq Cloud API [FREE/PAID]",
            "mistral": "Mistral AI API [FREE/PAID]",
            "anthropic": "Anthropic AI API [PAID]",
            "xai": "X AI API [PAID]",
            "googleai": "Google AI Studio API [PAID]",
            "vertexai": "Google Vertex AI [PAID]",
            "genai": "Google GenAI API [PAID]",
            "openai": "OpenAI ChatGPT [PAID]",
            "github": "OpenAI ChatGPT - Github [FREE]",
            "azure": "OpenAI ChatGPT - Azure [PAID]",
            "letmedoit": "LetMeDoIt Mode [via PAID ChatGPT models]",
        }
        try:
            from llama_cpp import Llama
        except:
            del options["llamacpppython"]
        try:
            from vertexai.generative_models import GenerativeModel
        except:
            del options["vertexai"]
        try:
            from google import genai as googlegenai
        except:
            del options["genai"]
        llmInterface = self.dialogs.getValidOptions(
            options=options.keys(),
            descriptions=list(options.values()),
            title="AI Backends",
            default=config.llmInterface if config.llmInterface else "llamacpppython",
            text=instruction,
        )
        if llmInterface:
            config.llmInterface = llmInterface
            if not config.llmInterface == "llamacpppython" and hasattr(config, "llamacppToolModel"):
                config.llamacppToolModel = None

    def setLlmModel(self):
        def askAdditionalChatModel() -> bool:
            options = ("yes", "no")
            question = "Would you like an additional model for running chat-only features?"
            print2("# Additional Chat Model [Optional] ...")
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

        currentLlmInterface = config.llmInterface
        self.selectLlmPlatform()

        print1("Select models ...")
        if config.llmInterface == "ollama":
            print2("# Tool Model - for both task execution and conversation")
            self.setLlmModel_ollama()
            self.setContextWindowSize(feature="default")
            self.setMaxTokens(feature="default")
            if askAdditionalChatModel():
                print2("# Chat Model - for conversation only")
                self.setLlmModel_ollama("chat")
                self.setContextWindowSize(feature="chat")
                self.setMaxTokens(feature="chat")
        elif config.llmInterface == "llamacpppython":
            print2("# Tool Model - for both task execution and conversation")
            self.setLlmModel_llamacpp()
            self.setContextWindowSize(feature="default")
            self.setMaxTokens(feature="default")
            self.setGpuLayers(feature="default")
            if askAdditionalChatModel():
                print2("# Chat Model - for conversation only")
                self.setLlmModel_llamacpp("chat")
                self.setContextWindowSize(feature="chat")
                self.setMaxTokens(feature="chat")
                self.setGpuLayers(feature="chat")
        elif config.llmInterface == "llamacppserver":
            print2("# Tool Server - for both task execution and conversation")
            self.setLlmModel_llamacppserver()
            self.setMaxTokens(feature="default")
            if askAdditionalChatModel():
                print2("# Chat Server - for conversation only")
                self.setLlmModel_llamacppserver("chat")
                self.setMaxTokens(feature="chat")
            #print2("# Vision Server - for vision only")
            #self.setLlmModel_llamacppserver("vision")
        elif config.llmInterface == "groq":
            #if not config.groqApi_key or config.groqApi_key == "toolmate":
            self.changeGroqApi()
            print2("# Tool Model - for both task execution and conversation")
            self.setLlmModel_groq()
            self.setMaxTokens(feature="default")
            if askAdditionalChatModel():
                print2("# Chat Model - for conversation only")
                self.setLlmModel_groq("chat")
                self.setMaxTokens(feature="chat")
        elif config.llmInterface == "mistral":
            #if not config.mistralApi_key or config.mistralApi_key == "toolmate":
            self.changeMistralApi()
            print2("# Tool Model - for both task execution and conversation")
            self.setLlmModel_mistral()
            self.setMaxTokens(feature="default")
            if askAdditionalChatModel():
                print2("# Chat Model - for conversation only")
                self.setLlmModel_mistral("chat")
                self.setMaxTokens(feature="chat")
        elif config.llmInterface == "xai":
            #if not config.xaiApi_key or config.xaiApi_key == "toolmate":
            self.changeXaiApikey()
            self.setLlmModel_xai()
            self.setMaxTokens(feature="default")
        elif config.llmInterface == "anthropic":
            self.changeAnthropicAPIkey()
            self.setLlmModel_anthropic()
            self.setMaxTokens(feature="default")
        elif config.llmInterface == "genai":
            print2("# GenAI Configurations ...")
            print1("GenAI SDK supports running Gemini 2.0 models. Configure either Google Vertex AI credentials or Google AI API Key. You will be prompted to enter Google AI API key only if you do not provide vertex AI credentials.")
            if not "Vertex AI" in config.enabledGoogleAPIs:
                config.enabledGoogleAPIs.append("Vertex AI")
            if not self.setGoogleCredentialsPath():
                self.changeGoogleaiApikey()
            self.setLlmModel_genai()
            self.setMaxTokens(feature="default")
        elif config.llmInterface == "vertexai":
            if not "Vertex AI" in config.enabledGoogleAPIs:
                config.enabledGoogleAPIs.append("Vertex AI")
            if not self.setGoogleCredentialsPath():
                return None
            self.setLlmModel_vertexai()
            self.setMaxTokens(feature="default")
        elif config.llmInterface == "googleai":
            self.changeGoogleaiApikey()
            self.setLlmModel_googleai()
            self.setMaxTokens(feature="default")
        else:
            # chatgpt / letmedoit
            if config.llmInterface == "github":
                self.changeGithubAPIkey()
            elif config.llmInterface == "azure":
                self.changeAzureAPIkey()
            else:
                self.changeChatGPTAPIkey()
            self.setLlmModel_chatgpt()
            self.setMaxTokens(feature="default")
        config.saveConfig()
        if not config.llmInterface == currentLlmInterface:
            if currentLlmInterface == "ollama":
                CallLLM.resetMessages() # unload Ollama models
            print2("LLM Interface changed! Starting a new chat session ...")
            config.defaultEntry = ".new"
            config.accept_default = True
        try:
            CallLLM.checkCompletion()
            self.setEmbeddingModel()
        except:
            config.llmInterface = ""
            self.setLlmModel()
        if not config.llmInterface:
            self.setLlmModel()

    def selectOllamaModel(self, message="Select a model from Ollama Library:", feature="default") -> str:
        # history session
        historyFolder = os.path.join(config.localStorage, "history")
        Path(historyFolder).mkdir(parents=True, exist_ok=True)
        model_history = os.path.join(historyFolder, "ollama_chat" if feature == "chat" else "ollama_default")
        model_session = PromptSession(history=FileHistory(model_history))
        completer = FuzzyCompleter(WordCompleter(sorted(ollama_models), ignore_case=True))
        bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}"""
        if feature == "embedding":
            default = config.embeddingModel[8:] if config.embeddingModel.startswith("_ollama_") else "nomic-embed-text"
        elif config.llmInterface == "llamacpppython":
            if feature == "default" and config.llamacppToolModel_ollama_tag:
                default = config.llamacppToolModel_ollama_tag
            elif feature == "chat" and config.llamacppChatModel_ollama_tag:
                default = config.llamacppChatModel_ollama_tag
        else:
            default = config.ollamaChatModel if feature == "chat" else config.ollamaToolModel
        # prompt
        print1(message)
        print1("(For details, visit https://ollama.com/library)")
        model = self.prompts.simplePrompt(style=self.prompts.promptStyle2, promptSession=model_session, bottom_toolbar=bottom_toolbar, default=default, completer=completer)
        if model and not model.lower() == config.exit_entry:
            return model
        return ""

    def setLlmModel_ollama(self, feature="default"):
        def setIp(feature=feature):
            ips = {
                "default": config.ollamaToolServer_host,
                "chat": config.ollamaChatServer_host,
            }
            ip = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=ips[feature])
            ip = re.sub("^(http://|https://)", "", ip, re.IGNORECASE)
            if ip is not None and not ip.strip().lower() == config.exit_entry: # accept blank entry
                if feature=="chat":
                    config.ollamaChatServer_host = ip
                else:
                    config.ollamaToolServer_host = ip
        def setPort(feature=feature):
            ports = {
                "default": config.ollamaToolServer_port,
                "chat": config.ollamaChatServer_port,
            }
            port = self.prompts.simplePrompt(numberOnly=True, style=self.prompts.promptStyle2, default=str(ports[feature]))
            if port and not port.strip().lower() == config.exit_entry:
                port = int(port)
                if feature=="chat":
                    config.ollamaChatServer_port = port
                else:
                    config.ollamaToolServer_port = port
        # specify host ip and port
        print3(f"# Ollama server for running: {'chatbot' if feature=='chat' else 'tool'}")
        print2("Enter server address below:")
        print1("(Enter a blank entry '' if you want to use device local ip address instead of '127.0.0.1')")
        setIp(feature=feature)
        print2("Enter server port below:")
        setPort(feature=feature)

        # select model
        downloadedOllamaModels = getLlms()["ollama"]
        if downloadedOllamaModels:
            model = self.dialogs.getValidOptions(
                options=downloadedOllamaModels+["more ..."],
                title="Ollama Models",
                default=config.ollamaChatModel if feature == "chat" else config.ollamaToolModel,
                text=f"Select a {'chat' if feature=='chat' else 'tool'} call model:\n(for {'conversations only' if feature=='chat' else 'both chat and task execution'})",
            )
            if model == "more ...":
                model = self.selectOllamaModel(feature=feature)
        else:
            model = self.selectOllamaModel(feature=feature)
        if model:
            try:
                if not model in getLlms()["ollama"]:
                    Downloader.downloadOllamaModel(model, True)
                if feature == "default":
                    config.ollamaToolModel = model
                elif feature == "chat":
                    config.ollamaChatModel = model
                elif feature == "embedding":
                    config.embeddingModel = f"_ollama_{model}"
            except:
                print2(f"Failed to download '{model}'! Please make sure Ollama server is running and specify a valid model name.")

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
        #print2(f"Enter full custom {server} server command line below:")
        #print1("(or leave it blank to use built-in or remote llama.cpp server)")
        #command = setCommand()
        print2(f"Enter custom {server} server IP address below:")
        setIp(server=server)
        print2(f"Enter custom {server} server port below:")
        setPort(server=server)
        #if command:
        #    # timeout option does not apply to built-in server
        #    print2(f"Enter custom {server} server read/write timeout in seconds below:")
        #    setTimeout()
        # try to start server
        #if server in ("tool", "chat"):
        #    runToolMateCommand(f"custom{server}server")

    def setLlmModel_llamacpp(self, feature="default"):
        library = self.dialogs.getValidOptions(
            options=("Downloaded GGUF Files", "Ollama Library", "Custom"),
            title="Model Library",
            default="Downloaded GGUF Files",
            text="Select a model library:",
        )
        if library:
            if library == "Ollama Library":
                downloadedOllamaModels = getLlms()["ollama"]
                if downloadedOllamaModels:
                    model = self.dialogs.getValidOptions(
                        options=downloadedOllamaModels+["more ..."],
                        title="Ollama Models",
                        default=config.ollamaChatModel if feature == "chat" else config.ollamaToolModel,
                        text=f"Select a {'chat' if feature=='chat' else 'tool'} call model:\n(for {'conversations only' if feature=='chat' else 'both chat and task execution'})",
                    )
                    if model == "more ...":
                        model = self.selectOllamaModel(feature=feature)
                else:
                    model = self.selectOllamaModel(feature=feature)
                if model:
                    if model in getLlms()["ollama"]:
                        exportedPath = exportOllamaModels([model])[0]
                        if feature == "default":
                            config.llamacppToolModel_model_path = exportedPath
                        elif feature == "chat":
                            config.llamacppChatModel_model_path = exportedPath
                    else:
                        try:
                            Downloader.downloadOllamaModel(model, True)
                            model_name = model.replace(":latest", "")
                            model_path = exportOllamaModels([model_name])[0]
                            # refresh download list
                            
                            if feature == "default":
                                config.llamacppToolModel_model_path = model_path
                            elif feature == "chat":
                                config.llamacppChatModel_model_path = model_path
                        except:
                            print2(f"Failed to download '{model}'! Please make sure Ollama server is running and specify a valid model name.")
                    if feature == "default":
                        config.llamacppToolModel_ollama_tag = model
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
                            config.llamacppToolModel_model_path = downloadedGgufModels[model]
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
            default=config.llamacppChatModel_model_path if feature == "chat" else config.llamacppToolModel_model_path,
        )
        if model_path and os.path.isfile(model_path):
            if feature == "default":
                config.llamacppToolModel_model_path = model_path
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
        repo_id = self.prompts.simplePrompt(style=self.prompts.promptStyle2, promptSession=repo_id_session, bottom_toolbar=bottom_toolbar, default=config.llamacppChatModel_repo_id if feature == "chat" else config.llamacppToolModel_repo_id)
        print2("Please specify a filename or glob pattern to match the model file in the repo:")
        filename = self.prompts.simplePrompt(style=self.prompts.promptStyle2, promptSession=filename_session, bottom_toolbar=bottom_toolbar, default=config.llamacppChatModel_filename if feature == "chat" else config.llamacppToolModel_filename)
        if (repo_id and not repo_id.lower() == config.exit_entry) and (filename and not filename.lower() == config.exit_entry):
            if feature == "default":
                config.llamacppToolModel_repo_id = repo_id
                config.llamacppToolModel_filename = filename
                config.llamacppToolModel_model_path = ""
            elif feature == "chat":
                config.llamacppChatModel_repo_id = repo_id
                config.llamacppChatModel_filename = filename
                config.llamacppChatModel_model_path = ""
            CallLLM.checkCompletion()
        else:
            print2("Action cancelled due to insufficient information!")

    def setLlmModel_groq(self, feature="default"):
        model = self.dialogs.getValidOptions(
            options=getLlms()["groq"],
            title="Groq Cloud Models",
            default=config.groqApi_chat_model if feature == "chat" else config.groqApi_tool_model,
            text=f"Select a {'chat' if feature=='chat' else 'tool'} call model:\n(for {'conversations only' if feature=='chat' else 'both chat and task execution'})",
        )
        if model:
            if feature == "default":
                config.groqApi_tool_model = model
            elif feature == "chat":
                config.groqApi_chat_model = model
            print3(f"Groq model: {model}")

    def setLlmModel_mistral(self, feature="default"):
        model = self.dialogs.getValidOptions(
            options=getLlms()["mistral"],
            title="Mistral AI Models",
            default=config.mistralApi_chat_model if feature == "chat" else config.mistralApi_tool_model,
            text=f"Select a {'chat' if feature=='chat' else 'tool'} call model:\n(for {'conversations only' if feature=='chat' else 'both chat and task execution'})",
        )
        if model:
            if feature == "default":
                config.mistralApi_tool_model = model
            elif feature == "chat":
                config.mistralApi_chat_model = model
            print3(f"Mistral model: {model}")

    def setLlmModel_googleai(self):
        models = getLlms()["googleai"]
        model = self.dialogs.getValidOptions(
            options=models,
            title="Google AI Studio Models",
            default=config.googleaiApi_tool_model if config.googleaiApi_tool_model in models else models[0],
            text="Select a tool call model:\n(for both chat and task execution)",
        )
        if model:
            config.googleaiApi_tool_model = model
            print3(f"Gemini model: {model}")

    def setLlmModel_anthropic(self):
        models = getLlms()["anthropic"]
        model = self.dialogs.getValidOptions(
            options=models,
            title="Anthropic Claude Models",
            default=config.anthropicApi_tool_model if config.anthropicApi_tool_model in models else models[0],
            text="Select a tool call model:\n(for both chat and task execution)",
        )
        if model:
            config.anthropicApi_tool_model = model
            print3(f"Anthropic Claude model: {model}")

    def setLlmModel_xai(self):
        models = getLlms()["xai"]
        model = self.dialogs.getValidOptions(
            options=models,
            title="X AI Models",
            default=config.xaiApi_tool_model if config.xaiApi_tool_model in models else models[0],
            text="Select a tool call model:\n(for both chat and task execution)",
        )
        if model:
            config.xaiApi_tool_model = model
            print3(f"X AI model: {model}")

    def setLlmModel_vertexai(self):
        models = getLlms()["vertexai"]
        model = self.dialogs.getValidOptions(
            options=models,
            title="Google Vertex AI Models",
            default=config.vertexai_model if config.vertexai_model in models else models[0],
            text="Select a tool call model:\n(for both chat and task execution)",
        )
        if model:
            config.vertexai_model = model
            print3(f"Gemini model: {model}")

    def setLlmModel_genai(self):
        models = getLlms()["genai"]
        model = self.dialogs.getValidOptions(
            options=models,
            title="Google GenAI Models",
            default=config.genai_model if config.genai_model in models else models[0],
            text="Select a tool call model:\n(for both chat and task execution)",
        )
        if model:
            config.vertexai_model = model
            print3(f"Gemini model: {model}")

    def setLlmModel_chatgpt(self):
        if config.llmInterface == "openai":
            models = list(chatgptTokenLimits.keys())
        if config.llmInterface == "azure":
            models = config.azureOpenAIModels
        else: # github
            models = ["gpt-4o", "gpt-4o-mini"]
        model = self.dialogs.getValidOptions(
            options=models,
            title="ChatGPT Model",
            default=config.chatGPTApiModel if config.chatGPTApiModel in models else models[0],
            text="Select a tool call model:\n(for both chat and task execution)",
        )
        if model:
            config.chatGPTApiModel = model
            print3(f"ChatGPT model: {model}")
            # set max tokens
            config.chatGPTApiMaxTokens = self.getMaxTokens()[-1]
            print3(f"Maximum output tokens: {config.chatGPTApiMaxTokens}")

    def setEmbeddingModel(self):
        def askChangingEmbedding():
            options = ("yes", "no")
            question = "Caution is advised! It is essential to use a consistent embedding model for searching stored vector databases. If you decide to switch to a different embedding model, you must delete any previous vector stores saved with ToolMate AI for ToolMate AI to function correctly. Do you want to change the default embedding model now?"
            print2("# Changing Embbeding Model [Optional] ...")
            print1(question)
            change = self.dialogs.getValidOptions(
                options=options,
                title="Changing Embbeding Model [Optional] ...",
                default="no",
                text=question,
            )
            return False if not change or not change == "yes" else True

        if not askChangingEmbedding():
            return None
        oldEmbeddingModel = config.embeddingModel
        model = self.dialogs.getValidOptions(
            options=("text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002", "paraphrase-multilingual-mpnet-base-v2", "all-mpnet-base-v2", "all-MiniLM-L6-v2", "Ollama models", "custom"),
            title="Embedding model",
            default=config.embeddingModel,
            text="Select an embedding model:",
        )
        if model:
            if model == "Ollama models":
                self.setLlmModel_ollama(feature="embedding")
            elif model == "custom":
                print1("Enter OpenAI or Sentence Transformer Embedding model:")
                print1("OpenAI Embedding Models: https://platform.openai.com/docs/guides/embeddings/embedding-models")
                print1("Sentence Transformer Models: https://www.sbert.net/docs/pretrained_models.html")
                customModel = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.embeddingModel)
                if customModel and not customModel.strip().lower() == config.exit_entry:
                    config.embeddingModel = customModel 
            else:
                config.embeddingModel = model
            print3(f"Embedding model: {model}")
        if not oldEmbeddingModel == config.embeddingModel:
            print1(f"You've change the embedding model from '{oldEmbeddingModel}' to '{config.embeddingModel}'.")
            print1("To work with the newly selected model, you need to delete the previous memory store and saved vector databases, saved by ToolMate AI.")
            print1("Do you want to delete them now? [y]es / [N]o")
            confirmation = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default="yes")
            if confirmation.lower() in ("y", "yes"):
                ragStore = os.path.join(config.localStorage, "rag")
                memory_store = os.path.join(config.localStorage, "memory")
                retrieved_collections = os.path.join(config.localStorage, "autogen", "retriever")
                for folder in (ragStore, memory_store, retrieved_collections):
                    shutil.rmtree(folder, ignore_errors=True)
            else:
                print1(f"Do you want to change back the embedding model from '{config.embeddingModel}' to '{oldEmbeddingModel}'? [y]es / [N]o")
                confirmation = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default="yes")
                if not confirmation.lower() in ("y", "yes"):
                    config.embeddingModel = oldEmbeddingModel
                    print3(f"Embedding model: {oldEmbeddingModel}")
        if not oldEmbeddingModel == config.embeddingModel:
            config.saveConfig()

    def setAutoGenConfig(self):
        if config.isLite:
            print("Autobuilder configurations are applicable in full version only!")
        else:
            AutoGenBuilder().promptConfig()

    def changeMyFavouries(self):
        if not config.tool_selection_agent:
            self.setDefaultTool()
        self.setFavorite_string()

    def setFavorite_string(self):
        completer = FuzzyCompleter(WordCompleter([f"@{i}" for i in config.allEnabledTools], ignore_case=True))
        hotkey_insert_bestliked_entry = str(config.hotkey_insert_bestliked_entry)[2:-2].replace("c-", "Ctrl+")
        hotkey_insert_favorite_entry = str(config.hotkey_insert_favorite_entry)[2:-2].replace("c-", "Ctrl+")
        print2(f"Two key combinations `{hotkey_insert_bestliked_entry}` and `{hotkey_insert_favorite_entry}` are used for inserting most frequently entries easily.")
        # best-link entry
        print1(f"Enter your best-liked entry that is inserted automatically with the key combo `{hotkey_insert_bestliked_entry}`:")
        favorite_string_best = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.favorite_string_best, completer=completer)
        if favorite_string_best and not favorite_string_best.strip().lower() == config.exit_entry:
            config.favorite_string_best = favorite_string_best
            config.saveConfig()
            print3(f"Favourite entry changed: {config.favorite_string_best}")
        # favourite entry
        print1(f"Enter your favourite entry that is inserted automatically with the key combo `{hotkey_insert_favorite_entry}`:")
        favorite_string = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.favorite_string, completer=completer)
        if favorite_string and not favorite_string.strip().lower() == config.exit_entry:
            config.favorite_string = favorite_string
            config.saveConfig()
            print3(f"Favourite entry changed: {config.favorite_string}")

    def setAssistantName(self):
        print1("You may modify my name below:")
        toolMateAIName = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.toolMateAIName)
        if toolMateAIName and not toolMateAIName.strip().lower() == config.exit_entry:
            config.toolMateAIName = toolMateAIName
            config.localStorage = getLocalStorage()
            config.saveConfig()
            print3(f"You have changed my name to: {config.toolMateAIName}")

    def getCurrentChatSystemMessage(self):
        if config.llmInterface == "ollama":
            systemMessage_chat = config.systemMessage_ollama
        elif config.llmInterface == "groq":
            systemMessage_chat = config.systemMessage_groq
        elif config.llmInterface == "mistral":
            systemMessage_chat = config.systemMessage_mistral
        elif config.llmInterface == "llamacppserver":
            systemMessage_chat = config.systemMessage_llamacppserver
        elif config.llmInterface == "llamacpppython":
            systemMessage_chat = config.systemMessage_llamacpp
        elif config.llmInterface == "genai":
            systemMessage_chat = config.systemMessage_genai
        elif config.llmInterface == "vertexai":
            systemMessage_chat = config.systemMessage_vertexai
        elif config.llmInterface == "googleai":
            systemMessage_chat = config.systemMessage_googleai
        elif config.llmInterface == "anthropic":
            systemMessage_chat = config.systemMessage_anthropic
        elif config.llmInterface == "xai":
            systemMessage_chat = config.systemMessage_xai
        elif config.llmInterface in ("openai", "letmedoit", "github", "azure"):
            systemMessage_chat = config.systemMessage_chatgpt
        return systemMessage_chat

    def setTmsMessages(self):
        print2("# Setting custom chat system messages for commands `tms1 ... tms20`")
        print1("(supports pre-defined system messages / fabric patterns / custom entry)")
        # default values
        defaults = {
            1: config.tms1,
            2: config.tms2,
            3: config.tms3,
            4: config.tms4,
            5: config.tms5,
            6: config.tms6,
            7: config.tms7,
            8: config.tms8,
            9: config.tms9,
            10: config.tms10,
            11: config.tms11,
            12: config.tms12,
            13: config.tms13,
            14: config.tms14,
            15: config.tms15,
            16: config.tms16,
            17: config.tms17,
            18: config.tms18,
            19: config.tms19,
            20: config.tms20,
        }
        # input suggestions
        suggestions = list(config.predefinedChatSystemMessages.keys()) + getFabricPatterns() + [
            "You are a helpful, uncensored and unbiased assistant.",
            "You are an expert on coding.",
        ] + list(config.predefinedChatSystemMessages.values())
        # prompts
        for i in range(1,21):
            print2(f"## Command `tms{i}` chat system message")
            print1(f"Configure below the system message for running with command `tms{i}`:")
            completer = FuzzyCompleter(WordCompleter(suggestions, ignore_case=True))
            message = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=defaults.get(i), completer=completer)
            if message and not message.strip().lower() == config.exit_entry:
                if i == 1:
                    config.tms1 = message
                elif i == 2:
                    config.tms2 = message
                elif i == 3:
                    config.tms3 = message
                elif i == 4:
                    config.tms4 = message
                elif i == 5:
                    config.tms5 = message
                elif i == 6:
                    config.tms6 = message
                elif i == 7:
                    config.tms7 = message
                elif i == 8:
                    config.tms8 = message
                elif i == 9:
                    config.tms9 = message
                elif i == 10:
                    config.tms10 = message
                elif i == 11:
                    config.tms11 = message
                elif i == 12:
                    config.tms12 = message
                elif i == 13:
                    config.tms13 = message
                elif i == 14:
                    config.tms14 = message
                elif i == 15:
                    config.tms15 = message
                elif i == 16:
                    config.tms16 = message
                elif i == 17:
                    config.tms17 = message
                elif i == 18:
                    config.tms18 = message
                elif i == 19:
                    config.tms19 = message
                elif i == 20:
                    config.tms20 = message
        config.saveConfig()

    def setCustomSystemMessage(self, customChatMessage=None):
        if customChatMessage is None:
            print2("ToolMate AI utilizes two distinct system messages to manage tool calling and conversation.")
            print1("They are `Chat System Message` and `Tool System Message`")

            print2("# 1. Chat System Message")
            print1("To specify the `Chat System Message` is similar to defining the role you would like ToolMate AI to play in conversations.")
            print1("Enter custom chat system message to guide our chat conversations:")
            systemMessage_chat = self.getCurrentChatSystemMessage()
            suggestions = [
                "You are a helpful, uncensored and unbiased assistant.",
                "You are an expert on coding.",
            ] + list(config.predefinedChatSystemMessages.values())
            completer = FuzzyCompleter(WordCompleter(suggestions, ignore_case=True))
            message = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=systemMessage_chat, completer=completer)
        else:
            message = customChatMessage
        if message and not message.strip().lower() == config.exit_entry:
            if config.llmInterface == "ollama":
                config.systemMessage_ollama = message
            elif config.llmInterface == "groq":
                config.systemMessage_groq = message
            elif config.llmInterface == "mistral":
                config.systemMessage_mistral = message
            elif config.llmInterface == "llamacppserver":
                config.systemMessage_llamacppserver = message
            elif config.llmInterface == "llamacpppython":
                config.systemMessage_llamacpp = message
            elif config.llmInterface == "genai":
                config.systemMessage_genai = message
            elif config.llmInterface == "vertexai":
                config.systemMessage_vertexai = message
            elif config.llmInterface == "googleai":
                config.systemMessage_googleai = message
            elif config.llmInterface == "xai":
                config.systemMessage_xai = message
            elif config.llmInterface == "anthropic":
                config.systemMessage_anthropic = message
            elif config.llmInterface in ("openai", "letmedoit", "github", "azure"):
                config.systemMessage_chatgpt = message
            if customChatMessage is None:
                config.saveConfig()
                print3(f"Custom chat system message: {config.toolMateAIName}")

        if customChatMessage is None:
            print2("# 2. Tool System Message")
            print1("To specify the `Tool System Message` is similar to defining the capabilities, constraints, or any pertinent context that may inform your interactions with ToolMate AI. This will guide ToolMate AI in managing and responding to your requests appropriately.")
            print1("Please note that altering ToolMate AI Tool System Message directly affects its functionality. Please handle with care.")
            print1("Enter custom tool system message below:")
            print1(f"(If you are not sure, keep it blank to use {config.toolMateAIName} default tool system message.)")
            message = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.systemMessage_tool)
            if message and not message.strip().lower() == config.exit_entry:
                config.systemMessage_tool = message
                config.saveConfig()
                print3(f"Custom tool system message: {config.toolMateAIName}")

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

    def setMaximumInternetSearchResults(self):
        print1("Please specify the maximum number of search results to be retrieved from the internet:")
        print1("(This value is applied in plugins `search google`, `search google news` and `search searxng`.)")
        maximumInternetSearchResults = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.maximumInternetSearchResults))
        if maximumInternetSearchResults and not maximumInternetSearchResults.strip().lower() == config.exit_entry and int(maximumInternetSearchResults) >= 0:
            config.maximumInternetSearchResults = int(maximumInternetSearchResults)
            config.saveConfig()
            print3(f"Maximum number of online search results: {config.maximumInternetSearchResults}")

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
        print2("# Maximum Python Code Auto-correction")
        print1(f"The auto-correction feature enables {config.toolMateAIName} to automatically fix the Python codes that are not executed properly.")
        print1("Please specify maximum number of auto-correction attempts below:")
        print1("(Remarks: Enter '0' if you want to disable auto-correction feature)")
        maxAutoCorrect = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.max_consecutive_auto_correction))
        if maxAutoCorrect and not maxAutoCorrect.strip().lower() == config.exit_entry and int(maxAutoCorrect) >= 0:
            config.max_consecutive_auto_correction = int(maxAutoCorrect)
            config.saveConfig()
            print3(f"Maximum consecutive auto-correction: {config.max_consecutive_auto_correction}")

    def setMinTokens(self):
        print1("Please specify minimum output tokens below:")
        print1("(applicable to 'openai', 'github', 'azure' and 'letmedoit' interfaces only)")
        mintokens = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.chatGPTApiMinTokens))
        if mintokens and not mintokens.strip().lower() == config.exit_entry and int(mintokens) > 0:
            config.chatGPTApiMinTokens = int(mintokens)
            if config.chatGPTApiMinTokens > config.chatGPTApiMaxTokens:
                config.chatGPTApiMinTokens = config.chatGPTApiMaxTokens
            config.saveConfig()
            print3(f"Minimum output tokens: {config.chatGPTApiMinTokens}")

    def getMaxTokens(self):
        contextWindowLimit = chatgptTokenLimits[config.chatGPTApiModel]
        functionTokens = count_tokens_from_functions(config.toolFunctionSchemas.values())
        maxToken = contextWindowLimit - functionTokens - config.chatGPTApiMinTokens
        if maxToken > 65536 and config.chatGPTApiModel in (
            "o1-mini",
        ):
            maxToken = 32768
        elif maxToken > 32768 and config.chatGPTApiModel in (
            "o1-preview",
        ):
            maxToken = 32768
        elif maxToken > 16384 and config.chatGPTApiModel in (
            "gpt-4o",
            "gpt-4o-mini",
        ):
            maxToken = 16384
        elif maxToken > 8192 and config.chatGPTApiModel in (
            "gpt-4",
        ):
            maxToken = 8192
        elif maxToken > 4096 and config.chatGPTApiModel in (
            "gpt-4-turbo",
            "gpt-3.5-turbo",
        ):
            maxToken = 4096
        return contextWindowLimit, functionTokens, maxToken

    def setGpuLayers(self, feature="default"):
        if not config.llmInterface in ("llamacpppython",):
            print1("Option `GPU Layers` applies to backend `llamacpp` only.")
            return None
        print1("Please specify the number of layers to store in VRAM (-1: all layers ):")
        if config.llmInterface == "llamacpppython":
            default = config.llamacppChatModel_n_gpu_layers if feature == "chat" else config.llamacppToolModel_n_gpu_layers
        gpuLayers = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(default))
        if gpuLayers and not gpuLayers.strip().lower() == config.exit_entry and int(gpuLayers) >= -1:
            gpuLayers = int(gpuLayers)
            if config.llmInterface == "llamacpppython":
                if feature == "chat":
                    config.llamacppChatModel_n_gpu_layers = gpuLayers
                else:
                    config.llamacppToolModel_n_gpu_layers = gpuLayers
            config.saveConfig()
            print3(f"GPU Layers: {gpuLayers}")

    def getCurrentContextWindowSize(self, feature="default"):
        if config.llmInterface == "llamacpppython":
            default = config.llamacppChatModel_n_ctx if feature == "chat" else config.llamacppToolModel_n_ctx
        elif config.llmInterface == "ollama":
            default = config.ollamaChatModel_num_ctx if feature == "chat" else config.ollamaToolModel_num_ctx
        else:
            default = ""
        return default

    def setContextWindowSize(self, feature="default", customContextWindowSize=None):
        if not config.llmInterface in ("llamacpppython", "ollama"):
            print2("Option `Context window size` applies to backends `llamacpp` and `ollama` only!")
            return None
        if customContextWindowSize is None:
            default = self.getCurrentContextWindowSize(feature=feature)
            print1("Please specify context window size below:")
            contextWindowSize = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(default))
        else:
            contextWindowSize = str(customContextWindowSize)
        if contextWindowSize and not contextWindowSize.strip().lower() == config.exit_entry and int(contextWindowSize) >= 0:
            contextWindowSize = int(contextWindowSize)
            if config.llmInterface == "llamacpppython":
                if feature == "chat":
                    config.llamacppChatModel_n_ctx = contextWindowSize
                else:
                    config.llamacppToolModel_n_ctx = contextWindowSize
            elif config.llmInterface == "ollama":
                if feature == "chat":
                    config.ollamaChatModel_num_ctx = contextWindowSize
                else:
                    config.ollamaToolModel_num_ctx = contextWindowSize
            if customContextWindowSize is None:
                config.saveConfig()
                print3(f"Context Window Size: {contextWindowSize}")

    def getCurrentMaxTokens(self, feature="default", showMessage=True):
        if config.llmInterface == "genai":
            if showMessage:
                print1("Visit https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models to read about tokens limits")
            currentMaxTokens = config.genai_max_output_tokens
        elif config.llmInterface == "vertexai":
            if showMessage:
                print1("Visit https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models to read about tokens limits")
            currentMaxTokens = config.vertexai_max_output_tokens
        elif config.llmInterface == "googleai":
            if showMessage:
                print1("Visit https://ai.google.dev/gemini-api/docs/models/gemini to read about tokens limits")
            currentMaxTokens = config.googleaiApi_tool_model_max_tokens
        elif config.llmInterface == "xai":
            if showMessage:
                print1("Visit https://docs.x.ai/docs#models to read about tokens limits. In our latest test, the maximum value accepts 127999.")
            currentMaxTokens = config.xaiApi_tool_model_max_tokens
        elif config.llmInterface in ("llamacpppython", "llamacppserver"):
            currentMaxTokens = config.llamacppChatModel_max_tokens if feature == "chat" else config.llamacppToolModel_max_tokens
        elif config.llmInterface == "ollama":
            currentMaxTokens = config.ollamaChatModel_num_predict if feature == "chat" else config.ollamaToolModel_num_predict
        elif config.llmInterface == "groq":
            if showMessage:
                print1("Visit https://console.groq.com/docs/models to read about tokens limits")
            currentMaxTokens = config.groqApi_chat_model_max_tokens if feature == "chat" else config.groqApi_tool_model_max_tokens
        elif config.llmInterface == "mistral":
            if showMessage:
                print1("Visit https://console.mistral.ai/limits/ to read about tokens limits")
            currentMaxTokens = config.mistralApi_chat_model_max_tokens if feature == "chat" else config.mistralApi_tool_model_max_tokens
        elif config.llmInterface == "anthropic":
            if showMessage:
                print1("Visit https://docs.anthropic.com/en/api/rate-limits#updated-rate-limits to read about tokens limits")
            currentMaxTokens = config.anthropicApi_tool_model_max_tokens if feature == "chat" else config.anthropicApi_tool_model_max_tokens
        elif config.llmInterface in ("openai", "letmedoit", "github", "azure"):
            if showMessage:
                url = "https://docs.github.com/en/github-models/prototyping-with-ai-models#rate-limits" if config.llmInterface == "github" else "https://platform.openai.com/docs/models"
                print1(f"Visit {url} to read about tokens limits")
            currentMaxTokens = config.chatGPTApiMaxTokens
        return currentMaxTokens

    def setMaxTokens_non_chatgpt(self, feature="default", customMaxtokens=None):
        if customMaxtokens is None:
            default = self.getCurrentMaxTokens(feature=feature)
            print1("Please specify maximum output tokens below:")
            maxtokens = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(default))
        else:
            maxtokens = str(customMaxtokens)
        if maxtokens and not maxtokens.strip().lower() == config.exit_entry and int(maxtokens) >= -1:
            maxtokens = int(maxtokens)
            if config.llmInterface == "genai":
                config.genai_max_output_tokens = maxtokens
            elif config.llmInterface == "vertexai":
                config.vertexai_max_output_tokens = maxtokens
            elif config.llmInterface == "googleai":
                config.googleaiApi_tool_model_max_tokens = maxtokens
            elif config.llmInterface == "xai":
                config.xaiApi_tool_model_max_tokens = maxtokens
            elif config.llmInterface == "anthropic":
                config.anthropicApi_tool_model_max_tokens = maxtokens
            elif config.llmInterface in ("llamacpppython", "llamacppserver"):
                if feature == "chat":
                    config.llamacppChatModel_max_tokens = maxtokens
                else:
                    config.llamacppToolModel_max_tokens = maxtokens
            elif config.llmInterface == "ollama":
                if feature == "chat":
                    config.ollamaChatModel_num_predict = maxtokens
                else:
                    config.ollamaToolModel_num_predict = maxtokens
            elif config.llmInterface == "groq":
                if feature == "chat":
                    config.groqApi_chat_model_max_tokens = maxtokens
                else:
                    config.groqApi_tool_model_max_tokens = maxtokens
            elif config.llmInterface == "mistral":
                if feature == "chat":
                    config.mistralApi_chat_model_max_tokens = maxtokens
                else:
                    config.mistralApi_tool_model_max_tokens = maxtokens
            if customMaxtokens is None:
                config.saveConfig()
                print3(f"Maximum output tokens: {maxtokens}")

    def setMaxTokens(self, feature="default", customMaxtokens=None):
        # non-chatgpt settings
        if not config.llmInterface in ("openai", "letmedoit", "github", "azure"):
            self.setMaxTokens_non_chatgpt(feature=feature, customMaxtokens=customMaxtokens)
            return None
        # chatgpt settings
        contextWindowLimit, functionTokens, tokenLimit = self.getMaxTokens()
        if customMaxtokens is None:
            if tokenLimit < config.chatGPTApiMinTokens:
                print2(f"Function tokens [{functionTokens}] exceed {config.chatGPTApiModel} output token limit.")
                print1("Either change to a model with higher token limit or disable unused function-call plguins.")
                maxtokens = config.exit_entry
            else:
                print1(self.divider)
                print1("GPT and embeddings models process text in chunks called tokens. As a rough rule of thumb, 1 token is approximately 4 characters or 0.75 words for English text. One limitation to keep in mind is that for a GPT model the prompt and the generated output combined must be no more than the model's maximum context length.")
                print1("Visit https://platform.openai.com/docs/models to read about tokens limits")
                print3(f"Current GPT model: {config.chatGPTApiModel}")
                print3(f"Maximum context length: {contextWindowLimit}")
                print3(f"Current function tokens: {functionTokens}")
                print3(f"Maximum output token allowed (excl. functions): {tokenLimit}")
                print1(self.divider)
                print1("Please specify maximum output tokens below:")
                maxtokens = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.chatGPTApiMaxTokens))
        else:
            maxtokens = str(customMaxtokens)
        if maxtokens and not maxtokens.strip().lower() == config.exit_entry and int(maxtokens) > 0:
            config.chatGPTApiMaxTokens = int(maxtokens)
            if config.chatGPTApiMaxTokens > tokenLimit:
                config.chatGPTApiMaxTokens = tokenLimit
            if customMaxtokens is None:
                config.saveConfig()
                print3(f"Maximum output tokens: {config.chatGPTApiMaxTokens}")
        if customMaxtokens is None:
            self.setMinTokens()
            self.setDynamicTokenCount()

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
        print1("* on Android Termux, e.g.:\n'termux-tts-speak' or 'termux-tts-speak -r 1.3'")
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

    def toggleDeveloperMode(self):
        config.developer = not config.developer
        config.saveConfig()
        print3(f"Developer mode: '{'enabled' if config.developer else 'disabled'}'!")

    def toggleInputImprovement(self):
        config.improveInputEntry = not config.improveInputEntry
        if config.improveInputEntry:
            print1("Please specify the writing style below:")
            style = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.improvedWritingSytle)
            if style and not style in (config.exit_entry, config.cancel_entry):
                config.improvedWritingSytle = style
                config.saveConfig()
        print3(f"Improve Input Entry: '{'enabled' if config.improveInputEntry else 'disabled'}'!")

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
        options = ["edge", "elevenlabs", "custom"] if config.isLite else ["edge", "google", "googlecloud", "elevenlabs", "custom"]
        descriptions = ["Microsoft Server Text-to-Speech", "ElevenLabs (credentials required)", "Custom Text-to-Speech Command [advanced]"] if config.isTermux else ["Microsoft Server Text-to-Speech", "Google Text-to-Speech (generic)", "Google Text-to-Speech (credentials required)", "ElevenLabs (credentials required)", "Custom Text-to-Speech Command [advanced]"]
        if config.isTermux and shutil.which("termux-tts-speak"):
            options.insert(0, "android")
            descriptions.insert(0, "Android Text-to-Speech")
        elif config.thisPlatform == "Linux" and not config.isTermux:
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
                print3("Read: https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Google%20Cloud%20Service%20Credential%20Setup.md")
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
                print3("Read: https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Offline%20TTS%20-%20Linux.md")
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
                print3("Read: https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Offline%20TTS%20-%20Windows.md")
        elif config.ttsPlatform == "elevenlabs":
            if not config.elevenlabsApi:
                self.changeElevenlabsApi()
            if not config.elevenlabsApi:
                print1("ElevenLabs API key not found!")
                print3("Text-to-Speech platform changed to: Google Text-to-Speech (Generic)")
                config.ttsPlatform = "google"
            else:
                self.setElevenlabsVoice()
        elif config.ttsPlatform == "edge":
            self.setEdgeTtsVoice()
        elif config.ttsPlatform == "android":
            self.setAndroidTtsVoice()
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
        if config.isLite:
            print1("This feature is not supported in Lite version.")
        if config.isTermux:
            print1("You may simply use the Android built-in voice typing feature.")
            return None
        voiceTypingPlatform = self.dialogs.getValidOptions(
            options=("google", "googlecloud", "whisper", "whispercpp", "vosk"),
            descriptions=("Google Speech-to-Text (generic) [online]", "Google Speech-to-Text (credentials required) [online]", "OpenAI Whisper [offline; slower with non-English voices]", "Whisper.cpp [offline; installed separately]", "Vosk Speech Recognition Toolkit [offline]"),
            title="Voice Recognition Configurations",
            text="Select a speech-to-text platform:",
            default=config.voiceTypingPlatform,
        )
        if voiceTypingPlatform:
            if voiceTypingPlatform == "googlecloud" and not (os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Speech-to-Text" in config.enabledGoogleAPIs):
                print2("Google Cloud Speech-to-Text feature is not enabled!")
                print3("Read: https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Google%20Cloud%20Service%20Credential%20Setup.md")
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
        if config.voiceTypingPlatform == "vosk":
            self.setVoskModel()
        else:
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
        print3(f"Speech-to-Text Platform: {config.voiceTypingPlatform}")
        if config.voiceTypingPlatform == "vosk":
            print3(f"Vosk Model: {config.voskModel}")
        else:
            print3(f"Speech-to-Text Language: {config.voiceTypingLanguage}")
        print3(f"Ambient Noise Adjustment: {config.voiceTypingAdjustAmbientNoise}")
        print3(f"Audio Notification: {config.voiceTypingNotification}")
        print3(f"Auto Completion: {config.voiceTypingAutoComplete}")
        # save configs
        config.saveConfig()

    def saveAsChat(self, messages):

        filePath = self.getPath.getFilePath(
            empty_to_cancel=True,
            list_content_on_directory_change=True,
            keep_startup_directory=True,
            message=f"{self.divider}\nEnter a file name or a file path:",
        )
        if filePath:
            if not "." in os.path.basename(filePath):
                filePath = f"{filePath}.txt"
                workflowPath = f"{filePath}_workflow.txt"
            else:
                workflowPath = re.sub(r"(\.[^\.]+?)$", r"_workflow\1", filePath)
            try:
                dirname = os.path.dirname(filePath)
                if not dirname:
                    dirname = os.getcwd()
                Path(dirname).mkdir(parents=True, exist_ok=True)
                if os.path.isdir(dirname):
                    if os.path.isfile(filePath):
                        # overwrite existing file?
                        options = ("yes", "no")
                        question = "Given file path exists! Would you like to overwrite it?"
                        print1(question)
                        overwrite = self.dialogs.getValidOptions(
                            options=options,
                            title="Overwrite?",
                            default="no",
                            text=question,
                        )
                        if not overwrite == "yes":
                            return None
                    with open(filePath, "w", encoding="utf-8") as fileObj:
                        fileObj.write(pprint.pformat([i for i in messages if i.get("role", "") in ("user", "assistant")]))
                        print3(f"Conversation saved: {filePath}")
                        config.last_conversation = filePath
                    with open(workflowPath, "w", encoding="utf-8") as fileObj:
                        fileObj.write(self.getCurrentWorkflow())
                        print3(f"Workflow saved: {workflowPath}")
                        config.last_workflow = workflowPath
                    config.saveConfig()
                    if shutil.which("termux-share"):
                        cli = f'''termux-share -a send "{filePath}"'''
                        subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    elif shutil.which(config.open):
                        os.system(f"{config.open} {filePath}")
            except:
                print2("Failed to save the conversation!\n")
                showErrors()

    def saveChat(self, messages):
        if config.conversationStarted:
            messagesCopy = copy.deepcopy(messages)
            timestamp = getCurrentDateTime()

            if hasattr(config, "save_chat_record"):
                # when plugin "save chat records" is enabled
                #messageLength = len(messagesCopy)
                for order, i in enumerate(messagesCopy):
                    #isLastItem = (order == (messageLength - 1))
                    config.save_chat_record(timestamp, order, i)

            try:
                folderPath = os.path.join(config.localStorage, "chats", re.sub("^([0-9]+?-[0-9]+?)-.*?$", r"\1", timestamp))
                Path(folderPath).mkdir(parents=True, exist_ok=True)
                if os.path.isdir(folderPath):
                    chatFile = os.path.join(folderPath, f"{timestamp}.txt")
                    with open(chatFile, "w", encoding="utf-8") as fileObj:
                        fileObj.write(pprint.pformat([i for i in messagesCopy if i.get("role", "") in ("user", "assistant")]))
                        print3(f"Conversation saved: {chatFile}")
                        config.last_conversation = chatFile
                    workflowFile = os.path.join(folderPath, f"{timestamp}_workflow.txt")
                    with open(workflowFile, "w", encoding="utf-8") as fileObj:
                        fileObj.write(self.getCurrentWorkflow())
                        print3(f"Workflow saved: {workflowFile}")
                        config.last_workflow = workflowFile
                    config.saveConfig()
            except:
                print2("Failed to save the conversation!\n")
                showErrors()

    def exportChat(self, messages, filePath=""):
        if config.conversationStarted:
            plainText = ""
            for i in messages:
                role = i.get("role", "")
                content = i.get("content", "")
                if role in ("user", "assistant"):
                    plainText += f"```{role}\n{content.rstrip()}\n```\n"
            if not filePath:
                filePath = self.getPath.getFilePath(
                    empty_to_cancel=True,
                    list_content_on_directory_change=True,
                    keep_startup_directory=True,
                    message=f"{self.divider}\nEnter a file name or a file path:",
                )
            if filePath:
                if not "." in os.path.basename(filePath):
                    filePath = f"{filePath}.txt"
                    workflowPath = f"{filePath}_workflow.txt"
                else:
                    workflowPath = re.sub(r"(\.[^\.]+?)$", r"_workflow\1", filePath)
                try:
                    dirname = os.path.dirname(filePath)
                    if not dirname:
                        dirname = os.getcwd()
                    Path(dirname).mkdir(parents=True, exist_ok=True)
                    if os.path.isdir(dirname):
                        if os.path.isfile(filePath):
                            # overwrite existing file?
                            options = ("yes", "no")
                            question = "Given file path exists! Would you like to overwrite it?"
                            print1(question)
                            overwrite = self.dialogs.getValidOptions(
                                options=options,
                                title="Overwrite?",
                                default="no",
                                text=question,
                            )
                            if not overwrite == "yes":
                                return None
                        with open(filePath, "w", encoding="utf-8") as fileObj:
                            fileObj.write(plainText)
                            print3(f"Conversation exported: {filePath}")
                        with open(workflowPath, "w", encoding="utf-8") as fileObj:
                            fileObj.write(self.getCurrentWorkflow())
                            print3(f"Workflow exported: {workflowPath}")
                        if shutil.which("termux-share"):
                            cli = f'''termux-share -a send "{filePath}"'''
                            subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        elif shutil.which(config.open):
                            os.system(f"{config.open} {filePath}")
                except:
                    print2("Failed to export the conversation!\n")
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

    def selectTool(self, title="Tools", text="Select a tool:", default=None):
        #config.allEnabledTools
        return self.dialogs.getValidOptions(
            options=sorted(config.allEnabledTools),
            title=title,
            default=default if default is not None else config.defaultTool,
            text=text,
        )

    def setDefaultTool(self):
        tool = self.selectTool(title="Default Tool", text="Select the default tool:")
        if tool:
            config.defaultTool = tool
            config.saveConfig()

    def setTmtTools(self):
        #print2("# Setting custom tools for commands `tmt1 ... tmt20`")
        defaults = {
            1: config.tmt1,
            2: config.tmt2,
            3: config.tmt3,
            4: config.tmt4,
            5: config.tmt5,
            6: config.tmt6,
            7: config.tmt7,
            8: config.tmt8,
            9: config.tmt9,
            10: config.tmt10,
            11: config.tmt11,
            12: config.tmt12,
            13: config.tmt13,
            14: config.tmt14,
            15: config.tmt15,
            16: config.tmt16,
            17: config.tmt17,
            18: config.tmt18,
            19: config.tmt19,
            20: config.tmt20,
        }
        for i in range(1,21):
            tool = self.selectTool(title=f"`tmt{i}` tool", text=f"Configure a tool for running with command `tmt{i}`:", default=defaults.get(i))
            if tool:
                if i == 1:
                    config.tmt1 = tool
                elif i == 2:
                    config.tmt2 = tool
                elif i == 3:
                    config.tmt3 = tool
                elif i == 4:
                    config.tmt4 = tool
                elif i == 5:
                    config.tmt5 = tool
                elif i == 6:
                    config.tmt6 = tool
                elif i == 7:
                    config.tmt7 = tool
                elif i == 8:
                    config.tmt8 = tool
                elif i == 9:
                    config.tmt9 = tool
                elif i == 10:
                    config.tmt10 = tool
                elif i == 11:
                    config.tmt11 = tool
                elif i == 12:
                    config.tmt12 = tool
                elif i == 13:
                    config.tmt13 = tool
                elif i == 14:
                    config.tmt14 = tool
                elif i == 15:
                    config.tmt15 = tool
                elif i == 16:
                    config.tmt16 = tool
                elif i == 17:
                    config.tmt17 = tool
                elif i == 18:
                    config.tmt18 = tool
                elif i == 19:
                    config.tmt19 = tool
                elif i == 20:
                    config.tmt20 = tool
        config.saveConfig()

    def insertPredefinedContext(self):
        contexts = list(config.predefinedContexts.keys())
        predefinedContext = self.dialogs.getValidOptions(
            options=contexts,
            title="Predefined Contexts",
            default=config.predefinedContext,
            text="Select a predefined context:",
        )
        if predefinedContext:
            config.predefinedContext = predefinedContext
            if config.predefinedContext == "custom":
                print1("Edit custom context below:")
                customContext = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.customPredefinedContext)
                if customContext and not customContext.strip().lower() == config.exit_entry:
                    config.customPredefinedContext = customContext.strip()
        else:
            # a way to quickly clean up context
            config.predefinedContext = "custom"
        config.saveConfig()
        config.defaultEntry = f"@chat `{config.predefinedContext}` "

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
        appName = config.appName if config.appName else config.toolMateAIName.split()[0].upper()
        terminal_width = shutil.get_terminal_size().columns
        try:
            from art import text2art
            if terminal_width >= 32:
                logo = text2art(appName, font=config.text2art_font1)
            elif terminal_width >= 20:
                logo = text2art(" ".join(appName) + " ", font=config.text2art_font2)
            else:
                logo = config.toolMateAIName
            logo = logo[:-1] # remove the linebreak at the end
        except:
            logo = config.toolMateAIName
        print_formatted_text(HTML(f"<{config.terminalCommandEntryColor2}>{logo}</{config.terminalCommandEntryColor2}>"))

    def runPythonScript(self, script):
        # Create a StringIO object to capture the output
        thisOutput = StringIO()
        # Redirect stdout to the StringIO object
        old_stdout = sys.stdout
        sys.stdout = thisOutput

        script = re.sub("^```(.+?)```", r"\1", script)
        try:
            exec(script, globals())
            # Restore the original stdout
            sys.stdout = old_stdout

            config.toolTextOutput = thisOutput.getvalue()
            if not config.toolTextOutput.strip():
                config.toolTextOutput = getPythonFunctionResponse()
            return ""
        except:
            # Restore the original stdout
            sys.stdout = old_stdout

            trace = traceback.format_exc()
            print(trace if config.developer else "Error encountered!")
            print1(config.divider)
            if config.max_consecutive_auto_correction > 0:
                return CallLLM.autoCorrectPythonCode(script, trace)
            else:
                return "[INVALID]"

    def improveWriting(self, writing: str):
        # Feature: improve writing:
        if writing:
            writing = re.sub(r"\n\[Current time: [^\n]*?$", "", writing)
            improvedVersion = CallLLM.getSingleChatResponse(f"""Improve the following writing, according to {config.improvedWritingSytle}.
Remember, provide me with the improved writing only, enclosed in triple quotes ``` and without any additional information or comments.
My writing:
{writing}""", prefill="```\n", stop=["```"])
            if improvedVersion:
                writing = improvedVersion[3:-3] if improvedVersion.startswith("```") and improvedVersion.endswith("```") else re.sub("^.*?```(.*?)```.*?$", r"\1", improvedVersion)
                try:
                    print2(writing)
                except:
                    print(f"```\n{writing}\n```")
        return writing

    def generateTermuxAPICommand(self, request: str):
        instruction = f"""# Instructions

* Generate a Termux API command line to resolve `My Request` given below.
* Remember, provide me with the generated command line ONLY, without additional notes or explanations.
* Enclose the command line with triple backticks ``` at the beginning and at the end of the command line in your output.

# My Request

{request}"""
        cli = CallLLM.getSingleChatResponse(instruction, prefill="```\n", stop=["```"], keepSystemMessage=True)
        if cli := cli.strip():
            cli = cli[3:-3].strip() if cli.startswith("```") and cli.endswith("```") else re.sub("^.*?```(.*?)```.*?$", r"\1", cli).strip()
        if config.developer:
            print2(f"```command")
            print(cli)
            print2(f"```")
        return cli

    def generateSystemCommand(self, request: str):
        distro = f" '{config.thisDistro}'" if config.thisDistro else ""
        instruction = f"""# Instructions

* Generate a system command line, that works on {config.thisPlatform}{distro}, to resolve `My Request` given below.
* Remember, provide me with the generated system command line ONLY, without additional notes or explanations.
* Enclose the system command line with triple backticks ``` at the beginning and at the end of the command line in your output.

# My Request

{request}"""
        cli = CallLLM.getSingleChatResponse(instruction, prefill="```\n", stop=["```"], keepSystemMessage=True)
        if cli := cli.strip():
            cli = extractSystemCommand(cli).strip()
        if config.developer:
            print2(f"```command")
            print(cli)
            print2(f"```")
        return cli

    def riskAssessment(self, content: str, target="python code"):
        instruction = f"""# Instructions

* You are a senior {target} engineer.
* Assess the risk level (high / medium / low) of damaging my device upon executing the `{target.capitalize()}` that I will provide for you. For examples, file deletions or similar significant impacts are regarded as ```high``` level.
* Enclose the risk level with triple backticks ```
* Answer me either ```high``` or ```medium``` or ```low``` ONLY, without additional notes or explanations.

Acess the risk level of the following `{target.capitalize()}`:

# {target.capitalize()}

{content}"""
        risk = CallLLM.getSingleChatResponse(instruction, temperature=0.0, prefill="```\n", stop=["```"], keepSystemMessage=True)
        if risk := risk.strip():
            risk = risk[3:-3].strip() if risk.startswith("```") and risk.endswith("```") else re.sub("^.*?```(.*?)```.*?$", r"\1", risk).strip()
        if "high" in risk:
            risk = "high"
        elif "medium" in risk:
            risk = "medium"
        elif "low" in risk:
            risk = "low"
        else:
            risk = "high"
        showRisk(risk)
        if confirmExecution(risk):
            if hasattr(config, "api_server_id"):
                return f"#{risk}"
            print1("Do you want to continue? [y]es / [N]o")
            confirmation = prompt(style=config.promptStyle2, default="y")
            if not confirmation.lower() in ("y", "yes"):
                return ""
        return risk

    def convertRelativeDateTime(self, writing: str):
        # Feature: improve writing:
        if writing:
            writing = re.sub(r"\n\[Current time: [^\n]*?$", "", writing)
            if config.isLite:
                day_of_week = ""
            else:
                day_of_week = f" ({getDayOfWeek()})"
            improvedVersion = CallLLM.getSingleChatResponse(f"""# Instructions

* Convert any relative dates and times in `My writing`, into exact dates and times, based on the reference that current datetime is {str(datetime.datetime.now())}{day_of_week}.
* Provide me with the revised writing only, enclosed in triple quotes ``` and without any additional information or comments.
* If there is no change, return to my original writing to me, enclosed in triple quotes ``` and without any additional information or comments.

# My writing:

{writing}""", prefill="```\n", stop=["```"])
            if improvedVersion:
                writing = improvedVersion[3:-3] if improvedVersion.startswith("```") and improvedVersion.endswith("```") else re.sub("^.*?```(.*?)```.*?$", r"\1", improvedVersion)
                try:
                    print2(writing)
                except:
                    print(f"```\n{writing}\n```")
        return writing

    def processSingleAction(self, action: str, description: str, gui: bool=False) -> Optional[bool]:
        config.selectedTool = ""
        config.toolTextOutput = ""
        config.tempChatSystemMessage = ""

        def forceLoadingInternetSearches():
            if config.loadingInternetSearches == "always":
                try:
                    config.currentMessages = CallLLM.runSingleFunctionCall(config.currentMessages, "search_google")
                except:
                    print1("Unable to load internet resources.")
                    showErrors()

        # backward compatibility to LetMeDoIt Mode
        # tool_selection_agent applies only to backends other than LetMeDoIt Mode

        if action == "recommend_tool" and config.llmInterface == "letmedoit":
            # tool `recommend_tool` is not supported in LetMeDoIt mode
            action = "chat"

        # append chat
        if action == "append_instruction":
            description = f'''description\n{getAssistantPreviousResponse()[0]}'''
            action = "chat"

        # Force Improve Writing
        if config.improveInputEntry:
            description = self.improveWriting(description)

        if action == "chat":
            # check for a predefined system message
            predefinedChatSystemMessages = "|".join(config.predefinedChatSystemMessages.keys())
            searchSystemMessage = re.search(f"`({predefinedChatSystemMessages})`", description)
            if searchSystemMessage:
                systemMessageKey = searchSystemMessage.group(1)
                config.tempChatSystemMessage = config.predefinedChatSystemMessages.get(systemMessageKey)
                description = re.sub(f"`{systemMessageKey}`", "", description)
            elif description.lstrip().startswith("-p_"): # fabric pattern
                pattern, description = description.lstrip().split(" ", 1)
                pattern = pattern[3:]
                if tempChatSystemMessage := getFabricPatternSystem(pattern):
                    config.tempChatSystemMessage = tempChatSystemMessage
            # check for a predefined context
            predefinedContexts = "|".join(config.predefinedContexts.keys())
            searchPredefinedContext = re.search(f"`({predefinedContexts})`", description)
            if searchPredefinedContext:
                config.predefinedContext = searchPredefinedContext.group(1)
                config.saveConfig()
                description = re.sub(f"`{config.predefinedContext}`", "", description)
                description = self.addPredefinedContext(description)
                # check if the new description call a particular tool
                searchTool = re.search(rf"^{config.toolPattern}([\d\D]*?)$", description.lstrip())
                if searchTool:
                    action = searchTool.group(1)
                    description = searchTool.group(2)

        if action in config.deviceInfoPlugins:
            description = f"""Context: Today is {config.dayOfWeek}. The current date and time here in {config.state}, {config.country} is {str(datetime.datetime.now())}.
{description}"""

        # Convert relative datetime
        if action in config.datetimeSensitivePlugins:
            description = self.convertRelativeDateTime(description).strip()

        # Run TTS to read action content
        if config.ttsInput:
            TTSUtil.play(description)

        config.currentMessages.append({"role": "user", "content": description})

        # check if user specify a tool
        if action == "chat":
            # chat feature only
            forceLoadingInternetSearches()
            runLLM = True
        elif action == "recommend_tool":
            print1("Sure, I am reviewing all currently enabled tools before providing my recommendation ...")
            Plugins.checkAvailableTools(display=False, includeRequirements=config.tool_selection_requirements)
            config.currentMessages[-1]["content"] = f"""Recommend which is the best `Tool` that can resolve `My Requests`. Each tool listed below is prefixed with "@" followed by their descriptions.

{config.toolTextOutput}

# My Request

{description}"""
            completion = CallLLM.regularCall(config.currentMessages)
            self.streamCompletion(completion)
            if config.tool_selection_agent:
                message, _ = getAssistantPreviousResponse()
                recommendation = message.replace("\\", "")
                keyword_processor = KeywordProcessor()
                keyword_processor.add_keywords_from_list(config.allEnabledTools)
                recommended_tools = removeDuplicatedListItems(keyword_processor.extract_keywords(recommendation))
                if config.auto_tool_selection:
                    selectedTool = recommended_tools[0]
                else:
                    selectedTool = selectTool(recommended_tools)
                if selectedTool:
                    action = selectedTool
                    # remove the tool selection message
                    config.currentMessages = config.currentMessages[:-2]
                    self.runSingleAction(action, description, gui)
            return None
        elif action == "extract_python_code":
            # extract
            python_code = extractPythonCode(description)
            content = f'''```python
{python_code}
```''' if python_code else "Not found!"
            # display code
            print("")
            displayPythonCode(python_code) if python_code else print1(content)
            # update main message chain
            config.currentMessages[-1]["content"] = f"Extract the python code in:\n\n{description}"
            config.currentMessages.append({"role": "assistant", "content": content})
            return None
        elif action == "execute_python_code":
            # extract
            python_code = extractPythonCode(description)
            if not python_code:
                message = "Python code not found!"
            else:
                # execute
                response = self.runPythonScript(python_code)
                if config.toolTextOutput.strip():
                    config.toolTextOutput = refineToolTextOutput(config.toolTextOutput)
                    message = config.toolTextOutput
                    config.toolTextOutput = ""
                elif not response:
                    message = "Done!"
                elif response == "[INVALID]":
                    message = "Failed to execute!"
                else:
                    message = response
            print1(f"\n{message}")
            config.currentMessages[-1]["content"] = f"Run the python code in:\n\n{description}"
            config.currentMessages.append({"role": "assistant", "content": message})
            return None
        elif action == "list_current_directory_contents":
            dirs, files = self.getPath.displayDirectoryContent()
            content = f'''# Directories

{dirs if dirs else "Not found!"}

# Files

{files if files else "Not found!"}'''
            config.currentMessages[-1]["content"] = f'''List contents in current directory {os.getcwd()}'''
            config.currentMessages.append({"role": "assistant", "content": content})
            return None
        elif action == "convert_relative_datetime":
            improvedWriting = self.convertRelativeDateTime(description).strip()
            if improvedWriting:
                print2("\n```improved")
                print(improvedWriting)
                print2("```\n")
                config.currentMessages[-1]["content"] = "Convert any relative dates and times in the following writing:\n\n```" + description + "\n```"
                config.currentMessages.append({"role": "assistant", "content": improvedWriting})
            else:
                config.currentMessages = config.currentMessages[:-1]
            return None
        elif action == "improve_writing":
            improvedWriting = self.improveWriting(description).strip()
            if improvedWriting:
                config.currentMessages[-1]["content"] = f"Improve the following writing, according to {config.improvedWritingSytle}:\n\n```" + description + "\n```"
                config.currentMessages.append({"role": "assistant", "content": improvedWriting})
            else:
                config.currentMessages = config.currentMessages[:-1]
            return None
        elif action == "termux" and config.isTermux:
            cli = description
            stdout, stderr = subprocess.Popen(description, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            if stderr and not stdout:
                cli = self.generateTermuxAPICommand(description)
                if risk := self.riskAssessment(cli, target="system command"):
                    if risk.startswith("#"): # api server running
                        config.currentMessages.append({"role": "assistant", "content": getPromptExecutionMessage(cli, risk, description="command")})
                        return None
                    stdout, stderr = subprocess.Popen(cli, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            # refine description
            description = f'''Run Termux command:\n```command\n{description}\n```'''
            config.currentMessages[-1]["content"] = description
            if stderr and not risk:
                done = "Cancelled!"
                config.currentMessages.append({"role": "assistant", "content": done})
                print2(done)
            elif stdout:
                print2("\n```output")
                print(stdout.strip())
                print2("```\n")
                config.currentMessages.append({"role": "assistant", "content": stdout.strip()})
            elif not stdout and not stderr:
                done = f"```executed\n{cli}\n```"
                config.currentMessages.append({"role": "assistant", "content": done})
                print2(done)
            elif stderr:
                print2("\n```error")
                print(stderr.strip())
                print2("```\n")
                done = f"```error\n{stderr.strip()}\n```" if config.developer else "Error encountered!"
                config.currentMessages.append({"role": "assistant", "content": done})
            return None
        elif action == "command":
            cli = extractSystemCommand(description)
            stdout, stderr = subprocess.Popen(cli, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            if stderr and not stdout:
                cli = self.generateSystemCommand(description)
                if risk := self.riskAssessment(cli, target="system command"):
                    if risk.startswith("#"): # api server running
                        config.currentMessages.append({"role": "assistant", "content": getPromptExecutionMessage(cli, risk, description="command")})
                        return None
                    stdout, stderr = subprocess.Popen(cli, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            # refine description
            description = f'''Run system command:\n```command\n{description}\n```'''
            config.currentMessages[-1]["content"] = description
            if stderr and not risk:
                done = "Cancelled!"
                config.currentMessages.append({"role": "assistant", "content": done})
                print2(done)
            elif stdout:
                print2("\n```output")
                print(stdout.strip())
                print2("```\n")
                config.currentMessages.append({"role": "assistant", "content": stdout.strip()})
            elif not stdout and not stderr:
                done = f"```executed\n{cli}\n```"
                config.currentMessages.append({"role": "assistant", "content": done})
                print2(done)
            elif stderr:
                print2("\n```error")
                print(stderr.strip())
                print2("```\n")
                done = f"```error\n{stderr.strip()}\n```" if config.developer else "Error encountered!"
                config.currentMessages.append({"role": "assistant", "content": done})
            return None
        elif action == "append_command":
            previousResponse = getAssistantPreviousResponse()[0]
            if previousResponse:
                previousResponse = previousResponse.replace('"', '\\"')
                description = f'''{description.strip()} "{previousResponse}"'''
                cli = extractSystemCommand(description)
                stdout, stderr = subprocess.Popen(cli, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                if stderr and not stdout:
                    cli = self.generateSystemCommand(description)
                    if risk := self.riskAssessment(cli, target="system command"):
                        if risk.startswith("#"): # api server running
                            config.currentMessages.append({"role": "assistant", "content": getPromptExecutionMessage(cli, risk, description="command")})
                            return None
                        stdout, stderr = subprocess.Popen(cli, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                description = f'''Run system command:\n```command\n{description}\n```'''
                config.currentMessages[-1]["content"] = description
                if stderr and not risk:
                    done = "Cancelled!"
                    config.currentMessages.append({"role": "assistant", "content": done})
                    print2(done)
                elif stdout:
                    print2("\n```output")
                    print(stdout.strip())
                    print2("```\n")
                    config.currentMessages.append({"role": "assistant", "content": stdout.strip()})
                elif not stdout and not stderr:
                    done = f"```executed\n{cli}\n```"
                    config.currentMessages.append({"role": "assistant", "content": done})
                    print2(done)
                elif stderr:
                    print2("\n```error")
                    print(stderr.strip())
                    print2("```\n")
                    done = f"```error\n{stderr.strip()}\n```" if config.developer else "Error encountered!"
                    config.currentMessages.append({"role": "assistant", "content": done})
            else:
                config.currentMessages = config.currentMessages[:-1]
            return None
        elif action == "search_searxng" and hasattr(config, "searx_tabs"):
            keyword_processor = KeywordProcessor()
            keyword_processor.add_keywords_from_list([i.rstrip() for i in config.searx_tabs])
            description = f"{description} "
            config.searx_categories = removeDuplicatedListItems(keyword_processor.extract_keywords(description))
            if config.searx_categories:
                searx_categories = " |".join(config.searx_categories)
                searx_categories_pattern = f"({searx_categories} )"
                description = re.sub(searx_categories_pattern, "", description)
            # passing parameters
            config.selectedTool = action
            config.currentMessages[-1]["content"] = description.rstrip()
            runLLM = True
        else:
            if action:
                # when user specify a tool
                config.selectedTool = action
                # notify devloper
                #if config.developer:
                #    print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Calling tool</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{config.selectedTool}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
                runLLM = True
            else:
                # no tool is specified
                config.selectedTool = ""
                forceLoadingInternetSearches()
                runLLM = True
        return runLLM

    def runSingleAction(self, action: str, description: str, gui: bool=False) -> bool:
        runLLM = self.processSingleAction(action, description, gui)
        if runLLM is not None:
            try:
                if not gui:
                    # start spinning in tui
                    config.stop_event = threading.Event()
                    config.spinner_thread = threading.Thread(target=spinning_animation, args=(config.stop_event,))
                    config.spinner_thread.start()
                completion = CallLLM.runToolCall(config.currentMessages)
                if not gui:
                    # stop spinning in tui
                    config.runPython = True
                    stopSpinning()
            except:
                stopSpinning()

                trace = traceback.format_exc()
                if "Please reduce the length of the messages or completion" in trace or "tokens" in trace:
                    print1("Maximum tokens reached!")
                elif config.developer:
                    print(self.divider)
                    print(trace)
                    print(self.divider)
                else:
                    print("Error encountered!")

                clear()
                previousRequest, _ = getUserPreviousRequest()
                config.defaultEntry = previousRequest
                print2("starting a new chat!")
                self.saveChat(config.currentMessages)
                return False
            return True if completion is None else self.streamCompletion(completion, gui)
        return True

    def streamCompletion(self, completion, gui: Optional[bool]=None, openai: Optional[bool]=None) -> bool:
        #if gui is None:
        #    gui = True if hasattr(config, "desktopAssistant") else False
        if openai is None:
            openai = True if config.llmInterface in ("openai", "letmedoit", "github", "azure", "googleai", "xai", "groq", "mistral", "llamacppserver") else False
        try:
            #if gui:
            #    QtResponseStreamer(config.desktopAssistant).workOnCompletion(completion, openai)
            #else:
                # Create a new thread for the streaming task
            streamingWordWrapper = StreamingWordWrapper()
            streaming_event = threading.Event()
            self.streaming_thread = threading.Thread(target=streamingWordWrapper.streamOutputs, args=(streaming_event, completion, openai))
            # Start the streaming thread
            self.streaming_thread.start()
            # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+z' to stop the streaming
            streamingWordWrapper.keyToStopStreaming(streaming_event)
            # when streaming is done or when user press "ctrl+q"
            self.streaming_thread.join()
        except:
            print(traceback.format_exc())
            return False
        return True

    def runMultipleActions(self, content: str, gui: bool=False):
        # check for any tool patterns
        actions = re.findall(config.toolPattern, f"{content} ") # add a space after `content` to allow tool entry at the end without a description
        
        if not actions:
            if content.strip():
                action = "recommend_tool" if config.tool_selection_agent else config.defaultTool
                return self.runMultipleActions(content=f"@{action} {content}", gui=gui)
        else:
            separator = "＊@＊@＊"
            descriptions = re.sub(config.toolPattern, separator, f"{content} ").split(separator)
            if descriptions[0].strip():
                # in case content entered before the first action declared
                actions.insert(0, "chat")
            else:
                del descriptions[0]

            for index, action in enumerate(actions):
                rawDescription = descriptions[index]
                self.workflow.append((action, rawDescription))
                if action == "list_current_directory_contents":
                    description = f"List contents in current directory {os.getcwd()}"
                elif action == "paste_from_clipboard" and not rawDescription.strip():
                    description = "Retrieve the clipboard text"
                elif action in ("search_bible", "search_bible_paragraphs") and not rawDescription.strip():
                    description = "[NONE]"
                else:
                    description = rawDescription
                if not description.strip():
                    if action == "screenshot":
                        description = os.path.join(os.getcwd(), "screenshot.png")
                    else:
                        # enable tool to work on previous generated response
                        description = getAssistantPreviousResponse()[0]
                elif re.search("^`[^`.,?!]+?`$", description.strip()) or re.search("^`[^`.,?!]+?` `[^`.,?!]+?`$", description.strip()):
                    # in case description is a predefined system message or a predefined context
                    assistantPreviousResponse = getAssistantPreviousResponse()[0]
                    description = f"{description} {assistantPreviousResponse}"
                if description.strip():
                    def displayActionMessage(message):
                        displayMessage = message[:50]
                        if len(message) > 50:
                            displayMessage += " ..."
                        print()
                        print2("```request")
                        print3(displayMessage)
                        print2("```")
                    if action == "deep_reflection":
                        # think
                        description = f'''`Think` {description}'''
                        message = f'''@chat: {description}\n'''
                        displayActionMessage(message)
                        complete = self.runSingleAction("chat", description, gui)
                        if not complete:
                            return False
                        # review
                        message = '''@chat: Review, evaluate, and reflect ...\n'''
                        displayActionMessage(message)
                        description = config.predefinedContexts["Review"][6:]
                        complete = self.runSingleAction("chat", description, gui)
                        if not complete:
                            return False
                        # refine
                        message = '''@chat: Refine ...\n'''
                        displayActionMessage(message)
                        description = config.predefinedContexts["Refine"][21:]
                        complete = self.runSingleAction("chat", description, gui)
                        if not complete:
                            return False
                    elif action == "workflow":
                        workflowFile = refinePath(description.strip())
                        if not os.path.isfile(workflowFile):
                            relativeWorkflowFile = os.path.join(config.localStorage, "workflows", workflowFile)
                            if os.path.isfile(relativeWorkflowFile):
                                workflowFile = relativeWorkflowFile
                        if os.path.isfile(workflowFile):
                            workflowContent = readTextFile(workflowFile)
                            complete = self.runMultipleActions(workflowContent)
                            if not complete:
                                return False
                        else:
                            print2("Workflow file invalid!")
                    else:
                        message = f'''@{action}: {description}'''
                        displayActionMessage(message)
                        complete = self.runSingleAction(action, description, gui)
                        if not complete:
                            return False
        return True

    def startChats(self):
        tokenValidator = TokenValidator()
        def getDynamicToolBar():
            return config.dynamicToolBarText
        def startChat():
            clear()
            print1(self.divider)
            self.showLogo()
            #self.showDefaultContext()
            # go to startup directory
            storagedirectory = config.localStorage
            os.chdir(storagedirectory)
            messages = CallLLM.resetMessages()
            #print1(f"startup directory:\n{storagedirectory}")
            print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Current Directory:</{config.terminalPromptIndicatorColor2}> {storagedirectory}"))
            print1(self.divider)
            config.conversationStarted = False
            return (storagedirectory, messages)
        def checkDirectory(storagedirectory):
            currentDirectory = os.getcwd()
            if not currentDirectory == storagedirectory:
                #print1(self.divider)
                print3(f"Current directory: {currentDirectory}")
                print1(self.divider)
                return currentDirectory
            return storagedirectory
        storagedirectory, config.currentMessages = startChat()
        config.multilineInput = False
        while True:
            # clear workflow
            self.workflow = []
            # default toolbar text
            config.dynamicToolBarText = f""" {str(config.hotkey_exit).replace("'", "")} exit {str(config.hotkey_display_key_combo).replace("'", "")} shortcuts """
            # display current directory if changed
            storagedirectory = checkDirectory(storagedirectory)
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
            userInput = self.prompts.simplePrompt(promptSession=self.terminal_chat_session, completer=config.completer_developer if config.developer else config.completer_user, default=defaultEntry, accept_default=accept_default, validator=tokenValidator, bottom_toolbar=getDynamicToolBar)
            
            # update system message when user enter a new input
            config.currentMessages = self.updateSystemMessage(config.currentMessages)
            
            # display options when empty string is entered
            userInputLower = userInput.lower()
            if userInputLower == ".backend":
                userInput = userInputLower = ".model"
            if config.addToolAt is not None:
                prefix = userInput[:config.addToolAt]
                suffix = userInput[config.addToolAt:]
                completer = FuzzyCompleter(WordCompleter([f"@{i}" for i in config.allEnabledTools], ignore_case=True))
                print2("Search for a tool below:")
                insrtedTool = self.prompts.simplePrompt(style=self.prompts.promptStyle2, completer=completer)
                config.defaultEntry = f"{prefix} {insrtedTool} {suffix}" if insrtedTool and not insrtedTool.strip().lower() == config.exit_entry else f"{prefix}{suffix}"
                config.addToolAt = None
                userInput = ""
            elif config.addPathAt is not None:
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

            # replace alias, if any, with full entry
            userInput = f"{userInput} "
            for alias, fullEntry in config.aliases.items():
                #userInput = re.sub(alias, fullEntry, userInput) # error on Windows coz of Windows path
                userInput = userInput.replace(alias, fullEntry)
            userInput = userInput[:-1]

            # open file / directory directly
            docs_path = isExistingPath(userInput)
            if os.path.isfile(docs_path) and shutil.which(config.open):
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

            if userInput == "@":
                Plugins.checkAvailableTools(display=True, includeRequirements=True)
                continue

            # try eval
            if config.developer and not userInput == "...":
                try:
                    value = eval(userInput) # it solve simple math, e.g. 1+1, or read variables, e.g. dir(config)
                    if value is not None:
                        #print(value)
                        pprint.pprint(value)
                        print("")
                        continue
                    elif re.search(r"^print\([^\)\)]+?\)$", userInput):
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
                self.insertPredefinedContext()
            elif userInputLower == ".new":
                self.saveChat(config.currentMessages)
                storagedirectory, config.currentMessages = startChat()
            elif userInputLower == ".last":
                last_conversation = config.last_conversation
                if last_conversation:
                    print3(f"Previous conversation found: {last_conversation}")
                    if config.conversationStarted:
                        print2("We are saving the current conversation first ...")
                        self.saveChat(config.currentMessages)
                    config.currentMessages = self.loadMessages(last_conversation)
                    storagedirectory, _ = startChat()
                    checkDirectory(storagedirectory)
                    displayLoadedMessages(config.currentMessages)
                else:
                    print2("Previously saved conversation not found!")
            elif userInputLower == ".open":
                try:
                    cwd = os.getcwd()
                    lastConversationDir = os.path.dirname(config.last_conversation)
                    changeDir = True if config.last_conversation and os.path.isdir(lastConversationDir) and not cwd==lastConversationDir else False
                    if changeDir:
                        os.chdir(lastConversationDir)
                    filePath = self.getPath.getFilePath(
                        check_isfile=True,
                        empty_to_cancel=True,
                        list_content_on_directory_change=True,
                        keep_startup_directory=True,
                        message=f"{self.divider}\nEnter the file path of the chat records that you would like to open:",
                    )
                    if filePath and os.path.isfile(filePath):
                        if config.conversationStarted:
                            print2("We are saving the current conversation first ...")
                            self.saveChat(config.currentMessages)
                        print3(f"Loading: {filePath}")
                        config.currentMessages = self.loadMessages(filePath)
                        storagedirectory, _ = startChat()
                        checkDirectory(storagedirectory)
                        displayLoadedMessages(config.currentMessages)
                    if changeDir:
                        os.chdir(cwd)
                except:
                    print2(f"Invalid file path of format!")
            elif userInput and not userInputLower in config.actionKeys:

                # tweak for `Let me Translate`
                if config.predefinedContext == "Let me Translate" and userInput.startswith("@chat Assist me by acting as a translator.\nPlease translate"):
                    if hasattr(config, "api_server_id"):
                        if not config.translateToLanguage:
                            config.translateToLanguage = "English"
                    else:
                        print1("Please specify the language you would like the content to be translated into:")
                        language = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.translateToLanguage)
                        if language and not language.strip().lower() in (config.cancel_entry, config.exit_entry):
                            config.translateToLanguage = language
                        else:
                            if not config.translateToLanguage:
                                config.translateToLanguage = "English"
                            print3(f"Language not specified! The content will be translated into: {config.translateToLanguage}")
                    userInput = f"{userInput}\n\nPlease translate the content into <language>{config.translateToLanguage}</language>."

                # reset `config.predefinedContext` and clear `config.predefinedContextTemp` if `config.predefinedContextTemp`` is not empty
                if config.predefinedContextTemp:
                    config.predefinedContext = config.predefinedContextTemp
                    config.predefinedContextTemp = ""

                complete = self.runMultipleActions(userInput)
                if not complete:
                    _, config.currentMessages = startChat()

    def launchPager(self, pagerContent=None):
        if pagerContent is None:
            previousResponse = getAssistantPreviousResponse()[0]
            if not previousResponse:
                return None
            terminal_width = shutil.get_terminal_size().columns
            pagerContent = wrapText(previousResponse, terminal_width) if config.wrapWords else previousResponse
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
