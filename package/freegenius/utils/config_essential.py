from freegenius import config
import shutil, os, pprint

pluginExcludeList = [
    "awesome prompts",
    "counselling",
    "edit text",
    "simplified Chinese to traditional Chinese",
]
if config.isTermux:
    pluginExcludeList += [
        "analyze files",
        "analyze web content",
        "ask codey",
        "ask gemini pro",
        "ask palm2",
        "create ai assistants",
        "create statistical graphics",
        "dates and times",
        "memory",
        "remove image background",
        "solve math problems",
        "search chat records",
        "check pyaudio",
    ]

defaultSettings = (
    ('llmServer', "ollama"),
    ('includeIpInSystemMessage', False),
    ('translateToLanguage', ''),
    ('dynamicTokenCount', False),
    ('use_oai_assistant', False), # support OpenAI Assistants API in AutoGen Agent Builder
    ('max_agents', 5), # maximum number of agents build manager can create.
    ('max_group_chat_round', 12), # AutoGen group chat maximum round
    ('env_QT_QPA_PLATFORM_PLUGIN_PATH', ''), # e.g. # deal with error: qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "~/apps/letmedoit/lib/python3.10/site-packages/cv2/qt/plugins" even though it was found.
    ('systemMessage_letmedoit', ''), # letmedoit system message
    ('systemMessage_chatgpt', 'You are a helpful assistant.'), # system message for standalone chatgpt chatbot
    ('systemMessage_geminipro', 'You are a helpful assistant.'), # system message for standalone geminipro chatbot
    ('systemMessage_palm2', 'You are a helpful assistant.'), # system message for standalone palm2 chatbot
    ('systemMessage_codey', 'You are an expert on coding.'), # system message for standalone codey chatbot
    ('embeddingModel', 'paraphrase-multilingual-mpnet-base-v2'), # reference: https://www.sbert.net/docs/pretrained_models.html
    ('historyParentFolder', ""),
    ('customTextEditor', ""), # e.g. 'micro -softwrap true -wordwrap true'; built-in text editor eTextEdit is used when it is not defined.
    ('pagerView', False),
    ('usePygame', False), # force to use pygame for audio playback even VLC player is installed
    ('wrapWords', True),
    ('mouseSupport', False),
    ('autoUpgrade', True),
    ('chatbot', 'chatgpt'),
    ('ollamaDefaultModel', 'phi'),
    ('customTrayCommands', ['starling-lm', 'orca2', 'mistral', 'llama2', 'codellama', 'llava']),
    ('chatGPTApiModel', 'gpt-3.5-turbo'),
    ('chatGPTApiMaxTokens', 4000),
    ('chatGPTApiMinTokens', 256),
    #('chatGPTApiNoOfChoices', 1),
    ('chatGPTApiFunctionCall', "auto"),
    ('passFunctionCallReturnToChatGPT', True),
    ('llmTemperature', 0.8),
    ('max_consecutive_auto_reply', 10), # work with pyautogen
    ('memoryClosestMatches', 5),
    ('chatRecordClosestMatches', 5),
    ('runPythonScriptGlobally', False),
    ('openaiApiKey', ''),
    ('openaiApiOrganization', ''),
    ('loadingInternetSearches', "auto"),
    ('maximumInternetSearchResults', 5),
    ('predefinedContext', '[none]'),
    ('customPredefinedContext', ''),
    ('applyPredefinedContextAlways', False), # True: apply predefined context with all use inputs; False: apply predefined context only in the beginning of the conversation
    ('thisTranslation', {}),
    ('terminalEnableTermuxAPI', True if config.isTermux and shutil.which("termux-open-url") else False),
    ('terminalEnableTermuxAPIToast', False),
    ('pluginExcludeList', pluginExcludeList),
    ('cancel_entry', '.cancel'),
    ('exit_entry', '.exit'),
    ('terminalHeadingTextColor', 'ansigreen'),
    ('terminalResourceLinkColor', 'ansiyellow'),
    ('terminalCommandEntryColor1', 'ansiyellow'),
    ('terminalPromptIndicatorColor1', 'ansimagenta'),
    ('terminalCommandEntryColor2', 'ansigreen'),
    ('terminalPromptIndicatorColor2', 'ansicyan'),
    ('terminalSearchHighlightBackground', 'ansiblue'),
    ('terminalSearchHighlightForeground', 'ansidefault'),
    ('pygments_style', ''),
    ('developer', False),
    ('confirmExecution', "always"), # 'always', 'high_risk_only', 'medium_risk_or_above', 'none'
    ('codeDisplay', False),
    ('terminalEditorScrollLineCount', 20),
    ('terminalEditorTabText', "    "),
    ('blankEntryAction', "..."),
    ('defaultBlankEntryAction', ".context"),
    ('storagedirectory', ""),
    ('suggestSystemCommand', True),
    ('displayImprovedWriting', False),
    ('improvedWritingSytle', 'standard English'), # e.g. British spoken English
    ('ttsPlatform', "google"), # "google", "googlecloud", "elevenlabs", "custom"
    ('ttsInput', False),
    ('ttsOutput', False),
    ('tts_readWhenStreamContains', "[\.\?!,:;”。，：；？！」]"), # regex pattern containing characters that LetMeDoIt AI starts reading text chunk when config.ttsOutput is set to True and the pattern is matched.  
    ('vlcSpeed', 1.0),
    ('gcttsLang', "en-US"), # https://cloud.google.com/text-to-speech/docs/voices
    ('gcttsSpeed', 1.0),
    ('gttsLang', "en"), # gTTS is used by default if ttsCommand is not given
    ('gttsTld', ""), # https://gtts.readthedocs.io/en/latest/module.html#languages-gtts-lang
    ('ttsCommand', ""), # ttsCommand is used if it is given; offline tts engine runs faster; on macOS [suggested speak rate: 100-300], e.g. "say -r 200 -v Daniel"; on Ubuntu [espeak; speed in approximate words per minute; 175 by default], e.g. "espeak -s 175 -v en"; remarks: always place the voice option, if any, at the end
    ('ttsCommandSuffix', ""), # try on Windows; ttsComand = '''Add-Type -TypeDefinition 'using System.Speech.Synthesis; class TTS { static void Main(string[] args) { using (SpeechSynthesizer synth = new SpeechSynthesizer()) { synth.Speak(args[0]); } } }'; [TTS]::Main('''; ttsCommandSuffix = ")"; a full example is Add-Type -TypeDefinition 'using System.Speech.Synthesis; class TTS { static void Main(string[] args) { using (SpeechSynthesizer synth = new SpeechSynthesizer()) { synth.Speak(args[0]); } } }'; [TTS]::Main("Text to be read")
    ("ttsLanguages", ["en", "en-gb", "en-us", "zh", "yue", "el"]), # users can edit this item in config.py to support more or less languages
    ("ttsLanguagesCommandMap", {"en": "", "en-gb": "", "en-us": "", "zh": "", "yue": "", "el": "",}), # advanced users need to edit this item manually to support different voices with customised tts command, e.g. ttsCommand set to "say -r 200 -v Daniel" and ttsLanguagesCommandMap set to {"en": "Daniel", "en-gb": "Daniel", "en-us": "", "zh": "", "yue": "", "el": "",}
    ("openweathermapApi", ""),
    ("elevenlabsApi", ""),
    ("elevenlabsVoice", "Rachel"),
    ("pyaudioInstalled", False),
    ("voiceTypingPlatform", "google"), # "google", "googlecloud", "whisper"
    ("voiceTypingLanguage", "en-US"), # https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
    ("voiceTypingAdjustAmbientNoise", False),
    ("voiceTypingNotification", True),
    ("voiceTypingAutoComplete", False),
    ("voiceTypingWhisperEnglishModel", "base"), # "tiny", "base", "small", "medium", "large"; read https://github.com/openai/whisper/tree/main#available-models-and-languages
    ("google_cloud_credentials", ""),
    ("enabledGoogleAPIs", ["Vertex AI"]), # "Vertex AI", "Speech-to-Text", "Text-to-Speech"
    ("hotkey_exit", ["c-q"]),
    ("hotkey_cancel", ["c-z"]),
    ("hotkey_new", ["c-n"]),
    ("hotkey_insert_filepath", ["c-f"]),
    ("hotkey_insert_newline", ["c-i"]),
    ("hotkey_select_context", ["c-o"]),
    ("hotkey_remove_context_temporarily", ["escape", "o"]),
    ("hotkey_export", ["c-g"]),
    ("hotkey_count_tokens", ["escape", "c"]),
    ("hotkey_launch_pager_view", ["c-p"]),
    ("hotkey_toggle_developer_mode", ["escape", "d"]),
    ("hotkey_toggle_multiline_entry", ["escape", "l"]),
    ("hotkey_list_directory_content", ["c-l"]),
    ("hotkey_launch_system_prompt", ["escape", "t"]),
    ("hotkey_text_to_speech_config", ["escape", "v"]),
    ("hotkey_voice_entry", ["c-s"]),
    ("hotkey_voice_entry_config", ["escape", "s"]),
    ("hotkey_display_key_combo", ["c-k"]),
    ("hotkey_display_device_info", ["escape", "k"]),
    ("hotkey_toggle_response_audio", ["c-y"]),
    ("hotkey_toggle_input_audio", ["escape", "y"]),
    ("hotkey_restart_app", ["escape", "r"]),
    ("hotkey_toggle_writing_improvement", ["escape", "w"]),
    ("hotkey_toggle_word_wrap", ["c-w"]),
    ("hotkey_toggle_mouse_support", ["escape", "m"]),
    ("hotkey_edit_current_entry", ["c-e"]),
    ("hotkey_edit_last_response", ["escape", "e"]),
    ("hotkey_swap_text_brightness", ["escape", "b"]),
    ("hotkey_select_plugins", ["escape", "p"]),
    # ["c-b"]; available
)

temporaryConfigs = [
    "runPython",
    "freeGeniusActions",
    "freeGeniusActionExamples",
    "freeGeniusActionParameters",
    "freeGeniusActionMethods",
    "setBasicConfigDone",
    "google_cloud_credentials_file",
    "actionHelp",
    "isTermux",
    "oai_client",
    "includeIpInSystemMessageTemp",
    "initialCompletionCheck",
    "promptStyle1",
    "promptStyle2",
    "runSpecificFuntion",
    "pluginsWithFunctionCall",
    "restartApp",
    "saveConfig",
    "aliases",
    "addPathAt",
    "multilineInput",
    "conversationStarted",
    "dynamicToolBarText",
    "tokenLimits",
    "currentMessages",
    "pagerContent",
    "selectAll",
    "clipboard",
    "showKeyBindings",
    "divider",
    "systemCommandPromptEntry",
    "stop_event",
    "spinner_thread",
    "tts",
    "isPygameInstalled",
    "isVlcPlayerInstalled",
    "accept_default",
    "defaultEntry",
    "pipIsUpdated",
    "setConfig",
    "excludeConfigList",
    "tempContent",
    "tempChunk",
    "predefinedContextTemp",
    "thisPlatform",
    "letMeDoItAI",
    "terminalColors",
    "letMeDoItFile",
    "letMeDoItAIFolder",
    "open",
    "inputSuggestions", # used with plugins; user input suggestions
    "outputTransformers", # used with plugins; transform output message
    "predefinedInstructions", # used with plugins; pre-defined instructions
    "predefinedContexts", # used with plugins; pre-defined contexts
    # used with plugins; function call
    "chatGPTApiFunctionSignatures",
    "chatGPTApiAvailableFunctions",
    "pythonFunctionResponse", # used with plugins; function call when function name is 'python'
    # LetMeDoItAI methods shared from Class LetMeDoItAI
    "getLocalStorage",
    "stopSpinning",
    "toggleMultiline",
    "print",
    "print2",
    "print3",
    "getWrappedHTMLText",
    "fineTuneUserInput",
    "launchPager",
    "addPagerText",
    "isTermux",
]

def saveConfig():
    configFile = os.path.join(config.letMeDoItAIFolder, "config.py")
    with open(configFile, "w", encoding="utf-8") as fileObj:
        for name in dir(config):
            excludeConfigList = temporaryConfigs + config.excludeConfigList
            if not name.startswith("__") and not name in excludeConfigList:
                try:
                    value = eval(f"config.{name}")
                    if not callable(value) and not str(value).startswith("<"):
                        fileObj.write("{0} = {1}\n".format(name, pprint.pformat(value)))
                except:
                    pass
config.saveConfig = saveConfig