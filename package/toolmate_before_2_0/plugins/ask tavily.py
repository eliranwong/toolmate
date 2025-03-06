"""
ToolMate AI Plugin - ask Tavily

Ask Tavily

[TOOL_CALL]
"""

from toolmate import config

if not config.isLite and config.online:

    from toolmate import getTavilyClient, print1

    def tavily(function_args):
        config.stopSpinning()
        if function_args:
            query = function_args.get("query")
            config.currentMessages[-1] = {"role": "user", "content": query}
        else:
            query = config.currentMessages[-1]["content"]
        config.toolTextOutput = getTavilyClient().qna_search(query=query)
        print1(config.toolTextOutput)
        return ""

    functionSignature = {
        "examples": [
            "Ask internet",
        ],
        "name": "tavily",
        "description": "Ask internet for a short and direct answer",
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

    config.addToolCall(signature=functionSignature, method=tavily)
    config.inputSuggestions.append("Ask Tavily: ")