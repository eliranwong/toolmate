"""
LetMeDoIt AI Plugin - input suggestions

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
        "[NO_FUNCTION_CALL] ",
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
    ]

config.inputSuggestions.append("""Translate Content. Assist me by acting as a translator. Once I have provided you with the content, you should inquire about the language I need it translated into. After I inform you of the desired language, proceed with the translation.
[CHAT]
Please translate the content below:
""")