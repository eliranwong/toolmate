"""
ToolMate AI Plugin - analyze audio file with Groq

analyze audio file with Groq

[TOOL_CALL]
"""

from toolmate import config

if config.online:

    from toolmate import showErrors, getGroqClient
    from toolmate import print1, print2, print3
    import os, shutil, subprocess

    # Function method
    def transcribe_audio_groq(function_args):
        from toolmate import config
        def check_file_format(file_path):
            # List of allowed file extensions
            allowed_extensions = ('.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm')
            # Getting the file extension
            _, file_extension = os.path.splitext(file_path)
            # Checking if the file extension is in the list of allowed extensions
            return True if file_extension.lower() in allowed_extensions else False

        audio_file = function_args.get("audio_filepath") # required

        if audio_file and os.path.isfile(audio_file):
            if shutil.which("ffmpeg"):
                temp_audio_file = os.path.join(config.toolMateAIFolder, "temp", os.path.basename(audio_file))
                if os.path.isfile(temp_audio_file):
                    os.remove(temp_audio_file)
                cli = f'''ffmpeg -i "{audio_file}" -ar 16000 -ac 1 -map 0:a: "{temp_audio_file}"'''
                run_cli = subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                *_, stderr = run_cli.communicate()
                if not stderr:
                    audio_file = temp_audio_file
            if not check_file_format(audio_file):
                print3("This feature supports the following input file types only: '.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'!")
                return ""
            elif os.path.getsize(audio_file) / (1024*1024) > 25:
                print3("Audio files are currently limited to 25 MB!")
                return ""
            try:
                # read https://console.groq.com/docs/speech-text
                with open(audio_file, "rb") as file:
                    transcription = getGroqClient().audio.transcriptions.create(
                        file=(audio_file, file.read()),
                        model="whisper-large-v3",
                        #prompt="Specify context or spelling",  # Optional
                        #response_format="json",  # Optional
                        #language="en",  # Optional
                        temperature=0.0  # Optional
                    )
                    config.toolTextOutput = transcription.text
                    print2("```transcript")
                    print1(config.toolTextOutput)
                    print2("```")
            except:
                showErrors()
            return ""

        return "[INVALID]"

    # Function Signature
    functionSignature = {
        "examples": [
            "Transcribe audio",
        ],
        "name": "transcribe_audio_groq",
        "description": f'''Transcribe audio into text with Groq''',
        "parameters": {
            "type": "object",
            "properties": {
                "audio_filepath": {
                    "type": "string",
                    "description": "Return the audio file path that I specified in my requests. Return an empty string '' if it is not specified.",
                },
            },
            "required": ["audio_filepath"],
        },
    }

    # Integrate the signature and method into LetMeDoIt AI
    config.addToolCall(signature=functionSignature, method=transcribe_audio_groq)
