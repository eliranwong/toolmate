"""
ToolMate AI Plugin - search bing

Search internet for keywords when LLM lacks information or when user ask about news or latest updates

[TOOL_CALL]
"""

from toolmate import config

if config.online and config.bing_api_key and not config.bing_api_key == "toolmate":

    from toolmate import print1
    import json, os, requests

    # pip3 install googlesearch-python
    # Use google https://pypi.org/project/googlesearch-python/ to search internet for information, about which ChatGPT doesn't know.

    def search_google(function_args):
        config.stopSpinning()
        if function_args:
            keywords = function_args.get("keywords")
            #config.currentMessages[-1] = {"role": "user", "content": keywords}
        else:
            keywords = config.currentMessages[-1]["content"]

        print1("Loading internet searches ...")

        # Construct a request
        mkt = 'en-US'
        params = { 'q': keywords, 'mkt': mkt }
        headers = { 'Ocp-Apim-Subscription-Key': config.bing_api_key }

        # Call the API
        try:
            response = requests.get(config.bing_api_endpoint, headers=headers, params=params)
            response.raise_for_status()

            print("Headers:")
            print(response.headers)

            print("JSON Response:")
            import pprint
            pprint(response.json())
        except Exception as ex:
            raise ex

        return response.text

    functionSignature = {
        "examples": [],
        "name": "search_google",
        "description": "Search Google for real-time information or latest updates when LLM lacks information",
        "parameters": {
            "type": "object",
            "properties": {} if not config.tool_selection_agent else {
                "keywords": {
                    "type": "string",
                    "description": "Keywords for online searches",
                },
            },
            "required": [] if not config.tool_selection_agent else ["keywords"],
        },
    }

    config.addToolCall(signature=functionSignature, method=search_google)