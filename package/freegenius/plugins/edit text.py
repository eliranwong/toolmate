"""
FreeGenius AI Plugin - edit text

edit text files

[FUNCTION_CALL]
"""

from freegenius import config, isCommandInstalled
import os, re, sys

# persistent
# users can customise 'textEditor' and 'textFileExtensions' in config.py
persistentConfigs = (
    #("textEditor", "micro -softwrap true -wordwrap true"), # read options at https://github.com/zyedidia/micro/blob/master/runtime/help/options.md
    ("textFileExtensions", ['txt', 'md', 'py']), # edit this option to support more or less extensions
)
config.setConfig(persistentConfigs)

if config.customTextEditor:
    textEditor = re.sub(" .*?$", "", config.customTextEditor)
    if not textEditor or not isCommandInstalled(textEditor):
        config.customTextEditor = ""

def edit_text(function_args):
    customTextEditor = config.customTextEditor if config.customTextEditor else f"{sys.executable} {os.path.join(config.freeGeniusAIFolder, 'eTextEdit.py')}"
    filename = function_args.get("filename") # required
    # in case folder name is mistaken
    if os.path.isdir(filename):
        os.system(f"""{config.open} {filename}""")
        return ""
    else:
        command = f"{customTextEditor} {filename}" if filename else customTextEditor
        config.stopSpinning()
        os.system(command)
        return ""

functionSignature = {
    "examples": [
        "edit text file",
    ],
    "name": "edit_text",
    "description": f'''Edit text files with extensions: '*.{"', '*.".join(config.textFileExtensions)}'.''',
    "parameters": {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Text file path given by user. Return an empty string if not given.",
            },
        },
        "required": ["filename"],
    },
}

config.addFunctionCall(signature=functionSignature, method=edit_text)