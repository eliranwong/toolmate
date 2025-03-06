"""
ToolMate AI Plugin - search contacts

search contacts on Android

[TOOL_CALL]
"""

from toolmate import config

if config.isTermux:

    from toolmate import print3
    import subprocess, json

    def search_contacts(function_args):
        found = []
        content = config.currentMessages[-1]["content"]
        contacts = subprocess.run("termux-contact-list", shell=True, capture_output=True, text=True).stdout
        contacts = json.loads(contacts)
        config.stopSpinning()
        for i in contacts:
            name = i.get("name", "")
            number = i.get("number", "")
            if content in name or content in number:
                foundItem = f"{name}: {number}"
                found.append(foundItem)
                try:
                    print3(foundItem)
                except:
                    print(foundItem)
        if found:
            config.toolTextOutput = "\n".join(found)
        return ""

    functionSignature = {
        "examples": [],
        "name": "search_contacts",
        "description": f'''Search contacts''',
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }

    config.addToolCall(signature=functionSignature, method=search_contacts)