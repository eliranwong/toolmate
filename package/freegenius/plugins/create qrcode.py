"""
LetMeDoIt AI Plugin - create qr code

Create qr code image

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.utils.shared_utils import SharedUtil
import os, qrcode

def create_qrcode(function_args):
    url = function_args.get("content") # required
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)

    filepath = os.path.join(SharedUtil.getLocalStorage(), "qrcode.png")
    img = qr.make_image(fill='black', back_color='white')
    img.save(filepath)
    
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
            "content": {
                "type": "string",
                "description": "The url or text content that is to be converted into qr code.",
            },
        },
        "required": ["content"],
    },
}

config.addFunctionCall(signature=functionSignature, method=create_qrcode)