"""
ToolMate AI Plugin - ask chatgpt

Ask ChatGPT for conversation only; no function calling

[TOOL_CALL]
"""

from toolmate import config

try:
    from toolmate.utils.call_llamacpp import CallLlamaCpp
    runnable = True
except:
    runnable = False

if not config.isLite and runnable:

    from toolmate import print1, loadLlamacppChatModel

    def llamacpppython(function_args):
        chatModel = None
        config.stopSpinning()
        if function_args:
            query = function_args.get("query") # required
            config.currentMessages[-1] = {"role": "user", "content": query}
        else:
            query = config.currentMessages[-1]["content"]
        if config.useAdditionalChatModel:
            chatModel = loadLlamacppChatModel()
            completion = CallLlamaCpp.regularCall(config.currentMessages, model=chatModel)
        else:
            completion = CallLlamaCpp.regularCall(config.currentMessages)
        config.toolmate.streamCompletion(completion, openai=False)
        if chatModel is not None:
            try:
                chatModel.close()
                print1("Llama.cpp chat model unloaded!")
            except:
                pass
        return ""

    functionSignature = {
        "examples": [
            "Ask Llama.cpp",
        ],
        "name": "llamacpppython",
        "description": "Ask Llama.cpp to chat or provide information",
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

    config.addToolCall(signature=functionSignature, method=llamacpppython)
    config.inputSuggestions.append("Ask ChatGPT: ")