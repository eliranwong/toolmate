"""
ToolMate AI Plugin - analyze files

analyze files with integrated "AutoGen Retriever"

[TOOL_CALL]
"""

from toolmate import config

if not config.isLite:

    from toolmate import is_valid_image_file, ragRefineDocsPath, ragGetSplits, ragSearchContext, getRagPrompt
    from toolmate import print2, print3
    from toolmate.utils.call_llm import CallLLM
    from toolmate.autoretrieve import AutoGenRetriever
    import os
    #from PIL import Image


    def examine_files(function_args):
        query = function_args.get("query") # required
        files = function_args.get("filepath") # required
        if os.path.exists(files):
            if os.path.isfile(files) and is_valid_image_file(files):
                # call function "analyze image" instead if it is an image
                function_args = {
                    "query": query,
                    "files": [files],
                }
                print3("Running tool: 'examine_images'")
                return config.toolFunctionMethods["examine_images"](function_args)
            config.stopSpinning()
            if config.rag_useAutoRetriever:
                print2("AutoGen Retriever launched!")
                last_message = AutoGenRetriever().getResponse(files, query, True)
                config.currentMessages += last_message
                print2("AutoGen Retriever closed!")
            else:
                print2("Retriever utility launched!")

                retrievedContext = ragSearchContext(ragGetSplits(ragRefineDocsPath(files)), query)

                formatted_prompt = getRagPrompt(query, retrievedContext)

                messages = config.currentMessages[:-1] + [{"role": "user", "content" : formatted_prompt}]

                completion = CallLLM.regularCall(messages)
                print2(config.divider)
                config.toolmate.streamCompletion(completion)
                print2(config.divider)

                print2("Retriever utility closed!")
            return ""

        return "[INVALID]"

    functionSignature = {
        "examples": [
            "analyze files",
            "retrieve file information",
        ],
        "name": "examine_files",
        "description": "Retrieve information from files",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Detailed queries about the given files",
                },
                "filepath": {
                    "type": "string",
                    "description": """Return a directory or non-image file path. Return an empty string '' if it is not given.""",
                },
            },
            "required": ["query", "filepath"],
        },
    }

    config.addToolCall(signature=functionSignature, method=examine_files)