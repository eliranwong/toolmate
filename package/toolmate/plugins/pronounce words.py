"""
ToolMate AI Plugin - pronunce words

pronunce words

[TOOL_CALL]
"""

try:
    from gtts import gTTS
except:
    from toolmate import installPipPackage, print1
    installPipPackage(f"--upgrade gTTS")

from toolmate import config
from toolmate.utils.tts_utils import TTSUtil


from gtts import gTTS

def pronunce_words(function_args):
    words = function_args.get("words") # required
    language = function_args.get("language") # required
    print1("Loading speech feature ...")
    TTSUtil.play(words, language)
    return ""

functionSignature = {
    "examples": [
        "pronounce",
        "speak in",
        "read aloud",
    ],
    "name": "pronunce_words",
    "description": "Pronounce words or sentences with text-to-speech utility",
    "parameters": {
        "type": "object",
        "properties": {
            "words": {
                "type": "string",
                "description": "Words to be pronounced",
            },
            "language": {
                "type": "string",
                "description": "Language of the words",
                "enum": config.ttsLanguages,
            },
        },
        "required": ["words", "language"],
    },
}

config.addFunctionCall(signature=functionSignature, method=pronunce_words)
config.inputSuggestions.append("pronunce ")
