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
    query = function_args.get("query") # required
    config.currentMessages[-1] = {"role": "user", "content": query}
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
        "properties": {
            #"model": {
            #    "type": "string",
            #    "description": "The LLM model name, e.g. 'llama3.1', 'llama3.1:8b', etc.",
            #},
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