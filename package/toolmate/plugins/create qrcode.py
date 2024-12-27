"""
ToolMate AI Plugin - create qr code

Create qr code image

[TOOL_CALL]
"""

from toolmate import config
from toolmate import print3
import os, qrcode, shutil

def create_qrcode(function_args):
    url = function_args.get("url", "") # required
    if not url:
        url = function_args.get("text", "") # required
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)

    filepath = os.path.join(config.localStorage, "qrcode.png")
    img = qr.make_image(fill='black', back_color='white')
    img.save(filepath)
    
    if os.path.isfile(filepath):
        if shutil.which(config.open):
            try:
                os.system(f'''{config.open} "{filepath}"''')
            except:
                pass
        config.toolTextOutput = f"File saved: {filepath}"
        print3(config.toolTextOutput)
    return ""

functionSignature = {
    "examples": [
        "create QR code",
    ],
    "name": "create_qrcode",
    "description": f'''Create QR code''',
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The url that is to be converted into qr code. Return '' if not given.",
            },
            "text": {
                "type": "string",
                "description": "The text content that is to be converted into qr code. Return '' if not given.",
            },
        },
        "required": ["url", "text"],
    },
}

config.addToolCall(signature=functionSignature, method=create_qrcode)