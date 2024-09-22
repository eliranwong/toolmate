"""
ToolMate AI Plugin - ask groq

Ask Groq Model for conversation only; no function calling

[FUNCTION_CALL]
"""


from toolmate import config
from toolmate.groqchat import GroqChatbot
from toolmate.utils.call_groq import CallGroq

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

def ask_groq(function_args):
    config.stopSpinning()
    query = function_args.get("query") # required
    config.currentMessages[-1] = {"role": "user", "content": query}
    completion = CallGroq.regularCall(config.currentMessages, chat_model=config.groqApi_chat_model if config.useAdditionalChatModel else None)
    streamCompletion(completion)
    return ""

functionSignature = {
    "examples": [
        "Ask Groq",
    ],
    "name": "ask_groq",
    "description": "Ask Groq to chat or provide information",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The original request in detail, including any supplementary information",
            },
        },
        "required": ["query"],
    },
}

config.addFunctionCall(signature=functionSignature, method=ask_groq)
config.inputSuggestions.append("Ask Groq: ")