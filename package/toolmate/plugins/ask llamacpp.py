"""
ToolMate AI Plugin - ask chatgpt

Ask ChatGPT for conversation only; no function calling

[TOOL_CALL]
"""

if not config.isTermux:

    from toolmate import config, print1, loadLlamacppChatModel
    from toolmate.utils.call_llamacpp import CallLlamaCpp

    def ask_llamacpp(function_args):
        chatModel = None
        config.stopSpinning()
        query = function_args.get("query") # required
        config.currentMessages[-1] = {"role": "user", "content": query}
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
        "name": "ask_llamacpp",
        "description": "Ask Llama.cpp to chat or provide information",
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

    config.addFunctionCall(signature=functionSignature, method=ask_llamacpp)
    config.inputSuggestions.append("Ask ChatGPT: ")