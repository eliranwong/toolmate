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
    # unique configs in FreeGenius AI
    ('llmPlatform', "llamacpp"), # "llamacpp", "ollama", "gemini", "chatgpt", "letmedoit"
    ('intent_screening', False), # set True to increase both reliability and waiting time
    ('tool_dependence', 0.8), # range: 0.0 - 1.0; 0.0 means model's its own capabilities; 1.0; use at least one function call plugin among available tools
    ('tool_auto_selection_threshold', 0.5), # range: 0.0 - 1.0; tool auto selection is implemented when the closest tool match has a semantic distance lower than its value; manual selection from top matched tools is implemented when the closest distance fall between its value and tool_dependence
    ('tool_selection_max_choices', 4), # when tool search distance is higher than tool_auto_selection_threshold but lower than or equal to tool_dependence, manual selection implemented among the top matched tools.  This value specifies the maximum number of choices for manual tool selection in such cases.
    ('tokenizers_parallelism', 'true'), # 'true' / 'false'
    ('includeDeviceInfoInContext', False),
    ('includeIpInDeviceInfo', False),
    ('useAdditionalChatModel', False),
    ('stableDiffusion_model_path', ""),
    ('stableDiffusion_output_width', 512),
    ('stableDiffusion_output_height', 512),
    ('ollamaVisionModel', 'llava'), # ollama model used for vision
    ('ollamaMainModel', 'mistral'), # ollama model used for both task execution and conversation
    ('ollamaMainModel_num_ctx', 100000), # ollama main model context window
    ('ollamaMainModel_num_batch', 512), # ollama chat model batch size
    ('ollamaMainModel_num_predict', -1), # ollama main model maximum tokens
    ('ollamaMainModel_keep_alive', "5m"), # ollama main model keep alive time
    ('ollamaChatModel', 'phi'), # ollama model used for chat
    ('ollamaChatModel_num_ctx', 100000), # ollama chat model context window
    ('ollamaChatModel_num_batch', 512), # ollama chat model batch size
    ('ollamaChatModel_num_predict', -1), # ollama chat model maximum tokens
    ('ollamaChatModel_keep_alive', "5m"), # ollama chat model keep alive time
    ('llamacppServer_port', 8000),
    ('llamacppVisionModel_model_path', ''), # specify file path of llama.cpp model for vision
    ('llamacppVisionModel_clip_model_path', ''), # specify file path of llama.cpp clip model for vision
    ('llamacppMainModel_ollama_tag', ''), # selected ollama hosted model to run with llamacpp
    ('llamacppMainModel_model_path', ''), # specify file path of llama.cpp model for general purpose
    ('llamacppMainModel_repo_id', 'TheBloke/Mistral-7B-Instruct-v0.2-GGUF'), # llama.cpp model used for both task execution and conversation, e.g. 'TheBloke/phi-2-GGUF', 'NousResearch/Hermes-2-Pro-Mistral-7B-GGUF', 'NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO-GGUF'
    ('llamacppMainModel_filename', 'mistral-7b-instruct-v0.2.Q4_K_M.gguf'), # llama.cpp model used for both task execution and conversation, e.g. 'Hermes-2-Pro-Mistral-7B.Q4_K_M.gguf', 'Nous-Hermes-2-Mixtral-8x7B-DPO.Q4_K_M.gguf'
    ('llamacppMainModel_n_ctx', 0), # llama.cpp main model context window
    ('llamacppMainModel_max_tokens', 10000), # llama.cpp main model maximum tokens
    ('llamacppMainModel_n_gpu_layers', 0), # change to -1 to use GPU acceleration
    ('llamacppMainModel_n_batch', 512), # The batch size to use per eval
    ('llamacppChatModel_ollama_tag', ''), # selected ollama hosted model to run with llamacpp
    ('llamacppChatModel_model_path', ''), # specify file path of llama.cpp model for chat
    ('llamacppChatModel_repo_id', 'TheBloke/phi-2-GGUF'), # llama.cpp model used for chat, e.g. 'TheBloke/CodeLlama-7B-Python-GGUF'
    ('llamacppChatModel_filename', 'phi-2.Q4_K_M.gguf'), # llama.cpp model used for chat, e.g. 'codellama-7b-python.Q4_K_M.gguf'
    ('llamacppChatModel_n_ctx', 0), # llama.cpp chat model context window
    ('llamacppChatModel_max_tokens', 10000), # llama.cpp chat model maximum tokens
    ('llamacppChatModel_n_gpu_layers', 0), # change to -1 to use GPU acceleration
    ('llamacppChatModel_n_batch', 512), # The batch size to use per eval
    ('geminipro_max_output_tokens', 8192), # check supported value at https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models
    # common configs as in LetMeDoIt AI
    ('translateToLanguage', ''),
    ('dynamicTokenCount', False),
    ('use_oai_assistant', False), # support OpenAI Assistants API in AutoGen Agent Builder
    ('max_agents', 5), # maximum number of agents build manager can create.
    ('max_group_chat_round', 12), # AutoGen group chat maximum round
    ('env_QT_QPA_PLATFORM_PLUGIN_PATH', ''), # e.g. # deal with error: qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "~/apps/letmedoit/lib/python3.10/site-packages/cv2/qt/plugins" even though it was found.
    ('systemMessage_letmedoit', ''), # letmedoit system message
    ('systemMessage_llamacpp', 'You are a helpful assistant.'), # system message for standalone llamacpp chatbot
    ('systemMessage_chatgpt', 'You are a helpful assistant.'), # system message for standalone chatgpt chatbot
    ('systemMessage_geminipro', 'You are a helpful assistant.'), # system message for standalone geminipro chatbot
    ('systemMessage_palm2', 'You are a helpful assistant.'), # system message for standalone palm2 chatbot
    ('systemMessage_codey', 'You are an expert on coding.'), # system message for standalone codey chatbot
    ('embeddingModel', 'paraphrase-multilingual-mpnet-base-v2'), # reference: https://www.sbert.net/docs/pretrained_models.html
    ('customTextEditor', ""), # e.g. 'micro -softwrap true -wordwrap true'; built-in text editor eTextEdit is used when it is not defined.
    ('pagerView', False),
    ('usePygame', False), # force to use pygame for audio playback even VLC player is installed
    ('wrapWords', True),
    ('mouseSupport', False),
    ('autoUpgrade', True),
    #('chatbot', 'chatgpt'),
    ('customTrayCommands', ['mistral', 'llama2']),
    ('chatGPTApiModel', 'gpt-3.5-turbo'),
    ('chatGPTApiMaxTokens', 4000),
    ('chatGPTApiMinTokens', 256),
    #('chatGPTApiNoOfChoices', 1),
    ('chatGPTApiFunctionCall', "auto"),
    ('passFunctionCallReturnToChatGPT', True),
    ('llmTemperature', 0.3),
    ('max_consecutive_auto_reply', 10), # work with pyautogen
    ('memoryClosestMatches', 5),
    ('rag_useAutoRetriever', False),
    ('rag_closestMatches', 5),
    ('rag_retrieverSettings', {'search_kwargs': {'k': 5}}),
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
    ("elevenlabsVoice", "21m00Tcm4TlvDq8ikWAM"),
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
    "llamacppServer",
    "llamacppVisionServer",
    "geminipro_model",
    "geminipro_generation_config",
    "geminipro_safety_settings",
    "llamacppMainModel",
    "llamacppChatModel",
    "new_chat_response",
    "runPython",
    "freeGeniusActions",
    "freeGeniusActionExamples",
    "freeGeniusActionParameters",
    "freeGeniusActionMethods",
    "google_cloud_credentials_file",
    "actionHelp",
    "isTermux",
    "oai_client",
    "includeIpInDeviceInfoTemp",
    "initialCompletionCheck",
    "promptStyle1",
    "promptStyle2",
    "selectedTool",
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
    "isPipUpdated",
    "setConfig",
    "excludeConfigList",
    "tempContent",
    "tempChunk",
    "predefinedContextTemp",
    "thisPlatform",
    "letMeDoItAI",
    "terminalColors",
    "freeGeniusAIFile",
    "freeGeniusAIFolder",
    "open",
    "inputSuggestions", # used with plugins; user input suggestions
    "outputTransformers", # used with plugins; transform output message
    "predefinedInstructions", # used with plugins; pre-defined instructions
    "predefinedContexts", # used with plugins; pre-defined contexts
    # used with plugins; function call
    "toolFunctionSchemas",
    "toolFunctionMethods",
    "pythonFunctionResponse", # used with plugins; function call when function name is 'python'
    # FreeGenius methods shared from Class FreeGenius
    "getLocalStorage",
    "localStorage",
    "stopSpinning",
    "toggleMultiline",
    "getWrappedHTMLText",
    "fineTuneUserInput",
    "launchPager",
    "addPagerText",
    "isTermux",
]

def saveConfig():
    configFile = os.path.join(config.freeGeniusAIFolder, "config.py")
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