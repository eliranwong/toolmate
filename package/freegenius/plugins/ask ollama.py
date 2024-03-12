"""
LetMeDoIt AI Plugin - ask Ollama Chat

Ask Ollama Chat for information

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.ollamachat import OllamaChat
from freegenius.utils.ollama_models import ollama_models
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from prompt_toolkit.styles import Style
from freegenius.health_check import HealthCheck
from pathlib import Path
import os


def ask_ollama(function_args):
    query = function_args.get("query") # required
    config.stopSpinning()

    # model
    promptStyle = Style.from_dict({
        # User input (default text).
        "": config.terminalCommandEntryColor2,
        # Prompt.
        "indicator": config.terminalPromptIndicatorColor2,
    })
    historyFolder = os.path.join(HealthCheck.getLocalStorage(), "history")
    Path(historyFolder).mkdir(parents=True, exist_ok=True)
    model_history = os.path.join(historyFolder, "ollama_default")
    model_session = PromptSession(history=FileHistory(model_history))
    completer = FuzzyCompleter(WordCompleter(sorted(ollama_models), ignore_case=True))
    bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}"""

    HealthCheck.print2("Ollama chat launched!")
    print("Select a model below:")
    print("Note: You should have at least 8 GB of RAM available to run the 7B models, 16 GB to run the 13B models, and 32 GB to run the 33B models.")
    model = HealthCheck.simplePrompt(style=promptStyle, promptSession=model_session, bottom_toolbar=bottom_toolbar, default=config.ollamaDefaultModel, completer=completer)
    if model:
        if model.lower() == config.exit_entry:
            return ""
    else:
        model = config.ollamaDefaultModel
    OllamaChat().run(query, model=model)
    return ""

functionSignature = {
    "intent": [
        "ask a chatbot",
    ],
    "examples": [
        "Ask Ollama about",
    ],
    "name": "ask_ollama",
    "description": "Ask Ollama to chat or provide information",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The request in detail, including any supplementary information",
            },
        },
        "required": ["query"],
    },
}

config.addFunctionCall(signature=functionSignature, method=ask_ollama)
config.inputSuggestions.append("Ask Ollama: ")