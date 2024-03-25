import os
thisFile = os.path.realpath(__file__)
packageFolder = os.path.dirname(thisFile)
package = os.path.basename(packageFolder)
if os.getcwd() != packageFolder:
    os.chdir(packageFolder)
configFile = os.path.join(packageFolder, "config.py")
if not os.path.isfile(configFile):
    open(configFile, "a", encoding="utf-8").close()
from freegenius import config, getLocalStorage
from freegenius import print1, print2, print3
config.isTermux = True if os.path.isdir("/data/data/com.termux/files/home") else False

import traceback, json, pprint, wcwidth, textwrap, threading, time, shutil
import openai, tiktoken
from openai import OpenAI
from pygments.styles import get_style_by_name
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit import prompt
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings, ConditionalKeyBindings
from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard
from prompt_toolkit.application import run_in_terminal
from freegenius.utils.vlc_utils import VlcUtil
from freegenius.utils.tts_utils import TTSUtil
from freegenius.utils.config_essential import defaultSettings
from freegenius.utils.download import Downloader
from llama_cpp import Llama
from pathlib import Path
from PIL import Image
import speech_recognition as sr
# a dummy import line to resolve ALSA error display
import sounddevice


class HealthCheck:

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

    models = tuple(tokenLimits.keys())

    @staticmethod
    def setBasicConfig():
        if not hasattr(config, "setBasicConfigDone") or not config.setBasicConfigDone:
            # package folder
            config.freeGeniusAIFolder = packageFolder
            config.excludeConfigList = []
            # Default Settings
            for key, value in defaultSettings:
                if not hasattr(config, key):
                    value = pprint.pformat(value)
                    exec(f"""config.{key} = {value} """)
            # tts
            config.isVlcPlayerInstalled = VlcUtil.isVlcPlayerInstalled()
            config.tts = False if not config.isVlcPlayerInstalled and not config.isPygameInstalled and not config.ttsCommand and not config.elevenlabsApi else True
            # Google Credentials
            if config.google_cloud_credentials and os.path.isfile(config.google_cloud_credentials):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.google_cloud_credentials
            else:
                files = getLocalStorage()
                gccfile1 = os.path.join(files, "credentials_google_cloud.json")
                gccfile2 = os.path.join(files, "credentials_googleaistudio.json")
                gccfile3 = os.path.join(files, "credentials_googletts.json")
                # set required file
                config.google_cloud_credentials_file = gccfile1

                if os.path.isfile(gccfile1):
                    config.google_cloud_credentials = gccfile1
                elif os.path.isfile(gccfile2):
                    config.google_cloud_credentials = gccfile2
                elif os.path.isfile(gccfile3):
                    config.google_cloud_credentials = gccfile3
                else:
                    config.google_cloud_credentials = ""
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.google_cloud_credentials if config.google_cloud_credentials else ""
                
            # print functions
            HealthCheck.setPrint()

            config.setBasicConfigDone = True


    @staticmethod
    def simplePrompt(inputIndicator="", validator=None, default="", accept_default=False, completer=None, promptSession=None, style=None, is_password=False, bottom_toolbar=None):
        this_key_bindings = KeyBindings()
        @this_key_bindings.add(*config.hotkey_exit)
        def _(event):
            buffer = event.app.current_buffer
            buffer.text = config.exit_entry
            buffer.validate_and_handle()
        @this_key_bindings.add(*config.hotkey_cancel)
        def _(event):
            buffer = event.app.current_buffer
            buffer.reset()
        @this_key_bindings.add(*config.hotkey_insert_newline)
        def _(event):
            buffer = event.app.current_buffer
            buffer.newline()
        @this_key_bindings.add(*config.hotkey_toggle_word_wrap)
        def _(_):
            config.wrapWords = not config.wrapWords
            config.saveConfig()
            run_in_terminal(lambda: config.print3(f"Word Wrap: '{'enabled' if config.wrapWords else 'disabled'}'!"))
        @this_key_bindings.add(*config.hotkey_toggle_response_audio)
        def _(_):
            if config.tts:
                config.ttsOutput = not config.ttsOutput
                config.saveConfig()
                run_in_terminal(lambda: config.print3(f"Response Audio: '{'enabled' if config.ttsOutput else 'disabled'}'!"))
        @this_key_bindings.add(*config.hotkey_voice_entry)
        def _(event):
            # reference: https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py
            def voiceTyping():
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    if config.voiceTypingNotification:
                        TTSUtil.playAudioFilePygame(os.path.join(packageFolder, "audio", "notification1_mild.mp3"))
                    #run_in_terminal(lambda: print2("Listensing to your voice ..."))
                    if config.voiceTypingAdjustAmbientNoise:
                        r.adjust_for_ambient_noise(source)
                    audio = r.listen(source)
                if config.voiceTypingNotification:
                    TTSUtil.playAudioFilePygame(os.path.join(packageFolder, "audio", "notification2_mild.mp3"))
                #run_in_terminal(lambda: print2("Processing to your voice ..."))
                if config.voiceTypingPlatform == "google":
                    # recognize speech using Google Speech Recognition
                    try:
                        # check google.recognize_legacy in SpeechRecognition package
                        # check availabl languages at: https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
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

            if config.pyaudioInstalled:
                buffer = event.app.current_buffer
                buffer.text = f"{buffer.text}{' ' if buffer.text else ''}{voiceTyping()}"
                if config.voiceTypingAutoComplete:
                    buffer.validate_and_handle()
                else:
                    buffer.cursor_position = buffer.cursor_position + buffer.document.get_end_of_line_position()
            else:
                run_in_terminal(lambda: print2("Install PyAudio first to enable voice entry!"))

        if hasattr(config, "currentMessages"):
            from freegenius.utils.prompt_shared_key_bindings import prompt_shared_key_bindings
            from freegenius.utils.prompt_multiline_shared_key_bindings import prompt_multiline_shared_key_bindings
            @this_key_bindings.add(*config.hotkey_launch_pager_view)
            def _(_):
                config.launchPager()
            # additional key binding
            conditional_prompt_multiline_shared_key_bindings = ConditionalKeyBindings(
                key_bindings=prompt_multiline_shared_key_bindings,
                filter=Condition(lambda: config.multilineInput),
            )
            this_key_bindings = merge_key_bindings([
                this_key_bindings,
                prompt_shared_key_bindings,
                conditional_prompt_multiline_shared_key_bindings,
            ])
        else:
            @this_key_bindings.add(*config.hotkey_new)
            def _(event):
                buffer = event.app.current_buffer
                config.defaultEntry = buffer.text
                buffer.text = ".new"
                buffer.validate_and_handle()

        config.selectAll = False
        inputPrompt = promptSession.prompt if promptSession is not None else prompt
        if not hasattr(config, "clipboard"):
            config.clipboard = PyperclipClipboard()
        if not inputIndicator:
            inputIndicator = [
                ("class:indicator", ">>> "),
            ]
        userInput = inputPrompt(
            inputIndicator,
            key_bindings=this_key_bindings,
            bottom_toolbar=bottom_toolbar if bottom_toolbar is not None else f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}""",
            #enable_system_prompt=True,
            swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")),
            style=style,
            validator=validator,
            multiline=Condition(lambda: hasattr(config, "currentMessages") and config.multilineInput),
            default=default,
            accept_default=accept_default,
            completer=completer,
            is_password=is_password,
            mouse_support=Condition(lambda: config.mouseSupport),
            clipboard=config.clipboard,
        )
        userInput = textwrap.dedent(userInput) # dedent to work with code block
        return userInput if hasattr(config, "addPathAt") and config.addPathAt else userInput.strip()

    @staticmethod
    def setPrint():
        if not hasattr(config, "print2"):
            config.print2 = print2
        if not hasattr(config, "print3"):
            config.print3 = print3

    @staticmethod
    def changeAPIkey():
        print("Enter your OpenAI API Key [optional]:")
        apikey = prompt(default=config.openaiApiKey, is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            config.openaiApiKey = apikey
        else:
            config.openaiApiKey = "freegenius"
        #HealthCheck.checkCompletion()

    @staticmethod
    def checkCompletion():
        os.environ["OPENAI_API_KEY"] = config.openaiApiKey

        if config.llmBackend == "llamacpp":
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
        elif config.llmBackend == "ollama":
            if shutil.which("ollama"):
                for i in (config.ollamaDefaultModel, config.ollamaCodeModel):
                    Downloader.downloadOllamaModel(i)
            else:
                print("Ollama not found! Install it first!")
                print("Check https://ollama.com")
                exit(0)
        elif config.llmBackend == "chatgpt":
            client = OpenAI()
            client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content" : "hello"}],
                n=1,
                max_tokens=10,
            )
        # set variable 'OAI_CONFIG_LIST' to work with pyautogen
        oai_config_list = []
        for model in HealthCheck.models:
            oai_config_list.append({"model": model, "api_key": config.openaiApiKey})
        os.environ["OAI_CONFIG_LIST"] = json.dumps(oai_config_list)

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
            return HealthCheck.count_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            #print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return HealthCheck.count_tokens_from_messages(messages, model="gpt-4-0613")
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