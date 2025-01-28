"""
ToolMate AI Plugin - ask llama.cpp server

Ask llama.cpp server Model for conversation only; no function calling

[TOOL_CALL]
"""

from toolmate import config
from toolmate.utils.call_llamacppserver import CallLlamaCppServer

def llamacpp(function_args):
    config.stopSpinning()
    if function_args:
        query = function_args.get("query") # required
        config.currentMessages[-1] = {"role": "user", "content": query}
    else:
        query = config.currentMessages[-1]["content"]
    completion = CallLlamaCppServer.regularCall(config.currentMessages)
    config.toolmate.streamCompletion(completion, openai=True)
    return ""

functionSignature = {
    "examples": [
        "Ask Llama.cpp Server",
    ],
    "name": "llamacpp",
    "description": "Ask Llama.cpp Server to chat or provide information",
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

config.addToolCall(signature=functionSignature, method=llamacpp)
config.inputSuggestions.append("Ask Llama.cpp Server: ")