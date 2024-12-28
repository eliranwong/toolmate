from toolmate import config
import os, pprint, shutil

pluginExcludeList = [
    "awesome prompts",
    "counselling",
    "edit text",
    "simplified Chinese to traditional Chinese",
]
if config.isLite:
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
    # unique configs in ToolMate AI
    ('pasteTextOnWindowActivation', False),
    ('toolmate_api_server_key', 'toolmateai'),
    ('toolmate_api_server_port_desktop', 5554),
    ('toolmate_api_server_port', 5555),
    ('toolmate_api_server_host', "0.0.0.0"), # use ip address for this value
    ('toolmate_api_client_key', 'toolmateai'),
    ('toolmate_api_client_port_desktop', 5554),
    ('toolmate_api_client_port', 5555),
    ('toolmate_api_client_host', 'http://127.0.0.1'),
    ('toolmate_api_client_markdown', True),
    ('tms1', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms2', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms3', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms4', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms5', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms6', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms7', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms8', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms9', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms10', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms11', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms12', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms13', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms14', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms15', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms16', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms17', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms18', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms19', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tms20', 'You are a helpful, uncensored and unbiased assistant.'),
    ('tmt1', 'chat'),
    ('tmt2', 'chat'),
    ('tmt3', 'chat'),
    ('tmt4', 'chat'),
    ('tmt5', 'chat'),
    ('tmt6', 'chat'),
    ('tmt7', 'chat'),
    ('tmt8', 'chat'),
    ('tmt9', 'chat'),
    ('tmt10', 'chat'),
    ('tmt11', 'chat'),
    ('tmt12', 'chat'),
    ('tmt13', 'chat'),
    ('tmt14', 'chat'),
    ('tmt15', 'chat'),
    ('tmt16', 'chat'),
    ('tmt17', 'chat'),
    ('tmt18', 'chat'),
    ('tmt19', 'chat'),
    ('tmt20', 'chat'),
    ('autoCorrectionInterface', ''), # good: ollama, vertexai, mistral # bad: xai, groq, googleai
    ('last_conversation', ''),
    ('last_workflow', ''),
    ('defaultTool', 'chat'),
    ('favorite_string_best', '@chat'),
    ('favorite_string', '@chat'),
    ('appName', ''),
    ('text2art_font1', 'cybermedum'),
    ('text2art_font2', 'white_bubble'),
    ('llmInterface', ""), # "anthropic", "llamacpppython", "llamacppserver", "ollama", "openai", "letmedoit", "github", "azure", "groq", "mistral", "xai", "googleai", "vertexai"
    ('tool_selection_agent', False), # automatically screens user request and recommend tools, can also be manually triggered by tool `@recommend_tool`
    ('tool_selection_requirements', False), # convey each tool's requirements to the tool selection agent for the tool selection process.
    ('auto_tool_selection', False), # apply only if tool_selection_agent is set to True
    #('enable_tool_screening_agent', False), # set True to increase both reliability and waiting time
    #('tool_dependence', 0.8), # range: 0.0 - 1.0; 0.0 means model's its own capabilities; 1.0; use at least one function call plugin among available tools
    #('tool_auto_selection_threshold', 0.5), # range: 0.0 - 1.0; tool auto selection is implemented when the closest tool match has a semantic distance lower than its value; manual selection from top matched tools is implemented when the closest distance fall between its value and tool_dependence
    #('tool_selection_max_choices', 4), # when tool search distance is higher than tool_auto_selection_threshold but lower than or equal to tool_dependence, manual selection implemented among the top matched tools.  This value specifies the maximum number of choices for manual tool selection in such cases.
    ('tokenizers_parallelism', 'true'), # 'true' / 'false'
    ('includeDeviceInfoInContext', False),
    ('includeIpInDeviceInfo', False),
    ('zero_shot_classification_model', 'facebook/bart-large-mnli'),
    ('labels_kind', ("greeting", "translation", "math", "question", "description", "command", "statement", "insturction")),
    ('labels_information', ("common knowledge", "published content", "trained knowledge", "archived records", "historical records", "programming", "technical knowledge", "religious knowledge", "literature", "evolving data", "recent updates", "latest information", "current information", "up-to-date news", "device information", "real-time data")),
    ('labels_action', ("calculation", "writing a text-response", "carrying out a task on your device")),
    ('labels_kind_chat_only_options', ("greeting", "translation", "math")),
    ('labels_kind_information_options', ("question", "description")),
    ('labels_information_chat_only_options', ("common knowledge", "published content", "trained knowledge", "archived records", "historical records", "programming", "technical knowledge", "religious knowledge", "literature")),
    ('labels_action_chat_only_options', ("calculation", "writing a text-response")),
    ('useAdditionalChatModel', False),
    ('stableDiffusion_verbose', False),
    ('stableDiffusion_model_path', ""),
    ('stableDiffusion_output_width', 512),
    ('stableDiffusion_output_height', 512),
    ('stableDiffusion_sample_steps', 20),
    ('flux_verbose', False),
    ('flux_model_path', ""),
    ('flux_output_width', 1024),
    ('flux_output_height', 1024),
    ('flux_sample_steps', 20),
    ('imageheight', None),
    ('imagewidth', None),
    ('imagesteps', None),
    ('imagehd', False),
    ('autogenstudio_server_port', 8081),
    #('perplexica_directory', ""),
    #('perplexica_ip', "127.0.0.1"),
    #('perplexica_port', 3000),
    ('customUrls', {"Perplexica":"http://localhost:3000", "SearXNG":"http://localhost:4000",}),
    #('ollamaToolServer', "http://127.0.0.1"),
    #('ollamaChatServer', "http://127.0.0.1"),
    ('ollamaToolServer_protocol', "http://"),
    ('ollamaChatServer_protocol', "http://"),
    ('ollamaToolServer_host', "127.0.0.1"),
    ('ollamaChatServer_host', "127.0.0.1"),
    ('ollamaToolServer_port', 11434),
    ('ollamaChatServer_port', 11434),
    #('ollamaVisionServer_ip', "127.0.0.1"),
    #('ollamaVisionServer_port', 11434),
    ('ollamaVisionModel', 'llava'), # ollama model used for vision
    ('ollamaToolModel', 'granite3-dense:2b' if config.isTermux else 'wizardlm2'), # ollama model used for both task execution and conversation
    ('ollamaToolModel_additional_options', {}),
    ('ollamaChatModel_additional_options', {}),
    ('ollamaToolModel_num_ctx', 2048), # ollama tool model context window
    ('ollamaToolModel_num_batch', 512), # ollama chat model batch size
    ('ollamaToolModel_num_predict', -1), # ollama tool model maximum tokens
    ('ollamaToolModel_keep_alive', "5m"), # ollama tool model keep alive time
    ('ollamaChatModel', 'llama3.2:3b' if config.isTermux else 'llama3.1'), # ollama model used for chat
    ('ollamaChatModel_num_ctx', 2048), # ollama chat model context window
    ('ollamaChatModel_num_batch', 512), # ollama chat model batch size
    ('ollamaChatModel_num_predict', -1), # ollama chat model maximum tokens
    ('ollamaChatModel_keep_alive', "5m"), # ollama chat model keep alive time
    ('llamacppToolModel_verbose', False),
    ('llamacppChatModel_verbose', False),
    ('llamacppVisionModel_verbose', False),
    ('customToolServer_protocol', "http://"),
    ('customChatServer_protocol', "http://"),
    ('customVisionServer_protocol', "http://"),
    ('customToolServer_command', ""),
    ('customChatServer_command', ""),
    ('customVisionServer_command', ""),
    ('customToolServer_stop', ["</s>", "<|im_end|>", "[/INST]", "<end_of_turn>", "<|END_OF_TURN_TOKEN|>", "<|eot_id|>", "<|endoftext|>"]),
    ('customChatServer_stop', ["</s>", "<|im_end|>", "[/INST]", "<end_of_turn>", "<|END_OF_TURN_TOKEN|>", "<|eot_id|>", "<|endoftext|>"]),
    ('customVisionServer_stop', ["</s>", "<|im_end|>", "[/INST]", "<end_of_turn>", "<|END_OF_TURN_TOKEN|>", "<|eot_id|>", "<|endoftext|>"]), # https://github.com/ggerganov/llama.cpp/wiki/Templates-supported-by-llama_chat_apply_template
    ('customToolServer_timeout', 20),
    ('customChatServer_timeout', 20),
    ('customVisionServer_timeout', 20),
    ('customToolServer_additional_options', {}),
    ('customChatServer_additional_options', {}),
    ('customVisionServer_additional_options', {}),
    ('customToolServer_ip', "127.0.0.1"),
    ('customChatServer_ip', "127.0.0.1"),
    ('customVisionServer_ip', "127.0.0.1"),
    ('customToolServer_port', 8000),
    ('customChatServer_port', 8001),
    ('customVisionServer_port', 8002),
    ('llamacppToolModel_server_ip', "127.0.0.1"),
    ('llamacppChatModel_server_ip', "127.0.0.1"),
    ('llamacppVisionModel_server_ip', "127.0.0.1"),
    ('llamacppToolModel_server_protocol', "http://"),
    ('llamacppChatModel_server_protocol', "http://"),
    ('llamacppVisionModel_server_protocol', "http://"),
    ('llamacppToolModel_server_port', 8000),
    ('llamacppChatModel_server_port', 8001),
    ('llamacppVisionModel_server_port', 8002),
    ('llamacppVisionModel_model_path', ''), # specify file path of llama.cpp model for vision
    ('llamacppVisionModel_clip_model_path', ''), # specify file path of llama.cpp clip model for vision
    ('llamacppVisionModel_additional_server_options', ''),
    ('llamacppVisionModel_additional_model_options', {}),
    ('llamacppVisionModel_additional_chat_options', {}),
    ('llamacppVisionModel_max_tokens', 2048), # llama.cpp vision model maximum tokens
    ('llamacppVisionModel_n_gpu_layers', 0), # -1 automatic if gpu is in place
    ('llamacppVisionModel_n_batch', 512),
    ('llamacppVisionModel_n_ctx', 0),
    ('llamacppToolModel_additional_server_options', ''),
    ('llamacppChatModel_additional_server_options', ''),
    ('llamacppToolModel_additional_model_options', {}),
    ('llamacppToolModel_additional_chat_options', {}),
    ('llamacppChatModel_additional_model_options', {}),
    ('llamacppChatModel_additional_chat_options', {}),
    ('llamacppToolModel_ollama_tag', ''), # selected ollama hosted model to run with llamacpp
    ('llamacppToolModel_model_path', ''), # specify file path of llama.cpp model for general purpose
    ('llamacppToolModel_repo_id', 'bartowski/Llama-3.2-3B-Instruct-GGUF' if config.isLite else 'MaziyarPanahi/WizardLM-2-7B-GGUF'), # llama.cpp model used for both task execution and conversation, e.g. 'TheBloke/phi-2-GGUF', 'NousResearch/Hermes-2-Pro-Mistral-7B-GGUF', 'NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO-GGUF'
    ('llamacppToolModel_filename', 'Llama-3.2-3B-Instruct-Q4_K_M.gguf' if config.isLite else 'WizardLM-2-7B.Q4_K_M.gguf'), # llama.cpp model used for both task execution and conversation, e.g. 'Hermes-2-Pro-Mistral-7B.Q4_K_M.gguf', 'Nous-Hermes-2-Mixtral-8x7B-DPO.Q4_K_M.gguf'
    ('llamacppToolModel_n_ctx', 0), # llama.cpp tool model context window
    ('llamacppToolModel_max_tokens', 2048), # llama.cpp tool model maximum tokens
    ('llamacppToolModel_n_gpu_layers', 0), # change to -1 to use GPU acceleration
    ('llamacppToolModel_n_batch', 512), # The batch size to use per eval
    ('llamacppChatModel_ollama_tag', ''), # selected ollama hosted model to run with llamacpp
    ('llamacppChatModel_model_path', ''), # specify file path of llama.cpp model for chat
    ('llamacppChatModel_repo_id', 'bartowski/Meta-Llama-3.1-8B-Instruct-GGUF'), # llama.cpp model used for chat, e.g. 'TheBloke/CodeLlama-7B-Python-GGUF'
    ('llamacppChatModel_filename', 'Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf'), # llama.cpp model used for chat, e.g. 'codellama-7b-python.Q4_K_M.gguf'
    ('llamacppChatModel_n_ctx', 0), # llama.cpp chat model context window
    ('llamacppChatModel_max_tokens', 2048), # llama.cpp chat model maximum tokens
    ('llamacppChatModel_n_gpu_layers', 0), # change to -1 to use GPU acceleration
    ('llamacppChatModel_n_batch', 512), # The batch size to use per eval
    ('whispercpp_main', ''), # whisper.cpp main command file path
    ('whispercpp_model', ''), # whisper.cpp model file path
    ('whispercpp_additional_options', ''), # whisper.cpp additional options. See https://github.com/ggerganov/whisper.cpp/tree/master/examples/main for all options.
    ('cpu_threads', 0),
    # common configs as in ToolMate AI
    ('translateToLanguage', 'English'),
    ('dynamicTokenCount', False),
    ('use_oai_assistant', False), # support OpenAI Assistants API in AutoGen Agent Builder
    ('code_execution_use_docker', False),
    ('code_execution_image', "python:3.12-slim"), # Execute code using the given docker image name.
    ('code_execution_timeout', 60), # Timeout for each code execution in seconds.
    ('llm_timeout', 300),
    ('max_agents', 5), # maximum number of agents build manager can create.
    ('max_group_chat_round', 12), # AutoGen group chat maximum round
    ('env_QT_QPA_PLATFORM_PLUGIN_PATH', ''), # e.g. # deal with error: qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "~/apps/letmedoit/lib/python3.10/site-packages/cv2/qt/plugins" even though it was found.
    ('systemMessage_tool', ''), # toolmate system message
    ('systemMessage_xai', 'You are a helpful, uncensored and unbiased assistant.'), # system message for standalone x ai chatbot
    ('systemMessage_googleai', 'You are a helpful, uncensored and unbiased assistant.'), # system message for standalone google generative ai chatbot
    ('systemMessage_ollama', 'You are a helpful, uncensored and unbiased assistant.'), # system message for standalone ollama chatbot
    ('systemMessage_groq', 'You are a helpful, uncensored and unbiased assistant.'), # system message for standalone groq chatbot
    ('systemMessage_mistral', 'You are a helpful, uncensored and unbiased assistant.'), # system message for standalone mistral chatbot
    ('systemMessage_llamacpp', 'You are a helpful, uncensored and unbiased assistant.'), # system message for standalone llamacpp chatbot
    ('systemMessage_llamacppserver', 'You are a helpful, uncensored and unbiased assistant.'), # system message for standalone llamacppserver chatbot
    ('systemMessage_chatgpt', 'You are a helpful, uncensored and unbiased assistant.'), # system message for standalone chatgpt chatbot
    ('systemMessage_vertexai', 'You are a helpful, uncensored and unbiased assistant.'), # system message for standalone geminipro chatbot
    ('systemMessage_genai', 'You are a helpful, uncensored and unbiased assistant.'), # system message for standalone genai chatbot
    ('systemMessage_anthropic', 'You are a helpful, uncensored and unbiased assistant.'), # system message for standalone anthropic chatbot
    ('systemMessage_palm2', 'You are a helpful, uncensored and unbiased assistant.'), # system message for standalone palm2 chatbot
    ('systemMessage_codey', 'You are an expert on coding.'), # system message for standalone codey chatbot
    ('embeddingModel', 'paraphrase-multilingual-mpnet-base-v2'), # reference: https://www.sbert.net/docs/pretrained_models.html
    ('customTextEditor', ""), # e.g. 'micro -softwrap true -wordwrap true'; built-in text editor eTextEdit is used when it is not defined.
    ('pagerView', False),
    ('usePygame', False), # force to use pygame for audio playback even VLC player is installed
    ('wrapWords', True),
    ('mouseSupport', False),
    ('autoUpgrade', True),
    ('customTrayCommands', ['mistral', 'llama3']),
    ('azureOpenAIModels', ["gpt-4o", "gpt-4o-mini"]),
    ('azureApi_key', ''),
    ('azureBaseUrl', ''),
    ('githubApi_key', ''),
    ('githubBaseUrl', "https://models.inference.ai.azure.com"),
    ('chatGPTApiModel', 'gpt-4o'),
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
    ('wsay_voice', "1"),
    ('wsay_speed', "50"),
    ('say_voice', ""),
    ('say_speed', "200"),
    ('piper_voice', "en_US-lessac-medium"),
    ('wsay_additional_options', ""),
    ('say_additional_options', ""),
    ('piper_additional_options', ""),
    ('tavilyApi_key', ''),
    ('groqApi_key', ''),
    ('groqApi_tool_model', 'llama-3.3-70b-versatile'),
    ('groqApi_tool_model_additional_chat_options', {}),
    ('groqApi_chat_model', 'llama-3.3-70b-versatile'),
    ('groqApi_chat_model_additional_chat_options', {}),
    ('groqApi_tool_model_max_tokens', 2048),
    ('groqApi_chat_model_max_tokens', 2048),
    ('mistralApi_key', ''),
    ('mistralApi_tool_model', 'mistral-large-latest'),
    ('mistralApi_tool_model_additional_chat_options', {}),
    ('mistralApi_chat_model', 'mistral-large-latest'),
    ('mistralApi_chat_model_additional_chat_options', {}),
    ('mistralApi_tool_model_max_tokens', 2048),
    ('mistralApi_chat_model_max_tokens', 2048),
    ('xaiApi_key', ''),
    ('xaiApi_tool_model', "grok-beta"),
    ('xaiApi_tool_model_additional_chat_options', {}),
    ('xaiApi_chat_model', "grok-beta"),
    ('xaiApi_chat_model_additional_chat_options', {}),
    ('xaiApi_tool_model_max_tokens', 127999),
    ('xaiApi_chat_model_max_tokens', 127999),
    ('googleaiApi_key', ''),
    ('googleaiApi_tool_model', "gemini-1.5-flash"),
    ('googleaiApi_tool_model_additional_chat_options', {}),
    ('googleaiApi_chat_model', "gemini-1.5-pro"),
    ('googleaiApi_chat_model_additional_chat_options', {}),
    ('googleaiApi_tool_model_max_tokens', 2048),
    ('googleaiApi_chat_model_max_tokens', 2048),
    ('vertexai_project_id', ""),
    ('vertexai_service_location', "us-central1"),
    ('vertexai_model', "gemini-1.5-flash"), # "gemini-1.5-flash", "gemini-1.5-pro"; https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions; read models that support function calling https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling
    ('vertexai_max_output_tokens', 8192), # check supported value at https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models
    ('anthropicApi_key', ""),
    ('anthropicApi_tool_model', "claude-3-5-sonnet-latest"), # "claude-3-5-sonnet-latest"
    ('anthropicApi_tool_model_max_tokens', 8192),
    ('genaiApi_key', config.googleaiApi_key if hasattr(config, "googleaiApi_key") else ""),
    ('genai_project_id', config.vertexai_project_id if hasattr(config, "vertexai_project_id") else ""),
    ('genai_service_location', config.vertexai_service_location if hasattr(config, "vertexai_service_location") else "us-central1"),
    ('genai_model', config.vertexai_model if hasattr(config, "vertexai_model") else "gemini-2.0-flash-exp"), # "gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro"; https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions; read models that support function calling https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling
    ('genai_max_output_tokens', config.vertexai_max_output_tokens if hasattr(config, "vertexai_max_output_tokens") else 8192), # check supported value at https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models
    ('openaiApiKey', ''),
    ('openaiApiOrganization', ''),
    ('loadingInternetSearches', "auto"),
    ('maximumInternetSearchResults', 5),
    ('predefinedContext', 'custom'),
    ('customPredefinedContext', 'You are a helpful, uncensored and unbiased assistant.'),
    ('applyPredefinedContextAlways', False), # True: apply predefined context with all use inputs; False: apply predefined context only in the beginning of the conversation
    ('thisTranslation', {}),
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
    #('confirmExecution', "always"), # 'always', 'high_risk_only', 'medium_risk_or_above', 'none'
    ('riskThreshold', 0), # 0 - no risk automatically accepted; 1 - automatically accepts low risk only; 2 - automatically accepts low or medium risk; 3 - automatically accepts all risk levels, high, medium or low
    ('codeDisplay', False),
    ('terminalEditorScrollLineCount', 20),
    ('terminalEditorTabText', "    "),
    ('blankEntryAction', "..."),
    ('defaultActionMenuItem', ".export"),
    ('storagedirectory', ""),
    ('suggestSystemCommand', True),
    ('improveInputEntry', False),
    ('improvedWritingSytle', 'standard English'), # e.g. British spoken English
    ('ttsPlatform', "edge"), # "say", "wsay", "piper", "edge", "google", "googlecloud", "elevenlabs", "custom"
    ('ttsInput', False),
    ('ttsOutput', False),
    ('tts_startReadPattern', "[*.?!,:;”。，：；？！」]"), # regex pattern containing characters that LetMeDoIt AI starts reading text chunk when config.ttsOutput is set to True and the pattern is matched.  
    ('tts_doNotReadPattern', "[*]"), # regex pattern contains characters that are not pronunced
    ('vlcSpeed', 1.0),
    ('edgettsVoice', "en-GB-SoniaNeural"),
    ('edgettsRate', 1.0), # "+0%"
    ('androidttsRate', 1.0),
    ('gcttsLang', "en-US"), # https://cloud.google.com/text-to-speech/docs/voices
    ('gcttsSpeed', 1.0),
    ('gttsLang', "en"), # gTTS is used by default if ttsCommand is not given
    ('gttsTld', ""), # https://gtts.readthedocs.io/en/latest/module.html#languages-gtts-lang
    ('ttsCommand', ""), # ttsCommand is used if it is given; offline tts engine runs faster; on macOS [suggested speak rate: 100-300], e.g. "say -r 200 -v Daniel"; on Ubuntu [espeak; speed in approximate words per minute; 175 by default], e.g. "espeak -s 175 -v en"; remarks: always place the voice option, if any, at the end
    ('ttsCommandSuffix', ""), # try on Windows; ttsComand = '''Add-Type -TypeDefinition 'using System.Speech.Synthesis; class TTS { static void Main(string[] args) { using (SpeechSynthesizer synth = new SpeechSynthesizer()) { synth.Speak(args[0]); } } }'; [TTS]::Main('''; ttsCommandSuffix = ")"; a full example is Add-Type -TypeDefinition 'using System.Speech.Synthesis; class TTS { static void Main(string[] args) { using (SpeechSynthesizer synth = new SpeechSynthesizer()) { synth.Speak(args[0]); } } }'; [TTS]::Main("Text to be read")
    ("ttsLanguages", ["en", "en-gb", "en-us", "zh", "yue", "el"]), # users can edit this item in config.py to support more or less languages
    ("ttsLanguagesCommandMap", {"en": "", "en-gb": "", "en-us": "", "zh": "", "yue": "", "el": "",}), # advanced users need to edit this item manually to support different voices with customised tts command, e.g. ttsCommand set to "say -r 200 -v Daniel" and ttsLanguagesCommandMap set to {"en": "Daniel", "en-gb": "Daniel", "en-us": "", "zh": "", "yue": "", "el": "",}
    ("fabricPath", "fabric"),
    ("fabricPatterns", os.path.join(os.path.expanduser("~"), ".config", "fabric", "patterns")),
    ("openweathermapApi", ""),
    ("bing_api_key", ""),
    ("rapid_api_key", ""),
    ("elevenlabsApi", ""),
    ("elevenlabsVoice", "21m00Tcm4TlvDq8ikWAM"),
    ("pyaudioInstalled", False),
    ("voskModel", "vosk-model-small-en-us-0.15"),
    ("voiceTypingPlatform", "google"), # "google", "googlecloud", "whisper"
    ("voiceTypingLanguage", "en-US"), # https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
    ("voiceTypingAdjustAmbientNoise", True),
    ("voiceTypingNotification", True),
    ("voiceTypingAutoComplete", False),
    ("voiceTypingWhisperEnglishModel", "base"), # "tiny", "base", "small", "medium", "large"; read https://github.com/openai/whisper/tree/main#available-models-and-languages
    ("google_cloud_credentials", ""),
    ("enabledGoogleAPIs", ["Vertex AI"]), # "Vertex AI", "Speech-to-Text", "Text-to-Speech"
    ("desktopAssistantFontSize", 12),
    ("desktopAssistantWidth", 500),
    ("desktopAssistantHeight", 900),
    ("parserStandarisation", False),
    ("autoRestoreConfigs", True),
    ("hotkey_exit", ["c-q"]),
    ("hotkey_cancel", ["c-z"]),
    ("hotkey_new", ["c-n"]),
    ("hotkey_insert_file_path", ["escape", "o"]),
    ("hotkey_insert_newline", ["c-i"]),
    ("hotkey_insert_tool", ["escape", "i"]),
    ("hotkey_open_chat_records", ["c-o"]),
    #("hotkey_open_plain_text_file", ["escape", "o"]),
    ("hotkey_open_last_conversation", ["c-l"]),
    ("hotkey_export", ["c-g"]),
    ("hotkey_count_tokens", ["escape", "c"]),
    ("hotkey_launch_pager_view", ["c-p"]),
    ("hotkey_toggle_developer_mode", ["escape", "d"]),
    ("hotkey_toggle_multiline_entry", ["escape", "l"]),
    ("hotkey_list_directory_content", ["c-l"]),
    ("hotkey_launch_xonsh", ["escape", "x"]),
    #("hotkey_launch_system_prompt", ["escape", "t"]),
    ("hotkey_voice_generation_config", ["escape", "v"]),
    ("hotkey_voice_entry", ["c-s"]),
    ("hotkey_voice_recognition_config", ["escape", "s"]),
    ("hotkey_display_key_combo", ["c-k"]),
    ("hotkey_display_device_info", ["escape", "k"]),
    ("hotkey_toggle_response_audio", ["c-y"]),
    ("hotkey_toggle_input_audio", ["escape", "y"]),
    #("hotkey_restart_app", ["escape", "r"]),
    ("hotkey_read_conversation", ["escape", "r"]),
    ("hotkey_toggle_input_improvement", ["escape", "w"]),
    ("hotkey_toggle_word_wrap", ["c-w"]),
    ("hotkey_toggle_mouse_support", ["escape", "m"]),
    ("hotkey_edit_current_entry", ["c-e"]),
    ("hotkey_edit_last_response", ["escape", "e"]),
    #("hotkey_swap_text_brightness", ["escape", "b"]), # "escape", "b" conflict with key combo to jump to the beginning of a line
    ("hotkey_select_plugins", ["escape", "p"]),
    ("hotkey_insert_favorite_entry", ["c-f"]),
    ("hotkey_insert_bestliked_entry", ["c-b"]),
)

temporaryConfigs = [
    "terminalEnableTermuxAPI",
    "this_api_server_host",
    "this_api_server_port",
    "online",
    "api_server_id",
    "custom_config",
    "systemMessage_tool_current",
    "completer_user",
    "completer_developer",
    "actionKeys",
    "deviceInfoPlugins",
    "datetimeSensitivePlugins",
    "tempChatSystemMessage",
    "allEnabledTools",
    "toolmate",
    "chatGui",
    "builtinTools",
    "toolPattern",
    "llamacppserver_tool_client",
    "llamacppserver_chat_client",
    "tempInterface",
    "llamacppServer",
    "llamacppChatServer",
    "llamacppVisionServer",
    "autogenstudioServer",
    "gemini_generation_config",
    "gemini_safety_settings",
    "llamacppToolModel",
    "llamacppChatModel",
    "new_chat_response",
    "runPython",
    "toolMateActions",
    "toolMateActionExamples",
    "toolMateActionParameters",
    "toolMateActionMethods",
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
    "addToolAt",
    "multilineInput",
    "conversationStarted",
    "dynamicToolBarText",
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
    "toolTextOutput",
    "llmTextChunk",
    "predefinedContextTemp",
    "thisPlatform",
    "letMeDoItAI",
    "terminalColors",
    "toolMateAIFile",
    "toolMateAIFolder",
    "open",
    "inputSuggestions", # used with plugins; user input suggestions
    "outputTextConverters", # used with plugins; transform output message
    "predefinedInstructions", # used with plugins; pre-defined instructions
    "predefinedContexts", # used with plugins; pre-defined contexts
    "predefinedChatSystemMessages", # used with plugins; pre-defined chat system messages
    # used with plugins; function call
    "toolFunctionSchemas",
    "toolFunctionMethods",
    "pythonFunctionResponse", # used with plugins; function call when function name is 'python'
    # ToolMate methods shared from Class ToolMate
    "getLocalStorage",
    "localStorage",
    "stopSpinning",
    "toggleMultiline",
    "getWrappedHTMLText",
    "addPredefinedContext",
    "launchPager",
]

def saveConfig():
    if not config.tempInterface:
        configFile = os.path.join(config.toolMateAIFolder, "config.py")
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
    if os.path.isdir(config.localStorage):
        shutil.copy(configFile, os.path.join(config.localStorage, "config_lite_backup.py" if config.isLite else "config_backup.py"))
config.saveConfig = saveConfig