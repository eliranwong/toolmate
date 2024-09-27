"""
ToolMate AI Plugin - ask Llama2

Ask Llama2 for information

[TOOL_CALL]
"""

from toolmate import config
from toolmate import print2
from toolmate.ollamachat import OllamaChat
#from toolmate.utils.ollama_models import ollama_models

from toolmate.utils.call_ollama import CallOllama

def ask_llama3_1(function_args):
    model = "llama3.1"
    config.stopSpinning()
    query = function_args.get("query") # required
    config.currentMessages[-1] = {"role": "user", "content": query}
    completion = CallOllama.regularCall(config.currentMessages, chat_model=model)
    config.toolmate.streamCompletion(completion, openai=False)
    if not model == config.ollamaToolModel:
        CallOllama.unloadModels(model)
    return ""

functionSignature = {
    "examples": [
        "Ask Llama3.1",
    ],
    "name": "ask_llama3_1",
    "description": "Ask Llama3.1 to chat or provide information",
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

config.addFunctionCall(signature=functionSignature, method=ask_llama3_1)
config.inputSuggestions.append("Ask Llama3.1: ")