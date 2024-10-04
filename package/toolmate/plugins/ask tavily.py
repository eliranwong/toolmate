"""
ToolMate AI Plugin - ask Tavily

Ask Tavily

[TOOL_CALL]
"""

if not config.isTermux:

    from toolmate import config, getTavilyClient, print1

    def ask_tavily(function_args):
        query = function_args.get("query") # required
        config.currentMessages[-1] = {"role": "user", "content": query}
        config.toolTextOutput = getTavilyClient().qna_search(query=query)
        config.stopSpinning()
        print1(config.toolTextOutput)
        return ""

    functionSignature = {
        "examples": [
            "Ask internet",
        ],
        "name": "ask_tavily",
        "description": "Ask internet for a short and direct answer",
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

    config.addFunctionCall(signature=functionSignature, method=ask_tavily)
    config.inputSuggestions.append("Ask Tavily: ")