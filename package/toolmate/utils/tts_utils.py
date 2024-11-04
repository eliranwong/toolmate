from toolmate import config, getHideOutputSuffix, getElevenlabsApi_key
import os, traceback, subprocess, re, pydoc, shutil, edge_tts, asyncio
from pathlib import Path
from gtts import gTTS
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from toolmate.utils.vlc_utils import VlcUtil
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
if not config.isTermux:
    import sounddevice, soundfile


class TTSUtil:

    @staticmethod
    def play(content, language=""):
        if config.tts and content.strip():
            try:
                if config.ttsPlatform == "android":
                    content = content.replace('"', '\\"')
                    os.system(f'''termux-tts-speak -l {config.gcttsLang} -r {config.androidttsRate} "{content}"''')
                elif config.ttsPlatform == "googlecloud" and os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Text-to-Speech" in config.enabledGoogleAPIs:
                    # official google-cloud-texttospeech
                    audioFile = os.path.join(config.toolMateAIFolder, "temp", "gctts.mp3")
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
                    audio = ElevenLabs(api_key=getElevenlabsApi_key()).generate(
                        #api_key=config.elevenlabsApi, # Defaults to os.getenv(ELEVEN_API_KEY)
                        text=content,
                        voice=config.elevenlabsVoice,
                        model="eleven_multilingual_v2"
                    )
                    play(audio) # elevanlabs play function
                elif config.ttsPlatform == "say":
                    additional_options = f" {config.say_additional_options.strip()}" if config.say_additional_options.strip() else ""
                    voice = f" -v {config.say_voice.strip()}" if config.say_voice.strip() else ""
                    cmd = f"say -r {config.say_speed}{voice}{additional_options}"
                    pydoc.pipepager(content, cmd=cmd)
                elif config.ttsPlatform == "wsay":
                    additional_options = f" {config.wsay_additional_options.strip()}" if config.wsay_additional_options.strip() else ""
                    homeWsay = os.path.join(config.localStorage, "wsay.exe")
                    cmd = f'''"{homeWsay if os.path.isfile(homeWsay) else 'wsay'}" --voice {config.wsay_voice} --speed {config.wsay_speed}{additional_options}'''
                    pydoc.pipepager(content, cmd=cmd)
                elif config.ttsPlatform == "piper":
                    audioFile = os.path.join(config.toolMateAIFolder, "temp", "piper.wav")
                    model_dir = os.path.join(config.localStorage, "LLMs", "piper")
                    model_path = f"""{os.path.join(model_dir, config.piper_voice)}.onnx"""
                    model_config_path = f"""{model_path}.json"""
                    piper_additional_options = f" {config.piper_additional_options.strip()}" if config.piper_additional_options.strip() else ""
                    if os.path.isfile(model_path):
                        if shutil.which("cvlc"):
                            cmd = f'''"{shutil.which("piper")}" --model "{model_path}" --config "{model_config_path}" --output-raw | cvlc --play-and-exit --rate {config.vlcSpeed} --demux=rawaud --rawaud-channels=1 --rawaud-samplerate=22050{piper_additional_options} -{getHideOutputSuffix()}'''
                        elif shutil.which("aplay"):
                            cmd = f'''"{shutil.which("piper")}" --model "{model_path}" --config "{model_config_path}" --output-raw | aplay -r 22050 -f S16_LE -t raw{piper_additional_options} -{getHideOutputSuffix()}'''
                        else:
                            cmd = f'''"{shutil.which("piper")}" --model "{model_path}" --config "{model_config_path}" --output_file "{audioFile}"{piper_additional_options}{getHideOutputSuffix()}'''
                    else:
                        print("[Downloading voice ...] ")
                        if shutil.which("cvlc"):
                            cmd = f'''"{shutil.which("piper")}" --model {config.piper_voice} --download-dir "{model_dir}" --data-dir "{model_dir}" --output-raw | cvlc --play-and-exit --rate {config.vlcSpeed} --demux=rawaud --rawaud-channels=1 --rawaud-samplerate=22050{piper_additional_options} -{getHideOutputSuffix()}'''
                        elif shutil.which("aplay"):
                            cmd = f'''"{shutil.which("piper")}" --model {config.piper_voice} --download-dir "{model_dir}" --data-dir "{model_dir}" --output-raw | aplay -r 22050 -f S16_LE -t raw{piper_additional_options} -{getHideOutputSuffix()}'''
                        else:
                            cmd = f'''"{shutil.which("piper")}" --model {config.piper_voice} --download-dir "{model_dir}" --data-dir "{model_dir}" --output_file "{audioFile}"{piper_additional_options}{getHideOutputSuffix()}'''
                    pydoc.pipepager(content, cmd=cmd)
                    if not shutil.which("cvlc") and not shutil.which("aplay"):
                        TTSUtil.playAudioFile(audioFile)
                elif config.ttsPlatform == "edge":
                    audioFile = os.path.join(config.toolMateAIFolder, "temp", "edge.wav")
                    async def saveEdgeAudio() -> None:
                        rate = (config.edgettsRate - 1.0) * 100
                        rate = int(round(rate, 0))
                        communicate = edge_tts.Communicate(content, config.edgettsVoice, rate=f"{'+' if rate >= 0 else ''}{rate}%")
                        await communicate.save(audioFile)
                    asyncio.run(saveEdgeAudio())
                    if shutil.which("mpv"):
                        os.system(f'''mpv --really-quiet "{audioFile}"''')
                    else:
                        TTSUtil.playAudioFile(audioFile, vlcSpeed=0.0)
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
                        language = re.sub("^(.*?)-.*?$", r"\1", language)
                    audioFile = os.path.join(config.toolMateAIFolder, "temp", "gtts.mp3")
                    tts = gTTS(content, lang=language, tld=config.gttsTld) if config.gttsTld else gTTS(content, lang=language)
                    tts.save(audioFile)
                    TTSUtil.playAudioFile(audioFile)
            except:
                if config.developer:
                    print(traceback.format_exc())
                else:
                    pass

    @staticmethod
    def playAudioFile(audioFile, vlcSpeed=None):
        try:
            if config.isVlcPlayerInstalled and not config.usePygame:
                # vlc is preferred as it allows speed control with config.vlcSpeed
                VlcUtil.playMediaFile(audioFile, vlcSpeed=vlcSpeed)
            elif config.isPygameInstalled:
                # use pygame if config.usePygame or vlc player is not installed
                TTSUtil.playAudioFilePygame(audioFile)
            elif config.isTermux and config.terminalEnableTermuxAPI:
                os.system(f'''termux-media-player play "{audioFile}"''')
            elif shutil.which("mpv"):
                os.system(f'''mpv --really-quiet "{audioFile}"''')
            else:
                sounddevice.play(*soundfile.read(audioFile)) 
                sounddevice.wait()
        except:
            if shutil.which(config.open):
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
        folder = os.path.join(config.toolMateAIFolder, "temp")
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
