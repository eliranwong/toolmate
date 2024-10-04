"""
ToolMate AI Plugin - send whatsapp messages

send whatsapp messages

[TOOL_CALL]
"""

if not config.isTermux:

    from toolmate import config
    import re, pywhatkit

    def send_whatsapp(function_args):
        recipient = function_args.get("recipient") # required
        message = function_args.get("message") # required
        config.stopSpinning()
        if re.search("^[\+\(\)0-9]+?$", recipient):
            pywhatkit.sendwhatmsg_instantly(recipient, message)
        else:
            pywhatkit.sendwhatmsg_to_group_instantly(recipient, message)
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
                "recipient": {
                    "type": "string",
                    "description": "Recipient's phone number or group name. Phone number is preferred. Figure out the group name only if phone number is not provided.",
                },
                "message": {
                    "type": "string",
                    "description": "The message that is to be sent to the recipient",
                },
            },
            "required": ["recipient", "message"],
        },
    }

    config.addFunctionCall(signature=functionSignature, method=send_whatsapp)