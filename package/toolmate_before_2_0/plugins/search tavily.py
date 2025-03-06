"""
ToolMate AI Plugin - search Tavily

search Tavily

[TOOL_CALL]
"""

from toolmate import config

if not config.isLite and config.online:

    from toolmate import getTavilyClient

    def search_tavily(function_args):
        config.stopSpinning()
        if function_args:
            query = function_args.get("query")
            config.currentMessages[-1] = {"role": "user", "content": query}
        else:
            query = config.currentMessages[-1]["content"]
        context = getTavilyClient().get_search_context(query=query)
        return context

    functionSignature = {
        "examples": [
            "Search Tavily",
        ],
        "name": "search_tavily",
        "description": "Search for online information with Tavily",
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

    config.addToolCall(signature=functionSignature, method=search_tavily)
    config.inputSuggestions.append("Search Tavily: ")