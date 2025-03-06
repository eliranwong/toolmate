"""
ToolMate AI Plugin - analyze audio file

analyze audio file

[TOOL_CALL]
"""

from toolmate import config

if not config.isLite:

    from toolmate import print1
    import os, whisper, shutil

    # Function method
    def examine_audio_whisper(function_args):
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

        if audio_file and os.path.isfile(audio_file):

            if not shutil.which("ffmpeg"):
                print1("Install 'ffmpeg' first!")
                print1("Read https://github.com/openai/whisper/tree/main#setup")
                return ""
            # https://github.com/openai/whisper/tree/main#python-usage
            # platform: llamacpp or ollama
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
        ],
        "name": "examine_audio_whisper",
        "description": f'''Retrieve information from an audio with Whisper''',
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
                    "enum": ["English", "non-English"],
                },
            },
            "required": ["audio_filepath", "language"],
        },
    }

    # Integrate the signature and method into LetMeDoIt AI
    config.addToolCall(signature=functionSignature, method=examine_audio_whisper)