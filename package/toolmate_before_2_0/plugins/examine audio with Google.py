"""
ToolMate AI Plugin - analyze audio file

analyze audio file

[TOOL_CALL]
"""

from toolmate import config

if not config.isLite and config.online:

    from toolmate.utils.sttLanguages import googleSpeeckToTextLanguages
    import os, io
    import speech_recognition as sr
    from pydub import AudioSegment

    # Function method
    def examine_audio_google(function_args):
        from toolmate import config
        def check_file_format(file_path):
            # List of allowed file extensions
            allowed_extensions = ('.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm')
            # Getting the file extension
            _, file_extension = os.path.splitext(file_path)
            # Checking if the file extension is in the list of allowed extensions
            return True if file_extension.lower() in allowed_extensions else False

        audio_file = function_args.get("audio_filepath") # required
        language = function_args.get("language") # required

        llmInterface = "vertexai"

        if audio_file and os.path.isfile(audio_file):
            if llmInterface in ("vertexai", "genai"):

                # create a speech recognition object
                r = sr.Recognizer()

                # convert mp3
                if audio_file.lower().endswith(".mp3"):
                    sound = AudioSegment.from_mp3(audio_file)
                    audio_file = os.path.join(config.toolMateAIFolder, "temp", os.path.basename(audio_file))
                    sound.export(audio_file, format='wav')

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

            elif llmInterface == "gemini_alternative":
                #https://cloud.google.com/speech-to-text/docs/sync-recognize#speech-sync-recognize-python

                # not supported on Android; so import here
                from google.cloud import speech

                # convert mp3
                if audio_file.lower().endswith(".mp3"):
                    sound = AudioSegment.from_mp3(audio_file)
                    audio_file = os.path.join(config.toolMateAIFolder, "temp", os.path.basename(audio_file))
                    sound.export(audio_file, format='wav')

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

        return "[INVALID]"

    # Function Signature
    functionSignature = {
        "examples": [
            "analyze speech",
        ],
        "name": "examine_audio_google",
        "description": f'''Retrieve information from an audio with Google''',
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
                    "enum": list(googleSpeeckToTextLanguages.values()),
                },
            },
            "required": ["audio_filepath", "language"],
        },
    }

    # Integrate the signature and method into LetMeDoIt AI
    config.addToolCall(signature=functionSignature, method=examine_audio_google)