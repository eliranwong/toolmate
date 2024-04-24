"""
FreeGenius AI Plugin - input suggestions

add input suggestions
"""

from freegenius import config
import sys, os

config.inputSuggestions += [
        "[CHAT] ",
        "[CHAT_chatgpt] ",
        "[CHAT_geminipro] ",
        "[CHAT_palm2] ",
        "[CHAT_codey] ",
        "[NO_TOOL] ",
        f"!{config.open} ",
        f"!{sys.executable} ",
        "open with default application: ",
        "open with file manager: ",
        "open with web browser: ",
        "read ",
        "search ",
        "analyze ",
        "tell me about ",
        "write a summary ",
        "explain ",
        "What does it mean? ",
        "Craft a prompt for ChatGPT that outlines the necessary steps it should take to complete the following task at hand:\n[CHAT]\n",
        f"Improve the following content according to {config.improvedWritingSytle}:\n[CHAT]\n",
        "Before you start, please ask me any questions you have about this so I can give you more context. Be extremely comprehensive.",
        "Write a short and complete summary of the text below:\n",
        "Ues the provided text and list 5 main topics.",
        "Using the provided text, raise 5 short questions that can help investigating the subject. The questions must be of the type 'who', 'what', 'when', 'how', 'why'.",
        """You are a Language Model trained to answer questions based solely on the provided text. The provided text is your only source of information, and you must not use any external knowledge. If you do not have enough information from the text to answer a question, please reply with 'I don't know.'

Question: {question}

```
{text}
```""",
        """Given a block of text, please extract and return the list of all sections and main topics. The list must provide a clear and concise overview of what is being discussed. This list must help readers to quickly find the information they need and navigate through the content. Avoid repetitions.

```
{text}
```

Index of the topics:""",
    ]

config.inputSuggestions.append("""Translate Content. Assist me by acting as a translator. Once I have provided you with the content, you should inquire about the language I need it translated into. After I inform you of the desired language, proceed with the translation.
[CHAT]
Please translate the content below:
""")