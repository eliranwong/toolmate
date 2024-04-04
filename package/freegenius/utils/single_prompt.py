import os, textwrap
from freegenius import config
from freegenius import print2, print3

from prompt_toolkit import prompt
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings, ConditionalKeyBindings
from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard
from prompt_toolkit.application import run_in_terminal
from freegenius.utils.tts_utils import TTSUtil
import speech_recognition as sr
# a dummy import line to resolve ALSA error display
import sounddevice


class SinglePrompt:

    @staticmethod
    def run(inputIndicator="", validator=None, default="", accept_default=False, completer=None, promptSession=None, style=None, is_password=False, bottom_toolbar=None, **kwargs):
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
            run_in_terminal(lambda: print3(f"Word Wrap: '{'enabled' if config.wrapWords else 'disabled'}'!"))
        @this_key_bindings.add(*config.hotkey_toggle_response_audio)
        def _(_):
            if config.tts:
                config.ttsOutput = not config.ttsOutput
                config.saveConfig()
                run_in_terminal(lambda: print3(f"Response Audio: '{'enabled' if config.ttsOutput else 'disabled'}'!"))
        @this_key_bindings.add(*config.hotkey_voice_entry)
        def _(event):
            # reference: https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py
            def voiceTyping():
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    if config.voiceTypingNotification:
                        TTSUtil.playAudioFilePygame(os.path.join(config.freeGeniusAIFolder, "audio", "notification1_mild.mp3"))
                    #run_in_terminal(lambda: print2("Listensing to your voice ..."))
                    if config.voiceTypingAdjustAmbientNoise:
                        r.adjust_for_ambient_noise(source)
                    audio = r.listen(source)
                if config.voiceTypingNotification:
                    TTSUtil.playAudioFilePygame(os.path.join(config.freeGeniusAIFolder, "audio", "notification2_mild.mp3"))
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
            **kwargs,
        )
        userInput = textwrap.dedent(userInput) # dedent to work with code block
        return userInput if hasattr(config, "addPathAt") and config.addPathAt else userInput.strip()
