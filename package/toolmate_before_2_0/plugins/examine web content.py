"""
ToolMate AI Plugin - analyze web content

analyze web content with "AutoGen Retriever"

[TOOL_CALL]
"""

from toolmate import config

if not config.isLite and config.online:

    from toolmate import print1, print2, print3, is_valid_url, downloadWebContent, ragRefineDocsPath, ragGetSplits, ragSearchContext, getRagPrompt
    from toolmate.utils.call_llm import CallLLM
    from toolmate.autoretrieve import AutoGenRetriever

    def examine_web_content(function_args):
        query = function_args.get("query") # required
        url = function_args.get("url") # required
        if not url or not is_valid_url(url):
            print1(f"'{url}' is not a valid url" if url else "No url is provided!")
            return "[INVALID]"
        config.stopSpinning()
        kind, filename = downloadWebContent(url)
        if not filename:
            return "[INVALID]"
        elif kind == "image":
            # call function "analyze image" instead if it is an image
            function_args = {
                "query": query,
                "files": [filename],
            }
            print3("Running tool: 'examine_images'")
            return config.toolFunctionMethods["examine_images"](function_args)

        if config.rag_useAutoRetriever:
            # process with AutoGen Retriever
            print2("AutoGen Retriever launched!")
            last_message = AutoGenRetriever().getResponse(filename, query, True)
            config.currentMessages += last_message
            print2("AutoGen Retriever closed!")
        else:
            print2("Retriever utility launched!")

            retrievedContext = ragSearchContext(ragGetSplits(ragRefineDocsPath(filename)), query)

            formatted_prompt = getRagPrompt(query, retrievedContext)

            messages = config.currentMessages[:-1] + [{"role": "user", "content" : formatted_prompt}]

            completion = CallLLM.regularCall(messages)
            print2(config.divider)
            config.toolmate.streamCompletion(completion)
            print2(config.divider)

            print2("Retriever utility closed!")
        return ""

    functionSignature = {
        "examples": [
            "analyze this url",
            "retrieve website information",
            "summarize this webpage",
        ],
        "name": "examine_web_content",
        "description": "retrieve information from a webpage if an url is provided",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": """Return the given url. Return an empty string '' if it is not given.""",
                },
                "query": {
                    "type": "string",
                    "description": "Question that I ask about the given url",
                },
            },
            "required": ["query", "url"],
        },
    }

    config.addToolCall(signature=functionSignature, method=examine_web_content)