"""
ToolMate AI Plugin 

- convert simplified Chinese into traditional Chinese
- convert traditional Chinese into simplified Chinese
"""

try:
    from opencc import OpenCC
except:
    from toolmate import installPipPackage
    installPipPackage(f"--upgrade opencc-python-reimplemented")

from toolmate import config
from opencc import OpenCC


def convert_simplified_chinese(_):
    originalText = config.currentMessages[-1]["content"]
    try:
        config.toolTextOutput = OpenCC('s2t').convert(originalText)
    except:
        config.toolTextOutput = originalText
    return ""

functionSignature = {
    "examples": [],
    "name": "convert_simplified_chinese",
    "description": "Convert simplified Chinese into traditional Chinese in text output",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

config.addToolCall(signature=functionSignature, method=convert_simplified_chinese)

def convert_traditional_chinese(_):
    originalText = config.currentMessages[-1]["content"]
    try:
        config.toolTextOutput = OpenCC('t2s').convert(originalText)
    except:
        config.toolTextOutput = originalText
    return ""

functionSignature = {
    "examples": [],
    "name": "convert_traditional_chinese",
    "description": "Convert traditional Chinese into simplified Chinese in text output",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

config.addToolCall(signature=functionSignature, method=convert_traditional_chinese)