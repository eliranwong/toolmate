"""
ToolMate AI Plugin - help

Retrieve information from the documentation regarding how to use ToolMate AI

[TOOL_CALL]
"""

from toolmate import config

if not config.isLite:

    from toolmate import getHelpCollection, query_vectors, getRagPrompt, print2
    from toolmate.utils.call_llm import CallLLM


    def help(function_args):
        query = function_args.get("query") # required
        if query.strip():
            collection = getHelpCollection()
            retrievedContext = query_vectors(collection, query, n=config.rag_closestMatches)["documents"]
            ragPrompt = getRagPrompt(query, retrievedContext)

            messages = config.currentMessages[:-1] + [{"role": "user", "content" : ragPrompt}]
            completion = CallLLM.regularCall(messages)
            print2(config.divider)
            config.toolmate.streamCompletion(completion)
            print2(config.divider)
        else:
            config.currentMessages = config.currentMessages[:-1]
        return ""

    functionSignature = {
        "examples": [
            "how to use ToolMate AI",
        ],
        "name": "help",
        "description": "Retrieve information from the documentation regarding how to use ToolMate AI",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Detailed queries about how to use ToolMate AI",
                },
            },
            "required": ["query"],
        },
    }

    config.addToolCall(signature=functionSignature, method=help)