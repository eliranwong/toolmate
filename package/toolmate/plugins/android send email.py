"""
ToolMate AI Plugin - send email

send email on Android

[TOOL_CALL]
"""

if config.isTermux:

    from toolmate import config, stopSpinning
    import urllib.parse
    import subprocess

    def send_email(function_args):
        recipient = function_args.get("email", "") # required
        subject = function_args.get("subject", "").replace('"', '\\"') # required
        body = function_args.get("body", "").replace('"', '\\"') # required

        subject = urllib.parse.quote(subject)
        body = urllib.parse.quote(body)

        stopSpinning()

        # e.g. am start -a android.intent.action.SENDTO -d "mailto:john.doe@example.com?subject=Hello&body=How%20are%20you?"
        cli = f'''am start -a android.intent.action.SENDTO -d "mailto:{recipient}?subject={subject}&body={body}"'''
        subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return ""

    functionSignature = {
        "examples": [
            "send an email",
        ],
        "name": "send_email",
        "description": "Send email",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "The recipient email address",
                },
                "subject": {
                    "type": "string",
                    "description": "Give a title to the email.",
                },
                "body": {
                    "type": "string",
                    "description": "The body or content of the email.",
                },
            },
            "required": ["email", "subject", "body"],
        },
    }

    config.addFunctionCall(signature=functionSignature, method=send_email)