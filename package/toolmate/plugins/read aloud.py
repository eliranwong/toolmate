"""
ToolMate AI Plugin - read aloud

pronunce words

[TOOL_CALL]
"""

from toolmate import config, print1
from toolmate.utils.tts_utils import TTSUtil
import re

def read_aloud(function_args):
    content = config.currentMessages[-1]["content"]
    content = re.sub("^[Rr]ead aloud[:]*", "", content).strip()
    #words = function_args.get("words") # required
    #language = function_args.get("language") # required
    print1("Loading speech feature ...")
    #TTSUtil.play(words, language)
    TTSUtil.play(content)
    return ""

functionSignature = {
    "examples": [
        "read aloud",
    ],
    "name": "read_aloud",
    "description": "Pronounce words or sentences with text-to-speech utility",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

config.addFunctionCall(signature=functionSignature, method=read_aloud)
config.inputSuggestions.append("Read aloud: ")
