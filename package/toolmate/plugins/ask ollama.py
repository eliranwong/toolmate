"""
ToolMate AI Plugin - ask Ollama Chat

Ask Ollama Chat for information

[TOOL_CALL]
"""

from toolmate import config
#from toolmate.utils.ollama_models import ollama_models
from toolmate.utils.call_ollama import CallOllama

def ask_ollama(function_args):
    config.stopSpinning()
    if function_args:
        query = function_args.get("query") # required
        config.currentMessages[-1] = {"role": "user", "content": query}
    else:
        query = config.currentMessages[-1]["content"]
    completion = CallOllama.regularCall(config.currentMessages, chat_model=config.ollamaChatModel if config.useAdditionalChatModel else None)
    config.toolmate.streamCompletion(completion, openai=False)
    if config.useAdditionalChatModel and not config.ollamaChatModel == config.ollamaToolModel:
        CallOllama.unloadModels(config.ollamaChatModel)
    return ""

functionSignature = {
    "examples": [
        "Ask Ollama",
    ],
    "name": "ask_ollama",
    "description": "Ask an Ollama model to chat or provide information",
    "parameters": {
        "type": "object",
        "properties": {} if not config.tool_selection_agent else {
            "query": {
                "type": "string",
                "description": "The original request in detail, including any supplementary information",
            },
        },
        "required": [] if not config.tool_selection_agent else ["query"],
    },
}

config.addFunctionCall(signature=functionSignature, method=ask_ollama)
config.inputSuggestions.append("Ask Ollama: ")