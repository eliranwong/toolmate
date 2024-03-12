"""
LetMeDoIt AI Plugin - manipulate files

Manipulate files, such as navigation, rename, removal, conversion, etc.

This plugin is created to avoid conflicts with plugin "analyze files"

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.utils.shared_utils import SharedUtil
import re, os

def manipulate_files(function_args):
    code = function_args.get("code") # required
    return SharedUtil.showAndExecutePythonCode(code)

functionSignature = {
    "intent": [
        "change files",
    ],
    "examples": [
        "Edit test.txt",
    ],
    "name": "manipulate_files",
    "description": f'''Manipulate files, such as opening, launching, navigation, renaming, editing, removal, conversion, etc.''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code that integrates any relevant packages to resolve my request",
            },
        },
        "required": ["code"],
    },
}

config.addFunctionCall(signature=functionSignature, method=manipulate_files)