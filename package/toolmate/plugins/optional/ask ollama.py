"""
ToolMate AI Plugin - ask Ollama Chat

Ask Ollama Chat for information

[FUNCTION_CALL]
"""

from toolmate import config
from toolmate import print2
from toolmate.ollamachat import OllamaChat
from toolmate.utils.ollama_models import ollama_models
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from prompt_toolkit.styles import Style
from toolmate.utils.single_prompt import SinglePrompt
from pathlib import Path
import os


from toolmate.utils.call_ollama import CallOllama

#####
from toolmate.gui.worker import QtResponseStreamer
from toolmate.utils.streaming_word_wrapper import StreamingWordWrapper
import threading, traceback
def streamCompletion(completion):
    try:
        if hasattr(config, "desktopAssistant"):
            QtResponseStreamer(config.desktopAssistant).workOnCompletion(completion, True)
        else:
            # Create a new thread for the streaming task
            streamingWordWrapper = StreamingWordWrapper()
            streaming_event = threading.Event()
            streaming_thread = threading.Thread(target=streamingWordWrapper.streamOutputs, args=(streaming_event, completion, True))
            # Start the streaming thread
            streaming_thread.start()
            # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+z' to stop the streaming
            streamingWordWrapper.keyToStopStreaming(streaming_event)
            # when streaming is done or when user press "ctrl+q"
            streaming_thread.join()
    except:
        print(traceback.format_exc())
        try:
            streaming_thread.join()
        except:
            pass
#####

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
    historyFolder = os.path.join(config.localStorage, "history")
    Path(historyFolder).mkdir(parents=True, exist_ok=True)
    model_history = os.path.join(historyFolder, "ollama_default")
    model_session = PromptSession(history=FileHistory(model_history))
    completer = FuzzyCompleter(WordCompleter(sorted(ollama_models), ignore_case=True))
    bottom_toolbar = f""" {str(config.hotkey_exit).replace("'", "")} {config.exit_entry}"""

    print2("Ollama chat launched!")
    print("Select a model below:")
    print("Note: You should have at least 8 GB of RAM available to run the 7B models, 16 GB to run the 13B models, and 32 GB to run the 33B models.")
    model = SinglePrompt.run(style=promptStyle, promptSession=model_session, bottom_toolbar=bottom_toolbar, default=config.ollamaMainModel, completer=completer)
    if model:
        if model.lower() == config.exit_entry:
            return ""
    else:
        model = config.ollamaMainModel
    OllamaChat().run(query, model=model, once=True)
    return ""

functionSignature = {
    "examples": [
        "Ask Ollama",
    ],
    "name": "ask_ollama",
    "description": "Ask an Ollama model to chat or provide information",
    "parameters": {
        "type": "object",
        "properties": {
            "model": {
                "type": "string",
                "description": "The LLM model name, e.g. 'llama3.1', 'llama3.1:8b', etc.",
            },
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