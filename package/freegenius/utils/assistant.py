from freegenius import config
import openai, threading, os, time, traceback, re, subprocess, json, pydoc, textwrap, shutil, datetime, pprint, sys
from pathlib import Path
import pygments
from pygments.lexers.python import PythonLexer
#from pygments.lexers.shell import BashLexer
#from pygments.lexers.markup import MarkdownLexer
from prompt_toolkit.formatted_text import PygmentsTokens
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
from freegenius.utils.file_utils import FileUtil
from freegenius.utils.terminal_system_command_prompt import SystemCommandPrompt
from freegenius.utils.shared_utils import SharedUtil
from freegenius.utils.tts_utils import TTSUtil
from freegenius.utils.ttsLanguages import TtsLanguages
from freegenius.utils.streaming_word_wrapper import StreamingWordWrapper
from freegenius.utils.text_utils import TextUtil
from freegenius.utils.sttLanguages import googleSpeeckToTextLanguages, whisperSpeeckToTextLanguages
from freegenius.chatgpt import ChatGPT
from freegenius.utils.install import installmodule
if not config.isTermux:
    from freegenius.autobuilder import AutoGenBuilder
    from freegenius.geminipro import GeminiPro
    from freegenius.palm2 import Palm2
    from freegenius.codey import Codey
from elevenlabs import generate, voices


class LetMeDoItAI:

    def __init__(self):
        #config.letMeDoItAI = self
        self.prompts = Prompts()
        self.dialogs = TerminalModeDialogs(self)
        self.setup()
        SharedUtil.runPlugins()

    def setup(self):
        # set up tool store client
        SharedUtil.setupToolStoreClient()

        self.models = list(SharedUtil.tokenLimits.keys())
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
        config.addFunctionCall = SharedUtil.addFunctionCall
        config.getLocalStorage = SharedUtil.getLocalStorage
        config.stopSpinning = self.stopSpinning
        config.toggleMultiline = self.toggleMultiline
        config.print = self.print
        config.print2 = self.print2
        config.print3 = self.print3
        config.getWrappedHTMLText = self.getWrappedHTMLText
        config.fineTuneUserInput = self.fineTuneUserInput
        config.launchPager = self.launchPager
        config.addPagerText = self.addPagerText
        config.changeOpenweathermapApi = self.changeOpenweathermapApi
        config.runSpecificFuntion = ""
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

        # local storage directory
        self.storageDir = SharedUtil.getLocalStorage()
        # hisotry directory
        if (not config.historyParentFolder or not os.path.isdir(config.historyParentFolder)) and self.storageDir:
            try:
                historyParentFolder = os.path.join(self.storageDir, "history")
                Path(historyParentFolder).mkdir(parents=True, exist_ok=True)
                for i in ("chats", "paths", "commands"):
                    historyFile = os.path.join(historyParentFolder, i)
                    if not os.path.isfile(historyFile):
                        open(historyFile, "a", encoding="utf-8").close()
                config.historyParentFolder = self.storageDir
            except:
                config.historyParentFolder = ""
            config.saveConfig()
        
        if not config.openaiApiKey:
            self.changeAPIkey()

        if not config.openaiApiKey:
            self.print2("ChatGPT API key not found!")
            self.print3("Read: https://github.com/eliranwong/letmedoit/wiki/ChatGPT-API-Key")
            exit(0)

        # initial completion check at startup
        if config.llmServer == "cahtgpt":
            if config.initialCompletionCheck:
                SharedUtil.checkCompletion()
            else:
                SharedUtil.setAPIkey()

        chat_history = os.path.join(config.historyParentFolder if config.historyParentFolder else config.letMeDoItAIFolder, "history", "chats")
        self.terminal_chat_session = PromptSession(history=FileHistory(chat_history))

        # check if tts is ready
        self.isTtsAvailable()

        self.actions = {
            ".new": (f"start a new chat {str(config.hotkey_new)}", None),
            ".save": ("save content", lambda: self.saveChat(config.currentMessages)),
            ".export": (f"export content {str(config.hotkey_export)}", lambda: self.exportChat(config.currentMessages)),
            ".context": (f"change chat context {str(config.hotkey_select_context)}", None),
            ".contextintegration": ("change chat context integration", self.setContextIntegration),
            ".changeapikey": ("change OpenAI API key", self.changeAPIkey),
            ".functionmodel": ("change function call model", self.setLlmModel),
            ".chatmodel": ("change chat-only model", self.setChatbot),
            ".embeddingmodel": ("change embedding model", self.setEmbeddingModel),
            ".temperature": ("change temperature", self.setTemperature),
            ".maxtokens": ("change maximum response tokens", self.setMaxTokens),
            ".mintokens": ("change minimum response tokens", self.setMinTokens),
            ".dynamictokencount": ("change dynamic token count", self.setDynamicTokenCount),
            ".maxautoheal": ("change maximum consecutive auto-heal", self.setMaxAutoHeal),
            ".maxmemorymatches": ("change maximum memory matches", self.setMemoryClosestMatches),
            ".maxchatrecordmatches": ("change maximum chat record matches", self.setChatRecordClosestMatches),
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
            ".voicetypingconfig": ("change voice typing config", self.setVoiceTypingConfig),
            ".texttospeechconfig": ("change text-to-speech config", self.setTextToSpeechConfig),
            ".googleapiservice": ("change Google API service", self.selectGoogleAPIs),
            ".openweathermapapi": ("change OpenWeatherMap API key", self.changeOpenweathermapApi),
            ".elevenlabsapi": ("change ElevenLabs API key", self.changeElevenlabsApi),
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
            ".toggleinputaudio": (f"toggle input audio {str(config.hotkey_toggle_input_audio)}", self.toggleinputaudio),
            ".toggleresponseaudio": (f"toggle response audio {str(config.hotkey_toggle_response_audio)}", self.toggleresponseaudio),
            ".editresponse": (f"edit the last response {str(config.hotkey_edit_last_response)}", self.editLastResponse),
            ".editconfigs": ("edit configuration settings", self.editConfigs),
            ".install": ("install python package", self.installPythonPackage),
            ".system": (f"open system command prompt {str(config.hotkey_launch_system_prompt)}", lambda: SystemCommandPrompt().run(allowPathChanges=True)),
            ".content": ("display current directory content", self.getPath.displayDirectoryContent),
            ".keys": (f"display key bindings {str(config.hotkey_display_key_combo)}", config.showKeyBindings),
            ".help": ("open LetMeDoIt wiki", lambda: SharedUtil.openURL('https://github.com/eliranwong/letmedoit/wiki')),
            ".donate": ("donate and support LetMeDoIt AI", lambda: SharedUtil.openURL('https://www.paypal.com/paypalme/letmedoitai')),
        }

        config.actionHelp = f"# Quick Actions\n(entries that start with '.')\n"
        for key, value in self.actions.items():
            config.actionHelp += f"{key}: {value[0]}\n"
        config.actionHelp += "\n## Read more at:\nhttps://github.com/eliranwong/letmedoit/wiki/Action-Menu"

    def getFolderPath(self, default=""):
        return self.getPath.getFolderPath(
            check_isdir=True,
            display_dir_only=True,
            create_dirs_if_not_exist=True,
            empty_to_cancel=True,
            list_content_on_directory_change=True,
            keep_startup_directory=True,
            message=f"{self.divider}\nSetting a startup directory ...\nEnter a folder name or path below:",
            bottom_toolbar="",
            promptIndicator = "",
            default=default,
        )

    # Voice Typing Language
    def setSpeechToTextLanguage(self):
        # record in history for easy retrieval by moving arrows upwards / downwards
        voice_typing_language_history = os.path.join(config.historyParentFolder if config.historyParentFolder else config.letMeDoItAIFolder, "history", "voice_typing_language")
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
        self.print("Please specify the voice typing language:")
        language = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=default, promptSession=voice_typing_language_session, completer=completer)
        if language and not language in (config.exit_entry, config.cancel_entry):
            config.voiceTypingLanguage = language
        if not config.voiceTypingLanguage in languages:
            config.voiceTypingLanguage = "en-US" if config.voiceTypingPlatform in ("google", "googlecloud") else "english"
        if config.voiceTypingPlatform in ("google", "googlecloud") and config.voiceTypingLanguage in languages:
            config.voiceTypingLanguage = googleSpeeckToTextLanguages[config.voiceTypingLanguage]

    # ElevenLabs Text-to-Speech Voice
    def setElevenlabsVoice(self):
        # record in history for easy retrieval by moving arrows upwards / downwards
        elevenlabsVoice_history = os.path.join(config.historyParentFolder if config.historyParentFolder else config.letMeDoItAIFolder, "history", "elevenlabsVoice")
        elevenlabsVoice_session = PromptSession(history=FileHistory(elevenlabsVoice_history))
        # input suggestion for options
        options = [voice.name for voice in voices()]
        # default
        default = config.elevenlabsVoice if config.elevenlabsVoice in options else "Rachel"
        # completer
        completer = FuzzyCompleter(WordCompleter(options, ignore_case=True))
        self.print("Please specify ElevenLabs Text-to-Speech Voice:")
        option = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=default, promptSession=elevenlabsVoice_session, completer=completer)
        if option and not option in (config.exit_entry, config.cancel_entry):
            config.elevenlabsVoice = option if option in options else "Rachel"

    # Google Text-to-Speech (Generic)
    def setGttsLanguage(self):
        # record in history for easy retrieval by moving arrows upwards / downwards
        gtts_language_history = os.path.join(config.historyParentFolder if config.historyParentFolder else config.letMeDoItAIFolder, "history", "gtts_language")
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
        self.print("Please specify Google Text-to-Speech language:")
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
        gctts_language_history = os.path.join(config.historyParentFolder if config.historyParentFolder else config.letMeDoItAIFolder, "history", "gctts_language")
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
        self.print("Please specify Google Cloud Text-to-Speech language:")
        language = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=default, promptSession=gctts_language_session, completer=completer)
        if language and not language in (config.exit_entry, config.cancel_entry):
            config.gcttsLang = language
        if config.gcttsLang in languages:
            config.gcttsLang = TtsLanguages.gctts[config.gcttsLang]
        else:
            config.gcttsLang = "en-US"

    def setVlcSpeed(self):
        if config.isVlcPlayerInstalled and not config.usePygame:
            self.print("Specify VLC player playback speed:")
            self.print("(between 0.1 and 2.0)")
            vlcSpeed = self.prompts.simplePrompt(style=self.prompts.promptStyle2, validator=FloatValidator(), default=str(config.vlcSpeed))
            if vlcSpeed and not vlcSpeed.strip().lower() == config.exit_entry:
                vlcSpeed = float(vlcSpeed)
                if vlcSpeed < 0.1:
                    vlcSpeed = 0.1
                elif vlcSpeed > 2:
                    vlcSpeed = 2
                config.vlcSpeed = round(vlcSpeed, 1)
                self.print3(f"VLC player playback speed: {vlcSpeed}")

    def setGcttsSpeed(self):
        self.print("Specify Google Cloud Text-to-Speech playback speed:")
        self.print("(between 0.1 and 2.0)")
        gcttsSpeed = self.prompts.simplePrompt(style=self.prompts.promptStyle2, validator=FloatValidator(), default=str(config.gcttsSpeed))
        if gcttsSpeed and not gcttsSpeed.strip().lower() == config.exit_entry:
            gcttsSpeed = float(gcttsSpeed)
            if gcttsSpeed < 0.1:
                gcttsSpeed = 0.1
            elif gcttsSpeed > 2:
                gcttsSpeed = 2
            config.gcttsSpeed = round(gcttsSpeed, 1)
            self.print3(f"Google Cloud Text-to-Speech playback speed: {gcttsSpeed}")

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
            self.print(f"API key json file '{config.google_cloud_credentials_file}' not found!")
            self.print("Read https://github.com/eliranwong/letmedoit/wiki/Google-API-Setup for setting up Google API.")
        if "Speech-to-Text" in config.enabledGoogleAPIs:
            if not config.voiceTypingPlatform == "googlecloud":
                config.voiceTypingPlatform = "googlecloud"
                self.print3("Voice typing platform changed to: Google Text-to-Speech (API)")
            self.setSpeechToTextLanguage()
        if "Text-to-Speech" in config.enabledGoogleAPIs:
            if not config.ttsPlatform == "googlecloud":
                config.ttsPlatform = "googlecloud"
                self.print3("Text-to-Speech platform changed to: Google Text-to-Speech (API)")
            self.setGcttsLanguage()
            self.setGcttsSpeed()
        config.saveConfig()

    def selectPlugins(self):
        plugins = []
        enabledPlugins = []
        pluginFolder = os.path.join(config.letMeDoItAIFolder, "plugins")
        if self.storageDir:
            customPluginFoler = os.path.join(self.storageDir, "plugins")
            Path(customPluginFoler).mkdir(parents=True, exist_ok=True)
            pluginFolders = (pluginFolder, customPluginFoler)
        else:
            pluginFolders = (pluginFolder,)
        for folder in pluginFolders:
            for plugin in FileUtil.fileNamesWithoutExtension(folder, "py"):
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
            SharedUtil.runPlugins()
            config.saveConfig()
            self.print("Plugin selection updated!")

    def getCliOutput(self, cli):
        try:
            process = subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, *_ = process.communicate()
            return stdout.decode("utf-8")
        except:
            return ""

    def fingerprint(self):
        try:
            output = json.loads(self.getCliOutput("termux-fingerprint"))
            return True if output["auth_result"] == "AUTH_RESULT_SUCCESS" else False
        except:
            return False

    def changeAPIkey(self):
        if not config.terminalEnableTermuxAPI or (config.terminalEnableTermuxAPI and self.fingerprint()):
            self.print("Enter your OpenAI API Key [required]:")
            apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.openaiApiKey, is_password=True)
            if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
                config.openaiApiKey = apikey
            #self.print("Enter your Organization ID [optional]:")
            #oid = self.prompts.simplePrompt(default=config.openaiApiOrganization, is_password=True)
            #if oid and not oid.strip().lower() in (config.cancel_entry, config.exit_entry):
            #    config.openaiApiOrganization = oid
            SharedUtil.checkCompletion()
            config.saveConfig()
            self.print2("Configurations updated!")

    def changeOpenweathermapApi(self):
        if not config.terminalEnableTermuxAPI or (config.terminalEnableTermuxAPI and self.fingerprint()):
            self.print("To set up OpenWeatherMap API Key, read:\nhttps://github.com/eliranwong/letmedoit/wiki/OpenWeatherMap-API-Setup\n")
            self.print("Enter your OpenWeatherMap API Key:")
            print()
            apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.openweathermapApi, is_password=True)
            if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
                config.openweathermapApi = apikey
            if SharedUtil.getWeather() is not None:
                config.saveConfig()
                self.print2("Configurations updated!")
            else:
                config.openweathermapApi = ""
                self.print2("Invalid API key entered!")

    def changeElevenlabsApi(self):
        if not config.terminalEnableTermuxAPI or (config.terminalEnableTermuxAPI and self.fingerprint()):
            self.print("To set up ElevenLabs API Key, read:\nhttps://elevenlabs.io/docs/api-reference/text-to-speech#authentication\n")
            self.print("Enter your ElevenLabs API Key:")
            print()
            apikey = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.elevenlabsApi, is_password=True)
            if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
                config.elevenlabsApi = apikey
            try:
                # testing
                generate(
                    api_key=config.elevenlabsApi, # Defaults to os.getenv(ELEVEN_API_KEY)
                    text="test",
                    voice="Rachel",
                    model="eleven_multilingual_v2"
                )
                config.saveConfig()
                self.print2("Configurations updated!")
            except:
                config.elevenlabsApi = ""
                self.print2("Invalid API key entered!")

    def exitAction(self):
        message = "closing ..."
        self.print2(message)
        self.print(self.divider)
        return ""

    def print(self, content):
        content = SharedUtil.transformText(content)
        if config.wrapWords:
            # wrap words to fit terminal width
            terminal_width = shutil.get_terminal_size().columns
            print(StreamingWordWrapper.wrapText(content, terminal_width))
            # remarks: 'fold' or 'fmt' does not work on Windows
            # pydoc.pipepager(f"{content}\n", cmd=f"fold -s -w {terminal_width}")
            # pydoc.pipepager(f"{content}\n", cmd=f"fmt -w {terminal_width}")
        else:
            print(content)

    def print2(self, content):
        print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>{content}</{config.terminalPromptIndicatorColor2}>"))

    def print3(self, content):
        splittedContent = content.split(": ", 1)
        if len(splittedContent) == 2:
            key, value = splittedContent
            print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>{key}:</{config.terminalPromptIndicatorColor2}> {value}"))
        else:
            self.print2(splittedContent)

    def spinning_animation(self, stop_event):
        while not stop_event.is_set():
            for symbol in "|/-\\":
                print(symbol, end="\r")
                time.sleep(0.1)
        #print("\r", end="")
        #print(" ", end="")

    # update system message
    def updateSystemMessage(self, messages):
        for index, message in enumerate(messages):
            try:
                if message.get("role", "") == "system":
                    # update system mess
                    dayOfWeek = SharedUtil.getDayOfWeek()
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
            self.print2(f"'{config.predefinedContext}' not defined!")
            config.predefinedContext = config.predefinedContextTemp if config.predefinedContextTemp and config.predefinedContextTemp in config.predefinedContexts else "[none]"
            self.print3(f"Predefined context changed to: {config.predefinedContext}")
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
        self.print(self.divider)
        self.print3(f"Context: {config.predefinedContext}{description}")
        self.print(self.divider)

    def fineTuneUserInput(self, userInput):
        # customise chat context
        context = self.getCurrentContext()
        if SharedUtil.is_valid_url(userInput) and config.predefinedContext in ("Let me Summarize", "Let me Explain"):
            context = context.replace("the following content:\n[NO_FUNCTION_CALL]", "the content in the this web url:\n")
        elif SharedUtil.is_valid_url(userInput) and config.predefinedContext == "Let me Translate":
            userInput = SharedUtil.getWebText(userInput)
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
            if feature.startswith("."):
                query = feature[1:]
            feature = self.dialogs.getValidOptions(
                options=options,
                descriptions=descriptions,
                title=config.letMeDoItName,
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
            self.print3(f"Automatic Upgrade: {option}d!")

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
            self.print3(f"Dynamic token count: {option}d!")

    def setIncludeIpInSystemMessage(self):
        options = ("enable", "disable")
        option = self.dialogs.getValidOptions(
            options=options,
            title="Include IP information",
            default="enable" if config.includeIpInSystemMessage else "disable",
            text="Include IP information in system message\ncan enhance response about locations.\nSelect an option below:"
        )
        if option:
            config.includeIpInSystemMessage = (option == "enable")
            config.saveConfig()
            self.print3(f"Include IP information: {option}d!")

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
            self.print3(f"Code display: {option}d!")

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
            self.print3(f"Predefined Context Integration: {option}!")

    def setStorageDirectory(self):
        try:
            folder = self.getFolderPath(default=config.storagedirectory)
        except:
            self.print2(f"Given path not accessible!")
            folder = ""
        if folder and os.path.isdir(folder):
            config.storagedirectory = folder
            config.saveConfig()
            self.print3(f"Startup directory:\n{folder}")

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
            text=f"{config.letMeDoItName} can perform online searches.\nHow do you want this feature?",
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
            SharedUtil.runPlugins()
            # notify
            config.saveConfig()
            self.print3(f"Latest Online Searches: {option}")

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
            text=f"{config.letMeDoItName} is designed to execute commands on your behalf.\nPlease specify when you would prefer\nto receive a confirmation\nbefore commands are executed:\n(Note: Execute commands at your own risk.)",
            default=config.confirmExecution,
        )
        if option:
            config.confirmExecution = option
            config.saveConfig()
            self.print3(f"Command Confirmation Protocol: {option}")

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
            self.print3(f"Pager View: {option}!")

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
            self.print3(f"Developer Mode: {option}d!")

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
                self.print("Termux is not installed!")
            if config.terminalEnableTermuxAPI:
                # Check if Termux API package is installed
                result = subprocess.run(['pkg', 'list-installed', 'termux-api'], capture_output=True, text=True)
                # Check if the package is installed
                if not "termux-api" in result.stdout:
                    self.print("Termux:API is not installed!")
            # reset plugins
            SharedUtil.runPlugins()
            config.saveConfig()
            self.print3(f"""Termux API Integration: {"enable" if config.terminalEnableTermuxAPI else "disable"}d!""")

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
            self.print3(f"ChaptGPT function call: {'enabled' if config.chatGPTApiFunctionCall == 'auto' else 'disabled'}!")

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
            self.print3(f"Pass Function Call Response to ChatGPT: {'enabled' if config.passFunctionCallReturnToChatGPT else 'disabled'}!")

    def editLastResponse(self):
        customTextEditor = config.customTextEditor if config.customTextEditor else f"{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'eTextEdit.py')}"
        pydoc.pipepager(config.pagerContent, cmd=customTextEditor)
        set_title(config.letMeDoItName)

    # change configs
    def editConfigs(self):
        # file paths
        configFile = os.path.join(config.letMeDoItAIFolder, "config.py")
        backupFile = os.path.join(config.getLocalStorage(), "config_backup.py")
        # backup configs
        config.saveConfig()
        shutil.copy(configFile, backupFile)
        # open current configs with built-in text editor
        customTextEditor = config.customTextEditor if config.customTextEditor else f"{sys.executable} {os.path.join(config.letMeDoItAIFolder, 'eTextEdit.py')}"
        os.system(f"{customTextEditor} {configFile}")
        set_title(config.letMeDoItName)
        # re-load configs
        try:
            config.loadConfig(configFile)
            self.print2("Changes loaded!")
        except:
            self.print2("Failed to load your changes!")
            print(traceback.format_exc())
            try:
                self.print2("Restoring backup ...")
                config.loadConfig(backupFile)
                shutil.copy(backupFile, configFile)
                self.print2("Restored!")
            except:
                self.print2("Failed to restore backup!")

    def installPythonPackage(self):
        self.print("Enter a python package name:")
        package = self.prompts.simplePrompt(style=self.prompts.promptStyle2)
        if package:
            self.print(f"Installing '{package}' ...")
            installmodule(f"--upgrade {package}")

    def setTemperature(self):
        self.print("Enter a value between 0.0 and 2.0:")
        self.print("(Lower values for temperature result in more consistent outputs, while higher values generate more diverse and creative results. Select a temperature value based on the desired trade-off between coherence and creativity for your specific application.)")
        temperature = self.prompts.simplePrompt(style=self.prompts.promptStyle2, validator=FloatValidator(), default=str(config.llmTemperature))
        if temperature and not temperature.strip().lower() == config.exit_entry:
            temperature = float(temperature)
            if temperature < 0:
                temperature = 0
            elif temperature > 2:
                temperature = 2
            config.llmTemperature = round(temperature, 1)
            config.saveConfig()
            self.print3(f"LLM Temperature: {temperature}")

    def setLlmModel(self):
        model = self.dialogs.getValidOptions(
            options=self.models,
            title="Function Calling Model",
            default=config.chatGPTApiModel if config.chatGPTApiModel in self.models else self.models[0],
            text="Select a function call model:\n(for both chat and task execution)",
        )
        if model:
            config.chatGPTApiModel = model
            self.print3(f"ChatGPT model: {model}")
            # set max tokens
            config.chatGPTApiMaxTokens = self.getMaxTokens()[-1]
            config.saveConfig()
            self.print3(f"Maximum response tokens: {config.chatGPTApiMaxTokens}")

    def setChatbot(self):
        model = self.dialogs.getValidOptions(
            options=("chatgpt", "geminipro", "palm2", "codey"),
            title="Chat-only model",
            default=config.chatbot,
            text="Select default chat-only model:\n(Default model is loaded when you include '[CHAT]' in your input)",
        )
        if model:
            config.chatbot = model
            self.print3(f"Chat-only model: {model}")

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
                self.print("Enter OpenAI or Sentence Transformer Embedding model:")
                self.print("Read more at: https://www.sbert.net/docs/pretrained_models.html")
                customModel = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.embeddingModel)
                if customModel and not customModel.strip().lower() == config.exit_entry:
                    config.embeddingModel = customModel 
            else:
                config.embeddingModel = model
            self.print3(f"Embedding model: {model}")
        if not oldEmbeddingModel == config.embeddingModel:
            self.print(f"You've change the embedding model from '{oldEmbeddingModel}' to '{config.embeddingModel}'.")
            self.print("To work with the newly selected model, previous memory store and retrieved collections need to be deleted.")
            self.print("Do you want to delete them now? [y]es / [N]o")
            confirmation = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default="yes")
            if confirmation.lower() in ("y", "yes"):
                memory_store = os.path.join(config.getLocalStorage(), "memory")
                retrieved_collections = os.path.join(config.getLocalStorage(), "autogen", "retriever")
                for folder in (memory_store, retrieved_collections):
                    shutil.rmtree(folder, ignore_errors=True)
            else:
                self.print(f"Do you want to change back the embedding model from '{config.embeddingModel}' to '{oldEmbeddingModel}'? [y]es / [N]o")
                confirmation = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default="yes")
                if not confirmation.lower() in ("y", "yes"):
                    config.embeddingModel = oldEmbeddingModel
                    self.print3(f"Embedding model: {oldEmbeddingModel}")
        if not oldEmbeddingModel == config.embeddingModel:
            config.saveConfig()

    def setAutoGenBuilderConfig(self):
        if not config.isTermux:
            AutoGenBuilder().promptConfig()

    def setAssistantName(self):
        self.print("You may modify my name below:")
        letMeDoItName = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.letMeDoItName)
        if letMeDoItName and not letMeDoItName.strip().lower() == config.exit_entry:
            config.letMeDoItName = letMeDoItName
            self.storageDir = SharedUtil.getLocalStorage()
            config.saveConfig()
            self.print3(f"You have changed my name to: {config.letMeDoItName}")

    def setCustomSystemMessage(self):
        self.print("You can modify the system message to furnish me with details about my capabilities, constraints, or any pertinent context that may inform our interactions. This will guide me in managing and responding to your requests appropriately.")
        self.print("Please note that altering my system message directly affects my functionality. Handle with care.")
        self.print("Enter custom system message below:")
        self.print(f"(Keep it blank to use {config.letMeDoItName} default system message.)")
        message = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.systemMessage_letmedoit)
        if message and not message.strip().lower() == config.exit_entry:
            config.systemMessage_letmedoit = message
            config.saveConfig()
            self.print3(f"Custom system message: {config.letMeDoItName}")

    def setCustomTextEditor(self):
        self.print("Please specify custom text editor command below:")
        self.print("e.g. 'micro -softwrap true -wordwrap true'")
        self.print("Leave it blank to use our built-in text editor 'eTextEdit' by default.")
        customTextEditor = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.customTextEditor)
        if customTextEditor and not customTextEditor.strip().lower() == config.exit_entry:
            textEditor = re.sub(" .*?$", "", customTextEditor)
            if not textEditor or not SharedUtil.isPackageInstalled(textEditor):
                self.print2("Command not found on your device!")
            else:
                config.customTextEditor = customTextEditor
                config.saveConfig()
                self.print3(f"Custom text editor: {config.customTextEditor}")

    def setChatRecordClosestMatches(self):
        self.print("Please specify the number of closest matches in each memory retrieval:")
        chatRecordClosestMatches = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.chatRecordClosestMatches))
        if chatRecordClosestMatches and not chatRecordClosestMatches.strip().lower() == config.exit_entry and int(chatRecordClosestMatches) >= 0:
            config.chatRecordClosestMatches = int(chatRecordClosestMatches)
            config.saveConfig()
            self.print3(f"Number of memory closest matches: {config.chatRecordClosestMatches}")

    def setMemoryClosestMatches(self):
        self.print("Please specify the number of closest matches in each memory retrieval:")
        memoryClosestMatches = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.memoryClosestMatches))
        if memoryClosestMatches and not memoryClosestMatches.strip().lower() == config.exit_entry and int(memoryClosestMatches) >= 0:
            config.memoryClosestMatches = int(memoryClosestMatches)
            config.saveConfig()
            self.print3(f"Number of memory closest matches: {config.memoryClosestMatches}")

    def setMaxAutoHeal(self):
        self.print(f"The auto-heal feature enables {config.letMeDoItName} to automatically fix broken Python code if it was not executed properly.")
        self.print("Please specify maximum number of auto-heal attempts below:")
        self.print("(Remarks: Enter '0' if you want to disable auto-heal feature)")
        maxAutoHeal = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.max_consecutive_auto_heal))
        if maxAutoHeal and not maxAutoHeal.strip().lower() == config.exit_entry and int(maxAutoHeal) >= 0:
            config.max_consecutive_auto_heal = int(maxAutoHeal)
            config.saveConfig()
            self.print3(f"Maximum consecutive auto-heal: {config.max_consecutive_auto_heal}")

    def setMinTokens(self):
        self.print("Please specify minimum response tokens below:")
        mintokens = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.chatGPTApiMinTokens))
        if mintokens and not mintokens.strip().lower() == config.exit_entry and int(mintokens) > 0:
            config.chatGPTApiMinTokens = int(mintokens)
            if config.chatGPTApiMinTokens > config.chatGPTApiMaxTokens:
                config.chatGPTApiMinTokens = config.chatGPTApiMaxTokens
            config.saveConfig()
            self.print3(f"Minimum tokens: {config.chatGPTApiMinTokens}")

    def getMaxTokens(self):
        contextWindowLimit = SharedUtil.tokenLimits[config.chatGPTApiModel]
        functionTokens = SharedUtil.count_tokens_from_functions(config.chatGPTApiFunctionSignatures.values())
        maxToken = contextWindowLimit - functionTokens - config.chatGPTApiMinTokens
        if maxToken > 4096 and config.chatGPTApiModel in (
            "gpt-4-turbo-preview",
            "gpt-4-0125-preview",
            "gpt-4-1106-preview",
            "gpt-3.5-turbo",
        ):
            maxToken = 4096
        return contextWindowLimit, functionTokens, maxToken

    def setMaxTokens(self):
        contextWindowLimit, functionTokens, tokenLimit = self.getMaxTokens()
        if tokenLimit < config.chatGPTApiMinTokens:
            self.print2(f"Function tokens [{functionTokens}] exceed {config.chatGPTApiModel} response token limit.")
            self.print("Either change to a model with higher token limit or disable unused function-call plguins.")
        else:
            self.print(self.divider)
            self.print("GPT and embeddings models process text in chunks called tokens. As a rough rule of thumb, 1 token is approximately 4 characters or 0.75 words for English text. One limitation to keep in mind is that for a GPT model the prompt and the generated output combined must be no more than the model's maximum context length.")
            self.print3(f"Current GPT model: {config.chatGPTApiModel}")
            self.print3(f"Maximum context length: {contextWindowLimit}")
            self.print3(f"Current function tokens: {functionTokens}")
            self.print3(f"Maximum response token allowed (excl. functions): {tokenLimit}")
            self.print(self.divider)
            self.print("Please specify maximum response tokens below:")
            maxtokens = self.prompts.simplePrompt(style=self.prompts.promptStyle2, numberOnly=True, default=str(config.chatGPTApiMaxTokens))
            if maxtokens and not maxtokens.strip().lower() == config.exit_entry and int(maxtokens) > 0:
                config.chatGPTApiMaxTokens = int(maxtokens)
                if config.chatGPTApiMaxTokens > tokenLimit:
                    config.chatGPTApiMaxTokens = tokenLimit
                config.saveConfig()
                self.print3(f"Maximum tokens: {config.chatGPTApiMaxTokens}")

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
        run_in_terminal(lambda: self.print(f"Multi-line input {'enabled' if config.multilineInput else 'disabled'}!"))
        if config.multilineInput:
            run_in_terminal(lambda: self.print("Use 'escape + enter' to complete your entry."))

    def isTtsAvailable(self):
        if not config.isVlcPlayerInstalled and not config.isPygameInstalled and not config.ttsCommand and not config.elevenlabsApi:
            self.print2("Text-to-speech feature is not enabled!")
            self.print3("Read: https://github.com/eliranwong/letmedoit/wiki/letMeDoIt-Speaks")
            config.tts = False
        else:
            config.tts = True
        return config.tts

    def toggleinputaudio(self):
        if self.isTtsAvailable:
            config.ttsInput = not config.ttsInput
            config.saveConfig()
            self.print3(f"Input Audio: '{'enabled' if config.ttsInput else 'disabled'}'!")

    def toggleresponseaudio(self):
        if self.isTtsAvailable:
            config.ttsOutput = not config.ttsOutput
            config.saveConfig()
            self.print3(f"Response Audio: '{'enabled' if config.ttsOutput else 'disabled'}'!")

    def defineTtsCommand(self):
        self.print("Define custom text-to-speech command below:")
        self.print("""* on macOS ['say -v "?"' to check voices], e.g.:\n'say' or 'say -r 200 -v Daniel'""")
        self.print("* on Ubuntu ['espeak --voices' to check voices], e.g.:\n'espeak' or 'espeak -s 175 -v en-gb'")
        self.print("* on Windows, simply enter 'windows' here to use Windows built-in speech engine") # letmedoit.ai will handle the command for Windows users
        self.print("remarks: always place the voice option, if any, at the end")
        ttsCommand = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.ttsCommand)
        if ttsCommand:
            self.print("Specify command suffix below, if any [leave it blank if N/A]:")
            ttsCommandSuffix = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.ttsCommandSuffix)
            if ttsCommand.lower() == "windows":
                command = f'''PowerShell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('testing');"'''
                ttsCommandSuffix = ""
            else:
                command = f'''{ttsCommand} "testing"{ttsCommandSuffix}'''
            _, stdErr = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            if stdErr:
                SharedUtil.showErrors() if config.developer else self.print("Entered command invalid!")
            else:
                config.ttsCommand, config.ttsCommandSuffix = ttsCommand, ttsCommandSuffix
                config.saveConfig()
        else:
            config.ttsCommand, config.ttsCommandSuffix = "", ""

    def toggleWordWrap(self):
        config.wrapWords = not config.wrapWords
        config.saveConfig()
        self.print3(f"Word Wrap: '{'enabled' if config.wrapWords else 'disabled'}'!")

    def toggleMouseSupport(self):
        config.mouseSupport = not config.mouseSupport
        config.saveConfig()
        self.print3(f"Entry Mouse Support: '{'enabled' if config.mouseSupport else 'disabled'}'!")

    def toggleImprovedWriting(self):
        config.displayImprovedWriting = not config.displayImprovedWriting
        if config.displayImprovedWriting:
            self.print("Please specify the writing style below:")
            style = self.prompts.simplePrompt(style=self.prompts.promptStyle2, default=config.improvedWritingSytle)
            if style and not style in (config.exit_entry, config.cancel_entry):
                config.improvedWritingSytle = style
                config.saveConfig()
        self.print3(f"Improved Writing Display: '{'enabled' if config.displayImprovedWriting else 'disabled'}'!")

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
                    self.print("VLC player not found! Install it first!")
                    self.print3("Text-to-Speech Playback changed to: PyGame")
                    config.usePygame = True
                else:
                    config.usePygame = False
            else:
                config.usePygame = True

    def setTextToSpeechConfig(self):
        ttsPlatform = self.dialogs.getValidOptions(
            options=("google", "googlecloud", "elevenlabs", "custom"),
            descriptions=("Google Text-to-Speech (Generic)", "Google Text-to-Speech (API)", "ElevenLabs (API)", "Custom Text-to-Speech Command [advanced]"),
            title="Text-to-Speech Configurations",
            text="Select a text-to-speech platform:",
            default=config.ttsPlatform,
        )
        if ttsPlatform:
            if ttsPlatform == "googlecloud" and not (os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Text-to-Speech" in config.enabledGoogleAPIs):
                self.print2("Google Cloud Text-to-Speech feature is not enabled!")
                self.print3("Read: https://github.com/eliranwong/letmedoit/wiki/Google-API-Setup")
                self.print3("Text-to-Speech platform changed to: Google Text-to-Speech (Generic)")
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
        elif config.ttsPlatform == "elevenlabs":
            if not config.elevenlabsApi:
                self.changeElevenlabsApi()
            if not config.elevenlabsApi:
                self.print("ElevenLabs API key not found!")
                self.print3("Text-to-Speech platform changed to: Google Text-to-Speech (Generic)")
                config.ttsPlatform = "google"
            else:
                self.setElevenlabsVoice()
        elif config.ttsPlatform == "custom":
            self.defineTtsCommand()
        # save configs
        config.saveConfig()

    def setVoiceTypingConfig(self):
        voiceTypingPlatform = self.dialogs.getValidOptions(
            options=("google", "googlecloud", "whisper"),
            descriptions=("Google Speech-to-Text (Generic) [online]", "Google Speech-to-Text (API) [online]", "OpenAI Whisper [offline; slower with non-English voices]"),
            title="Voice Typing Configurations",
            text="Select a voice typing platform:",
            default=config.voiceTypingPlatform,
        )
        if voiceTypingPlatform:
            if voiceTypingPlatform == "googlecloud" and not (os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Speech-to-Text" in config.enabledGoogleAPIs):
                self.print2("Google Cloud Speech-to-Text feature is not enabled!")
                self.print3("Read: https://github.com/eliranwong/letmedoit/wiki/Google-API-Setup")
                self.print3("Voice typing platform changed to: Google Speech-to-Text (Generic)")
                config.voiceTypingPlatform = "google"
            elif voiceTypingPlatform == "whisper" and not SharedUtil.isPackageInstalled("ffmpeg"):
                self.print2("Install 'ffmpeg' first to use offline openai whisper model!")
                self.print3("Read: https://github.com/openai/whisper#setup")
                self.print3("Voice typing platform changed to: Google Speech-to-Text (Generic)")
                config.voiceTypingPlatform = "google"
            else:
                config.voiceTypingPlatform = voiceTypingPlatform
        # language
        self.setSpeechToTextLanguage()
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
        self.print3(f"Voice Typing Model: {config.voiceTypingPlatform}")
        self.print3(f"Voice Typing Language: {config.voiceTypingLanguage}")
        self.print3(f"Ambient Noise Adjustment: {config.voiceTypingAdjustAmbientNoise}")
        self.print3(f"Audio Notification: {config.voiceTypingNotification}")
        self.print3(f"Auto Completion: {config.voiceTypingAutoComplete}")
        # save configs
        config.saveConfig()

    def saveChat(self, messages):
        if config.conversationStarted:
            timestamp = SharedUtil.getCurrentDateTime()

            if hasattr(config, "save_chat_record"):
                # when plugin "save chat records" is enabled
                for order, i in enumerate(messages):
                    config.save_chat_record(timestamp, order, i)

            try:
                folderPath = os.path.join(SharedUtil.getLocalStorage(), "chats", re.sub("^([0-9]+?\-[0-9]+?)\-.*?$", r"\1", timestamp))
                Path(folderPath).mkdir(parents=True, exist_ok=True)
                if os.path.isdir(folderPath):
                    chatFile = os.path.join(folderPath, f"{timestamp}.txt")
                    with open(chatFile, "w", encoding="utf-8") as fileObj:
                        fileObj.write(pprint.pformat(messages))
            except:
                self.print2("Failed to save chat!\n")
                SharedUtil.showErrors()

    def exportChat(self, messages, openFile=True):
        if config.conversationStarted:
            plainText = ""
            timestamp = SharedUtil.getCurrentDateTime()

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
                    folderPath = os.path.join(SharedUtil.getLocalStorage(), "chats", "export")
                    Path(folderPath).mkdir(parents=True, exist_ok=True)
                    if os.path.isdir(folderPath):
                        chatFile = os.path.join(folderPath, f"{timestamp}.txt")
                        with open(chatFile, "w", encoding="utf-8") as fileObj:
                            fileObj.write(plainText)
                        if openFile and os.path.isfile(chatFile):
                            os.system(f'''{config.open} "{chatFile}"''')
                except:
                    self.print2("Failed to save chat!\n")
                    SharedUtil.showErrors()

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
                self.print("Edit custom context below:")
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

    def stopSpinning(self):
        try:
            config.stop_event.set()
            config.spinner_thread.join()
        except:
            pass

    def showLogo(self):
        appName = config.letMeDoItName.split()[0].upper()
        terminal_width = shutil.get_terminal_size().columns
        try:
            from art import text2art
            if terminal_width >= 32:
                logo = text2art(appName, font="cybermedum")
            elif terminal_width >= 20:
                logo = text2art(" ".join(appName) + " ", font="white_bubble")
            else:
                logo = config.letMeDoItName
            logo = logo[:-1] # remove the linebreak at the end
        except:
            logo = config.letMeDoItName
        print_formatted_text(HTML(f"<{config.terminalCommandEntryColor2}>{logo}</{config.terminalCommandEntryColor2}>"))

    def startChats(self):
        tokenValidator = TokenValidator()
        def getDynamicToolBar():
            return config.dynamicToolBarText
        def startChat():
            clear()
            self.print(self.divider)
            self.showLogo()
            self.showCurrentContext()
            # go to startup directory
            storagedirectory = SharedUtil.getLocalStorage()
            os.chdir(storagedirectory)
            messages = SharedUtil.resetMessages()
            #self.print(f"startup directory:\n{storagedirectory}")
            print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Directory:</{config.terminalPromptIndicatorColor2}> {storagedirectory}"))
            self.print(self.divider)

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
                #self.print(self.divider)
                self.print3(f"Current directory: {currentDirectory}")
                self.print(self.divider)
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

            # replace alias, if any with full entry
            for alias, fullEntry in config.aliases.items():
                #userInput = re.sub(alias, fullEntry, userInput) # error on Windows coz of Windows path
                userInput = userInput.replace(alias, fullEntry)

            # open file / directory directly
            docs_path = SharedUtil.isExistingPath(userInput)
            if os.path.isfile(docs_path):
                os.system(f"{config.open} {docs_path}")
                continue
            elif os.path.isdir(docs_path):
                try:
                    os.chdir(docs_path)
                    self.print3(f"Directory changed to: {docs_path}")
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
                SharedUtil.runPythonScript(userInput)
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
            elif userInputLower == ".new" and config.conversationStarted:
                self.saveChat(config.currentMessages)
                storagedirectory, config.currentMessages = startChat()
            elif userInput and not userInputLower in featuresLower:
                try:
                    if userInput and config.ttsInput:
                        TTSUtil.play(userInput)
                    # Feature: improve writing:
                    specialEntryPattern = "\[CALL_[^\[\]]*?\]|\[NO_FUNCTION_CALL\]|\[NO_SCREENING\]"
                    specialEntry = re.search(specialEntryPattern, userInput)
                    specialEntry = specialEntry.group(0) if specialEntry else ""
                    userInput = re.sub(specialEntryPattern, "", userInput) # remove special entry temporarily
                    if userInput and config.displayImprovedWriting:
                        userInput = re.sub("\n\[Current time: [^\n]*?$", "", userInput)
                        if config.isTermux:
                            day_of_week = ""
                        else:
                            day_of_week = f"today is {SharedUtil.getDayOfWeek()} and "
                        improvedVersion = SharedUtil.getSingleChatResponse(f"""Improve the following writing, according to {config.improvedWritingSytle}
In addition, I would like you to help me with converting relative dates and times, if any, into exact dates and times based on the reference that {day_of_week}current datetime is {str(datetime.datetime.now())}.
Remember, provide me with the improved writing only, enclosed in triple quotes ``` and without any additional information or comments.
My writing:
{userInput}""")
                        if improvedVersion and improvedVersion.startswith("```") and improvedVersion.endswith("```"):
                            self.print(improvedVersion)
                            userInput = improvedVersion[3:-3]
                            if config.ttsOutput:
                                TTSUtil.play(userInput)
                    if specialEntry:
                        userInput = f"{userInput}{specialEntry}"
                    # refine messages before running completion
                    fineTunedUserInput = self.fineTuneUserInput(userInput)
                    # in case of translation
                    if config.predefinedContext == "Let me Translate" and fineTunedUserInput.startswith("Assist me by acting as a translator.\nPlease translate"):
                        self.print("Please specify below the language you would like the content to be translated into:")
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
                        chatbot = config.chatbot
                    elif callChatBot := re.search("\[CHAT_([^\[\]]+?)\]", fineTunedUserInput):
                        chatbot = callChatBot.group(1).lower() if callChatBot and callChatBot.group(1).lower() in ("chatgpt", "geminipro", "palm2", "codey") else ""
                    else:
                        chatbot = ""
                    if chatbot:
                        # call the spcified chatbot to continue the conversation
                        fineTunedUserInput = re.sub("\[CHAT\]|\[CHAT_[^\[\]]+?\]", "", fineTunedUserInput)
                        self.launchChatbot(chatbot, fineTunedUserInput)
                        continue
                    # if user don't want function call or a particular function call
                    noFunctionCall = ("[NO_FUNCTION_CALL]" in fineTunedUserInput)
                    checkCallSpecificFunction = re.search("\[CALL_([^\[\]]+?)\]", fineTunedUserInput)
                    config.runSpecificFuntion = checkCallSpecificFunction.group(1) if checkCallSpecificFunction and checkCallSpecificFunction.group(1) in config.chatGPTApiAvailableFunctions else ""
                    if config.developer and config.runSpecificFuntion:
                        #self.print(f"calling function '{config.runSpecificFuntion}' ...")
                        print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Calling function</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{config.runSpecificFuntion}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
                    fineTunedUserInput = re.sub(specialEntryPattern, "", fineTunedUserInput)
                    config.currentMessages.append({"role": "user", "content": fineTunedUserInput})

                    # start spinning
                    config.stop_event = threading.Event()
                    config.spinner_thread = threading.Thread(target=self.spinning_animation, args=(config.stop_event,))
                    config.spinner_thread.start()

                    # force loading internet searches
                    if config.loadingInternetSearches == "always":
                        try:
                            config.currentMessages = SharedUtil.runFunction(config.currentMessages, [config.chatGPTApiFunctionSignatures["integrate_google_searches"]], "integrate_google_searches")
                        except:
                            self.print("Unable to load internet resources.")
                            SharedUtil.showErrors()

                    completion = SharedUtil.runCompletion(config.currentMessages, noFunctionCall)
                    # stop spinning
                    config.runPython = True
                    self.stopSpinning()

                    if completion is not None:
                        # Create a new thread for the streaming task
                        streamingWordWrapper = StreamingWordWrapper()
                        streaming_event = threading.Event()
                        self.streaming_thread = threading.Thread(target=streamingWordWrapper.streamOutputs, args=(streaming_event, completion, True if config.llmServer == "chatgpt" else False))
                        # Start the streaming thread
                        self.streaming_thread.start()

                        # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+z' to stop the streaming
                        streamingWordWrapper.keyToStopStreaming(streaming_event)

                        # when streaming is done or when user press "ctrl+q"
                        self.streaming_thread.join()

                # error codes: https://platform.openai.com/docs/guides/error-codes/python-library-error-types
                except openai.APIError as e:
                    self.stopSpinning()
                    #Handle API error here, e.g. retry or log
                    self.print(f"OpenAI API returned an API Error: {e}")
                except openai.APIConnectionError as e:
                    self.stopSpinning()
                    #Handle connection error here
                    self.print(f"Failed to connect to OpenAI API: {e}")
                except openai.RateLimitError as e:
                    self.stopSpinning()
                    #Handle rate limit error (we recommend using exponential backoff)
                    self.print(f"OpenAI API request exceeded rate limit: {e}")
                except:
                    self.stopSpinning()
                    trace = traceback.format_exc()
                    if "Please reduce the length of the messages or completion" in trace:
                        self.print("Maximum tokens reached!")
                    elif config.developer:
                        self.print(self.divider)
                        self.print(trace)
                        self.print(self.divider)
                    else:
                        self.print("Error encountered!")

                    config.defaultEntry = userInput
                    self.print("starting a new chat!")
                    self.saveChat(config.currentMessages)
                    storagedirectory, config.currentMessages = startChat()

    def launchChatbot(self, chatbot, fineTunedUserInput):
        if config.isTermux:
            chatbot = "chatgpt"
        chatbots = {
            "chatgpt": lambda: ChatGPT().run(fineTunedUserInput),
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
                SharedUtil.showErrors()

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
                if SharedUtil.is_CJK(item):
                    for iIndex, i in enumerate(item):
                        isSpaceItem = (not isLastItem and (len(item) - iIndex == 1))
                        iWidth = SharedUtil.getStringWidth(i)
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
                    itemWidth = SharedUtil.getStringWidth(item)
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
