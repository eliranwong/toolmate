"""
ToolMate AI Plugin - send emails

send google or outlook emails

[TOOL_CALL]
"""

"""
# Information

To send an email using a single URL via Google Mail, you can use the following format:

https://mail.google.com/mail/?view=cm&fs=1&to=Recipient&subject=Subject&body=Body

You need to replace the parameters with the values you want, such as:

Recipient: The email address of the person you want to send the email to (URL encoded format).
Subject: The subject line of the email (URL encoded format).
Body: The content of the email (URL encoded format).
For example, if you want to send an email with the following details:

Recipient: john.doe@example.com
Subject: Hello
Body: How are you?
You can use this URL:

https://mail.google.com/mail/?view=cm&fs=1&to=john.doe%40example.com&su=Hello&body=How%20are%20you%3F

When you click on this URL, it will open a new window in Google Mail and fill in the email details for you. You can then send or edit the email as you wish.
"""

"""
To send an email using a single URL via Microsoft Outlook web version, you can use the following format:

https://outlook.office.com/owa/?path=/mail/action/compose
&to=Recipient
&su=Subject
&body=Body

You need to replace the parameters with the values you want, such as:

Recipient: The email address of the person you want to send the email to (URL encoded format).
Subject: The subject line of the email (URL encoded format).
Body: The content of the email (URL encoded format).
For example, if you want to send an email with the following details:

Recipient: john.doe@example.com
Subject: Hello
Body: How are you?
You can use this URL:

https://outlook.office.com/owa/?path=/mail/action/compose&to=john.doe%40example.com&subject=Hello&body=How%20are%20you%3F

When you click on this URL, it will open a new window in Outlook web app and fill in the email details for you. You can then send or edit the email as you wish.
"""

if not config.isTermux:

    from toolmate import config, openURL
    import urllib.parse

    def send_gmail(function_args):
        email = "gmail"
        recipient = function_args.get("email", "") # required
        subject = function_args.get("subject", "") # required
        body = function_args.get("body", "") # required

        subject = urllib.parse.quote(subject)
        body = urllib.parse.quote(body)

        def getGoogleLink():
            link = "https://mail.google.com/mail/?view=cm&fs=1"
            if recipient:
                link += f"&to={recipient}"
            if subject:
                link += f"&su={subject}"
            if body:
                link += f"&body={body}"
            return link

        def getOutlookLink():
            link = "https://outlook.office.com/owa/?path=/mail/action/compose"
            if recipient:
                link += f"&to={recipient}"
            if subject:
                link += f"&subject={subject}"
            if body:
                link += f"&body={body}"
            return link

        openURL(getOutlookLink() if email == "outlook" else getGoogleLink())

        return ""

    functionSignature = {
        "examples": [
            "draft an Google email",
            "write an Google email",
            "send an Google email",
            "draft an Gmail",
            "write an Gmail",
            "send an Gmail",
        ],
        "name": "send_gmail",
        "description": "Send Gmail",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "The recipient of the email.",
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

    config.addFunctionCall(signature=functionSignature, method=send_gmail)