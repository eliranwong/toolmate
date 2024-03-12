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

import traceback, json, pprint, wcwidth, textwrap, threading, time
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
from pathlib import Path
from PIL import Image
import speech_recognition as sr
# a dummy import line to resolve ALSA error display
import sounddevice


def check_openai_errors(func):
    def wrapper(*args, **kwargs):
        try: 
            return func(*args, **kwargs)
        except openai.APIError as e:
            print("Error: Issue on OpenAI side.")
            print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
        except openai.APIConnectionError as e:
            print("Error: Issue connecting to our services.")
            print("Solution: Check your network settings, proxy configuration, SSL certificates, or firewall rules.")
        except openai.APITimeoutError as e:
            print("Error: Request timed out.")
            print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
        except openai.AuthenticationError as e:
            print("Error: Your API key or token was invalid, expired, or revoked.")
            print("Solution: Check your API key or token and make sure it is correct and active. You may need to generate a new one from your account dashboard.")
            HealthCheck.changeAPIkey()
        except openai.BadRequestError as e:
            print("Error: Your request was malformed or missing some required parameters, such as a token or an input.")
            print("Solution: The error message should advise you on the specific error made. Check the [documentation](https://platform.openai.com/docs/api-reference/) for the specific API method you are calling and make sure you are sending valid and complete parameters. You may also need to check the encoding, format, or size of your request data.")
        except openai.ConflictError as e:
            print("Error: The resource was updated by another request.")
            print("Solution: Try to update the resource again and ensure no other requests are trying to update it.")
        except openai.InternalServerError as e:
            print("Error: Issue on OpenAI servers.")
            print("Solution: Retry your request after a brief wait and contact us if the issue persists. Check the [status page](https://status.openai.com).")
        except openai.NotFoundError as e:
            print("Error: Requested resource does not exist.")
            print("Solution: Ensure you are the correct resource identifier.")
        except openai.PermissionDeniedError as e:
            print("Error: You don't have access to the requested resource.")
            print("Solution: Ensure you are using the correct API key, organization ID, and resource ID.")
        except openai.RateLimitError as e:
            print("Error: You have hit your assigned rate limit.")
            print("Solution: Pace your requests. Read more in OpenAI [Rate limit guide](https://platform.openai.com/docs/guides/rate-limits).")
        except openai.UnprocessableEntityError as e:
            print("Error: Unable to process the request despite the format being correct.")
            print("Solution: Please try the request again.")
        except:
            print(traceback.format_exc())
    return wrapper

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
            config.letMeDoItAIFolder = packageFolder
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
                files = HealthCheck.getLocalStorage()
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
    def showErrors():
        trace = traceback.format_exc()
        print(trace if config.developer else "Error encountered!")
        return trace

    @staticmethod
    def spinning_animation(stop_event):
        while not stop_event.is_set():
            for symbol in "|/-\\":
                print(symbol, end="\r")
                time.sleep(0.1)
        #print("\r", end="")
        #print(" ", end="")

    @staticmethod
    def startSpinning():
        config.stop_event = threading.Event()
        config.spinner_thread = threading.Thread(target=HealthCheck.spinning_animation, args=(config.stop_event,))
        config.spinner_thread.start()

    @staticmethod
    def stopSpinning():
        try:
            config.stop_event.set()
            config.spinner_thread.join()
        except:
            pass

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
                    #run_in_terminal(lambda: config.print2("Listensing to your voice ..."))
                    if config.voiceTypingAdjustAmbientNoise:
                        r.adjust_for_ambient_noise(source)
                    audio = r.listen(source)
                if config.voiceTypingNotification:
                    TTSUtil.playAudioFilePygame(os.path.join(packageFolder, "audio", "notification2_mild.mp3"))
                #run_in_terminal(lambda: config.print2("Processing to your voice ..."))
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
                run_in_terminal(lambda: config.print2("Install PyAudio first to enable voice entry!"))

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
    def getStringWidth(text):
        width = 0
        for character in text:
            width += wcwidth.wcwidth(character)
        return width

    @staticmethod
    def getPygmentsStyle():
        theme = config.pygments_style if hasattr(config, "pygments_style") and config.pygments_style else "stata-dark" if not config.terminalResourceLinkColor.startswith("ansibright") else "stata-light"
        return style_from_pygments_cls(get_style_by_name(theme))

    @staticmethod
    def getLocalStorage():
        # config.letMeDoItName
        if not hasattr(config, "letMeDoItName") or not config.letMeDoItName:
            config.letMeDoItName = "FreeGenius AI"

        # option 1: config.storagedirectory; user custom folder
        if not hasattr(config, "storagedirectory") or (config.storagedirectory and not os.path.isdir(config.storagedirectory)):
            config.storagedirectory = ""
        if config.storagedirectory:
            return config.storagedirectory
        # option 2: defaultStorageDir; located in user home directory
        defaultStorageDir = os.path.join(os.path.expanduser('~'), config.letMeDoItName.split()[0].lower())
        try:
            Path(defaultStorageDir).mkdir(parents=True, exist_ok=True)
        except:
            pass
        if os.path.isdir(defaultStorageDir):
            return defaultStorageDir
        # option 3: directory "files" in app directory; to be deleted on every upgrade
        else:
            return os.path.join(packageFolder, "files")

    @staticmethod
    def setPrint():
        if not hasattr(config, "print2"):
            config.print2 = HealthCheck.print2
        if not hasattr(config, "print3"):
            config.print3 = HealthCheck.print3

    @staticmethod
    def print2(content):
        print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>{content}</{config.terminalPromptIndicatorColor2}>"))

    @staticmethod
    def print3(content):
        splittedContent = content.split(": ", 1)
        if len(splittedContent) == 2:
            key, value = splittedContent
            print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>{key}:</{config.terminalPromptIndicatorColor2}> {value}"))
        else:
            config.print2(splittedContent)

    @staticmethod
    def getEmbeddingFunction(embeddingModel=None):
        # import statement is placed here to make this file compatible on Android
        from chromadb.utils import embedding_functions
        embeddingModel = embeddingModel if embeddingModel is not None else config.embeddingModel
        if embeddingModel in ("text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002"):
            return embedding_functions.OpenAIEmbeddingFunction(api_key=config.openaiApiKey, model_name=embeddingModel)
        return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embeddingModel) # support custom Sentence Transformer Embedding models by modifying config.embeddingModel

    @staticmethod
    def changeAPIkey():
        print("Enter your OpenAI API Key [required]:")
        apikey = prompt(default=config.openaiApiKey, is_password=True)
        if apikey and not apikey.strip().lower() in (config.cancel_entry, config.exit_entry):
            config.openaiApiKey = apikey
        #HealthCheck.checkCompletion()

    @staticmethod
    @check_openai_errors
    def checkCompletion():
        # instantiate a client that can shared with plugins
        os.environ["OPENAI_API_KEY"] = config.openaiApiKey
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