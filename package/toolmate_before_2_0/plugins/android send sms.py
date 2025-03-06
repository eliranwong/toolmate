"""
ToolMate AI Plugin - send sms

send sms on Android

[TOOL_CALL]
"""

from toolmate import config

if config.isTermux:

    import subprocess

    def send_sms(function_args):
        phone_number = function_args.get("phone_number", "") # required
        message = function_args.get("message", "").replace('"', '\\"') # required
        cli = f'''termux-sms-send -n {phone_number} "{message}"'''
        subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return ""

    functionSignature = {
        "examples": [],
        "name": "send_sms",
        "description": f'''Send sms''',
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "The phone number of the selected person",
                },
                "message": {
                    "type": "string",
                    "description": "Generate SMS message",
                },
            },
            "required": ["phone_number", "message"],
        },
    }

    config.addToolCall(signature=functionSignature, method=send_sms)

    config.aliases["@read_sms "] = "@command termux-sms-list "
    config.builtinTools["read_sms"] = "read sms"
    config.inputSuggestions.append("@read_sms ")