"""
FreeGenius AI Plugin - analyze audio file

analyze audio file

[FUNCTION_CALL]
"""

from freegenius import config, showErrors
from freegenius import print1, print2, print3
from freegenius.utils.sttLanguages import googleSpeeckToTextLanguages
import os, whisper, io, shutil
import speech_recognition as sr
from pydub import AudioSegment

# Function method
def analyze_audio(function_args):
    from freegenius import config
    def check_file_format(file_path):
        # List of allowed file extensions
        allowed_extensions = ('.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm')
        # Getting the file extension
        _, file_extension = os.path.splitext(file_path)
        # Checking if the file extension is in the list of allowed extensions
        return True if file_extension.lower() in allowed_extensions else False

    audio_file = function_args.get("audio_filepath") # required
    language = function_args.get("language") # required

    if audio_file and os.path.isfile(audio_file):
        if config.llmBackend in ("chatgpt", "letmedoit"):
            if not check_file_format(audio_file):
                print3("This feature supports the following input file types only: '.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'!")
                return ""
            elif os.path.getsize(audio_file) / (1024*1024) > 25:
                print3("Audio files are currently limited to 25 MB!")
                return ""
            try:
                with open(audio_file, "rb") as audio_file:
                    transcript = config.oai_client.audio.transcriptions.create(
                        model="whisper-1", 
                        file=audio_file, 
                        response_format="text"
                    )
                transcript = f"The transcript of the audio is: {transcript}"
                if config.llmBackend == "letmedoit" and config.developer:
                    config.print2(config.divider)
                    config.print3(transcript)
                    config.print2(config.divider)
                    config.print2("Answer to your enquiry:")
                return transcript
            except:
                showErrors()

        elif config.llmBackend == "gemini":

            # create a speech recognition object
            r = sr.Recognizer()

            # convert mp3
            if audio_file.lower().endswith(".mp3"):
                sound = AudioSegment.from_mp3(audio_file)
                tempFile = os.path.join(config.freeGeniusAIFolder, "temp", os.path.basename(audio_file))
                sound.export(tempFile, format='wav')

            # open the audio file
            with sr.AudioFile(audio_file) as source:
                # listen for the data (load audio to memory)
                audio_data = r.record(source)

            # recognize (convert from speech to text)
            try:
                text = r.recognize_google(audio_data, language=language)
                transcript = f"The transcript of the audio is: {text}"
                return transcript
            except sr.UnknownValueError:
                print("Speech recognition could not understand the audio")
            except sr.RequestError as e:
                print("Could not request results from Google Web Speech API; {0}".format(e))

            return ""

        elif config.llmBackend == "gemini_alternative":
            #https://cloud.google.com/speech-to-text/docs/sync-recognize#speech-sync-recognize-python

            # not supported on Android; so import here
            from google.cloud import speech

            # convert mp3
            if audio_file.lower().endswith(".mp3"):
                sound = AudioSegment.from_mp3(audio_file)
                tempFile = os.path.join(config.freeGeniusAIFolder, "temp", os.path.basename(audio_file))
                sound.export(tempFile, format='wav')

            # Instantiates a client
            client = speech.SpeechClient.from_service_account_json(config.google_cloud_credentials)
            #client = speech.SpeechClient()

            # Loads the audio into memory
            with io.open(audio_file, 'rb') as audio_file:
                content = audio_file.read()

            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                #encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                #sample_rate_hertz=16000,
                language_code=language,
            )

            # Performs speech recognition on the audio file
            response = client.recognize(
                config=config,
                audio=audio,
            )

            # Print the transcription
            for result in response.results:
                transcript = f"The transcript of the audio is: {result.alternatives[0].transcript}"
                return transcript
            
            return ""

        else:
            if not shutil.which("ffmpeg"):
                print1("Install 'ffmpeg' first!")
                print1("Read https://github.com/openai/whisper/tree/main#setup")
                return ""
            # https://github.com/openai/whisper/tree/main#python-usage
            # backend: llamacpp or ollama
            if language.lower() in ("english", "non-english"):
                model = whisper.load_model(config.voiceTypingWhisperEnglishModel if language.lower() == "english" else "large")
                result = model.transcribe(audio_file)
            else:
                # non-English
                model = whisper.load_model("large")

                # load audio and pad/trim it to fit 30 seconds
                audio = whisper.load_audio(audio_file)
                audio = whisper.pad_or_trim(audio)

                # make log-Mel spectrogram and move to the same device as the model
                mel = whisper.log_mel_spectrogram(audio).to(model.device)

                # detect the spoken language
                _, probs = model.detect_language(mel)
                print(f"Detected language: {max(probs, key=probs.get)}")

                # decode the audio
                options = whisper.DecodingOptions()
                result = whisper.decode(model, mel, options)

            transcript = f"The transcript of the audio is: {result['text']}"
            return transcript


    return "[INVALID]"

# Function Signature
functionSignature = {
    "examples": [
        "analyze speech",
        "audio transcript",
        "transcibe audio",
    ],
    "name": "analyze_audio",
    "description": f'''Transcribe audio into text or retrieve information from an audio''',
    "parameters": {
        "type": "object",
        "properties": {
            "audio_filepath": {
                "type": "string",
                "description": "Return the audio file path that I specified in my requests. Return an empty string '' if it is not specified.",
            },
            "language": {
                "type": "string",
                "description": "Audio language",
                "enum": list(googleSpeeckToTextLanguages.values()) if config.llmBackend == "gemini" else ["English", "non-English"],
            },
        },
        "required": ["audio_filepath", "language"],
    },
}

# Integrate the signature and method into LetMeDoIt AI
config.addFunctionCall(signature=functionSignature, method=analyze_audio)