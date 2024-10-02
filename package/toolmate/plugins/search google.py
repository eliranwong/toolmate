"""
ToolMate AI Plugin - search google

Search internet for keywords when LLM lacks information or when user ask about news or latest updates

[TOOL_CALL]
"""

from toolmate import config
from toolmate import print1
import json, googlesearch

# pip3 install googlesearch-python
# Use google https://pypi.org/project/googlesearch-python/ to search internet for information, about which ChatGPT doesn't know.

def search_google(function_args):
    # retrieve argument values from a dictionary
    #print(function_args)
    keywords = function_args.get("keywords") # required

    print1("Loading internet searches ...")

    info = {}
    for index, item in enumerate(googlesearch.search(keywords, advanced=True, num_results=config.maximumInternetSearchResults)):
        info[f"information {index}"] = {
            "title": item.title,
            "url": item.url,
            "description": item.description,
        }

    print1("Loaded!\n")

    return json.dumps(info)

functionSignature = {
    "examples": [
        "access real-time information",
        "search online",
        "Google search",
    ],
    "name": "search_google",
    "description": "Search Google for real-time information or latest updates when LLM lacks information",
    "parameters": {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "string",
                "description": "keywords for searches, e.g. ChatGPT",
            },
        },
        "required": ["keywords"],
    },
}

config.addFunctionCall(signature=functionSignature, method=search_google)