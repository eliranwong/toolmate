from toolmate import config, print1, print2
import pyperclip

# Tool: @copy_to_clipboard
def copy_to_clipboard(function_args):
    content = config.currentMessages[-1]["content"]
    pyperclip.copy(content)
    message = "Copied!"
    print1(message)
    config.currentMessages[-1]["content"] = "Copy the following text to the system clipboard:\n\n```" + content + "\n```"
    config.currentMessages.append({"role": "assistant", "content": message})
    return ""
functionSignature = {
    "examples": [],
    "name": "copy_to_clipboard",
    "description": "Copy a given content to the system clipboard",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}
config.addFunctionCall(signature=functionSignature, method=copy_to_clipboard)

# Tool: @paste_from_clipboard
def paste_from_clipboard(function_args):
    content = config.currentMessages[-1]["content"]
    clipboardText = pyperclip.paste()
    print2("\n```clipboard")
    print1(f"{clipboardText}")
    print2("```")
    if not content.strip():
        config.currentMessages[-1]["content"] = "Retrieve and display the contents of the system clipboard."
        config.currentMessages.append({"role": "assistant", "content": clipboardText})
        return ""
    config.currentMessages[-1]["content"] = f"{content}\n\n{clipboardText}"
    return "[INVALID]" # this take to generate a chat response based on the user input, together with the clipboard content
functionSignature = {
    "examples": [],
    "name": "paste_from_clipboard",
    "description": "Retrieve the text content from the system clipboard and paste",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}
config.addFunctionCall(signature=functionSignature, method=paste_from_clipboard)