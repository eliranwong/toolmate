"""
ToolMate AI Plugin - send whatsapp messages

send whatsapp messages on Android

[TOOL_CALL]
"""

from toolmate import config

if config.isTermux and config.online:

    import subprocess

    def send_whatsapp(function_args):
        message = function_args.get("message").replace('"', '\\"') # required
        config.stopSpinning()
        # e.g. am start -a android.intent.action.VIEW -d "https://api.whatsapp.com/send?phone=+441234567&text=Hello"
        # https://api.whatsapp.com/send?phone=+18772241042
        cli = f'''am start -a android.intent.action.VIEW -d "https://api.whatsapp.com/send?text={message}"'''
        subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return ""

    functionSignature = {
        "examples": [
            "send WhatsApp",
        ],
        "name": "send_whatsapp",
        "description": f'''Send WhatsApp messages''',
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message that is to be sent to the recipient",
                },
            },
            "required": ["message"],
        },
    }

    config.addToolCall(signature=functionSignature, method=send_whatsapp)

    def ask_copilot(function_args):
        message = function_args.get("message").replace('"', '\\"') # required
        config.stopSpinning()
        # e.g. am start -a android.intent.action.VIEW -d "https://api.whatsapp.com/send?phone=+441234567&text=Hello"
        # Microsoft Copilot Business Account: +18772241042
        cli = f'''am start -a android.intent.action.VIEW -d "https://api.whatsapp.com/send?phone=+18772241042&text={message}"'''
        subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return ""

    functionSignature = {
        "examples": [
            "Ask CoPilot",
        ],
        "name": "ask_copilot",
        "description": f'''Whatsapp Microsoft CoPilot''',
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message that is to be sent to Microsoft CoPilot",
                },
            },
            "required": ["message"],
        },
    }

    config.addToolCall(signature=functionSignature, method=ask_copilot)