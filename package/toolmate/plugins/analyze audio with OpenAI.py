"""
ToolMate AI Plugin - analyze audio file

analyze audio file

[TOOL_CALL]
"""

if not config.isTermux:

    from toolmate import config, showErrors, getGroqClient
    from toolmate import print1, print2, print3
    from toolmate.utils.sttLanguages import googleSpeeckToTextLanguages
    import os, whisper, io, shutil, subprocess
    import speech_recognition as sr
    from pydub import AudioSegment

    # Function method
    def analyze_audio_openai(function_args):
        from toolmate import config
        def check_file_format(file_path):
            # List of allowed file extensions
            allowed_extensions = ('.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm')
            # Getting the file extension
            _, file_extension = os.path.splitext(file_path)
            # Checking if the file extension is in the list of allowed extensions
            return True if file_extension.lower() in allowed_extensions else False

        audio_file = function_args.get("audio_filepath") # required
        #language = function_args.get("language") # required

        if audio_file and os.path.isfile(audio_file):
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
                if config.developer:
                    print2(config.divider)
                    print3(transcript)
                    print2(config.divider)
                    print2("Answer to your enquiry:")
                return transcript
            except:
                showErrors()
            return ""

        return "[INVALID]"

    # Function Signature
    functionSignature = {
        "examples": [
            "analyze speech",
        ],
        "name": "analyze_audio_openai",
        "description": f'''Retrieve information from an audio with OpenAI''',
        "parameters": {
            "type": "object",
            "properties": {
                "audio_filepath": {
                    "type": "string",
                    "description": "Return the audio file path that I specified in my requests. Return an empty string '' if it is not specified.",
                },
            },
            "required": ["audio_filepath", "language"],
        },
    }

    # Integrate the signature and method into LetMeDoIt AI
    config.addFunctionCall(signature=functionSignature, method=analyze_audio_openai)