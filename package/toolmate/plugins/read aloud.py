"""
ToolMate AI Plugin - read aloud

pronunce words

[TOOL_CALL]
"""

from toolmate import config, print1
from toolmate.utils.tts_utils import TTSUtil

def read_aloud(function_args):
    words = function_args.get("words") # required
    #language = function_args.get("language") # required
    print1("Loading speech feature ...")
    #TTSUtil.play(words, language)
    TTSUtil.play(words)
    return ""

functionSignature = {
    "examples": [
        "pronounce",
        "read aloud",
    ],
    "name": "read_aloud",
    "description": "Pronounce words or sentences with text-to-speech utility",
    "parameters": {
        "type": "object",
        "properties": {
            "words": {
                "type": "string",
                "description": "Words to be pronounced",
            },
        },
        "required": ["words"],
    },
}

config.addFunctionCall(signature=functionSignature, method=read_aloud)
config.inputSuggestions.append("pronunce ")
