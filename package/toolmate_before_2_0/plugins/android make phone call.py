"""
ToolMate AI Plugin - make phone call

make a phone call on Android

[TOOL_CALL]
"""

from toolmate import config

if config.isTermux:

    import subprocess

    def phone_call(function_args):
        phone_number = function_args.get("phone_number", "") # required
        cli = f'''termux-telephony-call {phone_number}'''
        subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return ""

    functionSignature = {
        "examples": [],
        "name": "phone_call",
        "description": f'''Make a phone call''',
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "The phone number of the selected person",
                },
            },
            "required": ["phone_number"],
        },
    }

    config.addToolCall(signature=functionSignature, method=phone_call)