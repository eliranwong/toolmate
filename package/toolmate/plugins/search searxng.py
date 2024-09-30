"""
ToolMate AI Plugin - search SearxNG

Default Configurations
(assuming Perplexica is installed locally)
searx_server = "localhost"
searx_port = 4000

You can manually edit config.py to customise these settings.

[TOOL_CALL]
"""

from langchain_community.utilities import SearxSearchWrapper
from toolmate import config, isServerAlive

persistentConfigs = (
    ("searx_server", "localhost"),
    ("searx_port", 4000),
)
config.setConfig(persistentConfigs)

if isServerAlive(config.searx_server, config.searx_port):

    def search_searxng(function_args):
        query = function_args.get("query") # required
        config.currentMessages[-1] = {"role": "user", "content": query}
        context = SearxSearchWrapper(searx_host=f"http://{config.searx_server}:{config.searx_port}").run(query)
        config.stopSpinning()
        return context

    functionSignature = {
        "examples": [
            "Search SearxNG",
        ],
        "name": "search_searxng",
        "description": "Search SearxNG for online information",
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

    config.addFunctionCall(signature=functionSignature, method=search_searxng)
    config.inputSuggestions.append("Search SearxNG: ")

else:

    print1(f"Searx Host `http://{config.searx_server}:{config.searx_port}`! Plugin `search searxng not enabled!`")