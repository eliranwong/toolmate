"""
LetMeDoIt AI Plugin - create qr code

Create qr code image

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.utils.shared_utils import SharedUtil
import os, json

def create_qrcode(function_args):
    code = function_args.get("code") # required
    information = SharedUtil.showAndExecutePythonCode(code)
    if information:
        filepath = json.loads(information)["information"]
        if os.path.isfile(filepath):
            config.print3(f"File saved at: {filepath}")
            try:
                os.system(f'''{config.open} "{filepath}"''')
            except:
                pass
    return ""

functionSignature = {
    "intent": [
        "create content",
    ],
    "examples": [
        "Create a QR code",
    ],
    "name": "create_qrcode",
    "description": f'''Create QR code''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code that integrates package qrcode to resolve my request. Always save the qr code image in png format and use 'print' function to print its full path only, without additional description or comment, in the last line of your code.",
            },
        },
        "required": ["code"],
    },
}

config.addFunctionCall(signature=functionSignature, method=create_qrcode)