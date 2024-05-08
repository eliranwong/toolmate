"""
FreeGenius AI Plugin - integrate google searches

Search internet for keywords when ChatGPT lacks information or when user ask about news or latest updates

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius import print1
import json, googlesearch

# pip3 install googlesearch-python
# Use google https://pypi.org/project/googlesearch-python/ to search internet for information, about which ChatGPT doesn't know.

def integrate_google_searches(function_args):
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
    "name": "integrate_google_searches",
    "description": "Search internet for real-time information or latest updates when you lack information",
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

config.addFunctionCall(signature=functionSignature, method=integrate_google_searches)