from freegenius import config
import os, traceback, subprocess, re, sounddevice, soundfile
from gtts import gTTS
from elevenlabs import generate, play
from freegenius.utils.vlc_utils import VlcUtil
try:
    from google.cloud import texttospeech
except:
    pass
try:
    # hide pygame welcome message
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    import pygame
    if pygame.mixer.get_init() is None:
        pygame.mixer.init()
    config.isPygameInstalled = True
except:
    config.usePygame = False
    config.isPygameInstalled = True

class TTSUtil:

    @staticmethod
    def play(content, language=""):
        if config.tts:
            try:
                # official google-cloud-texttospeech
                if config.ttsPlatform == "googlecloud" and os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Text-to-Speech" in config.enabledGoogleAPIs:
                    audioFile = os.path.join(config.letMeDoItAIFolder, "temp", "gctts.mp3")
                    if not language:
                        language = config.gcttsLang
                    elif language == "yue":
                        language = "yue-HK"
                    elif "-" in language:
                        language, accent = language.split("-", 1)
                        language = f"{language}-{accent.upper()}"
                    TTSUtil.saveCloudTTSAudio(content, language, filename=audioFile)
                    TTSUtil.playAudioFile(audioFile)
                elif config.ttsPlatform == "custom" and config.ttsCommand:
                    # remove '"' from the content
                    content = re.sub('"', "", content)

                    # Windows users
                    # https://stackoverflow.com/questions/1040655/ms-speech-from-command-lines
                    # https://www.powerofpowershell.com/post/powershell-can-speak-too#:~:text=The%20Add%2DType%20cmdlet%20is,want%20to%20convert%20into%20speech.
                    windows = (config.ttsCommand.lower() == "windows")
                    if windows:
                        content = re.sub("'", "", content)
                    if language and language in config.ttsLanguagesCommandMap and config.ttsLanguagesCommandMap[language]:
                        voice = config.ttsLanguagesCommandMap[language]
                        if windows:
                            command = f'''PowerShell -Command "Add-Type –AssemblyName System.Speech; $ttsEngine = New-Object System.Speech.Synthesis.SpeechSynthesizer; $ttsEngine.SelectVoice('{voice} Desktop'); $ttsEngine.Speak('{content}');"'''
                        else:
                            ttsCommand = re.sub("^(.*?) [^ ]+?$", r"\1", config.ttsCommand.strip()) + " " + voice
                            command = f'''{ttsCommand} "{content}"{config.ttsCommandSuffix}'''
                    else:
                        if windows:
                            command = f'''PowerShell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{content}');"'''
                        else:
                            command = f'''{config.ttsCommand} "{content}"{config.ttsCommandSuffix}'''
                    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                elif config.ttsPlatform == "elevenlabs" and config.elevenlabsApi:
                    audio = generate(
                        api_key=config.elevenlabsApi, # Defaults to os.getenv(ELEVEN_API_KEY)
                        text=content,
                        voice="Rachel",
                        model="eleven_multilingual_v2"
                    )
                    play(audio)
                else:
                    if not config.ttsPlatform == "google":
                        config.ttsPlatform == "google"
                        config.saveConfig()
                    # use gTTS as default as config.ttsCommand is empty by default
                    if not language:
                        language = config.gttsLang
                    elif language == "yue":
                        language = "zh"
                    elif "-" in language:
                        language = re.sub("^(.*?)\-.*?$", r"\1", language)
                    audioFile = os.path.join(config.letMeDoItAIFolder, "temp", "gtts.mp3")
                    tts = gTTS(content, lang=language, tld=config.gttsTld) if config.gttsTld else gTTS(content, lang=language)
                    tts.save(audioFile)
                    TTSUtil.playAudioFile(audioFile)
            except:
                if config.developer:
                    print(traceback.format_exc())
                else:
                    pass

    @staticmethod
    def playAudioFile(audioFile):
        try:
            if config.isVlcPlayerInstalled and not config.usePygame:
                # vlc is preferred as it allows speed control with config.vlcSpeed
                VlcUtil.playMediaFile(audioFile)
            elif config.isPygameInstalled:
                # use pygame if config.usePygame or vlc player is not installed
                TTSUtil.playAudioFilePygame(audioFile)
            else:
                sounddevice.play(*soundfile.read(audioFile)) 
                sounddevice.wait()
        except:
            command = f"{config.open} {audioFile}"
            subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    @staticmethod
    def playAudioFilePygame(audioFile):
        pygame.mixer.music.load(audioFile)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Check every 10 milliseconds
        pygame.mixer.music.stop()

    # Temporary filepath for tts export
    @staticmethod
    def getGttsFilename():
        folder = os.path.join(config.letMeDoItAIFolder, "temp")
        if not os.path.isdir(folder):
            os.makedirs(folder, exist_ok=True)
        return os.path.abspath(os.path.join(folder, "gtts.mp3"))

    # Official Google Cloud Text-to-speech Service
    @staticmethod
    def saveCloudTTSAudio(inputText, languageCode="", filename=""):
        if not languageCode:
            languageCode = config.gcttsLang
        # Modified from source: https://cloud.google.com/text-to-speech/docs/create-audio-text-client-libraries#client-libraries-install-python
        """Synthesizes speech from the input string of text or ssml.
        Make sure to be working in a virtual environment.

        Note: ssml must be well-formed according to:
            https://www.w3.org/TR/speech-synthesis/
        """
        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=inputText)

        # Build the voice request, select the language code (e.g. "yue-HK") and the ssml
        # voice gender ("neutral")
        # Supported language: https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
        # Voice: https://cloud.google.com/text-to-speech/docs/voices
        # Gener: https://cloud.google.com/text-to-speech/docs/reference/rest/v1/SsmlVoiceGender
        voice = texttospeech.VoiceSelectionParams(
            language_code=languageCode, ssml_gender=texttospeech.SsmlVoiceGender.SSML_VOICE_GENDER_UNSPECIFIED
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            # For more config, read https://cloud.google.com/text-to-speech/docs/reference/rest/v1/text/synthesize#audioconfig
            speaking_rate=config.gcttsSpeed,
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        # Save into mp3
        if not filename:
            filename = os.path.abspath(TTSUtil.getGttsFilename())
        if os.path.isfile(filename):
            os.remove(filename)
        with open(filename, "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            #print('Audio content written to file "{0}"'.format(outputFile))
