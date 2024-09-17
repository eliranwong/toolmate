"""
ToolMate AI Plugin - analyze files

analyze files with integrated "AutoGen Retriever"

[FUNCTION_CALL]
"""


from toolmate import config, is_valid_image_file
from toolmate import print2, print3
import os
from toolmate.autoretriever import AutoGenRetriever
from toolmate.rag import RAG
#from PIL import Image


def analyze_files(function_args):
    query = function_args.get("query") # required
    files = function_args.get("filepath") # required
    if os.path.exists(files):
        if os.path.isfile(files) and is_valid_image_file(files):
            # call function "analyze image" instead if it is an image
            function_args = {
                "query": query,
                "files": [files],
            }
            print3("Running function: 'analyze_images'")
            return config.toolFunctionMethods["analyze_images"](function_args)
        config.stopSpinning()
        if config.rag_useAutoRetriever and not config.llmInterface == "gemini":
            print2("AutoGen Retriever launched!")
            last_message = AutoGenRetriever().getResponse(files, query, True)
            config.currentMessages += last_message
            print2("AutoGen Retriever closed!")
        else:
            print2("Retriever utility launched!")
            RAG().getResponse(files, query)
            print2("Retriever utility closed!")
        return ""

    return "[INVALID]"

functionSignature = {
    "examples": [
        "analyze files",
        "retrieve file information",
    ],
    "name": "analyze_files",
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

config.addFunctionCall(signature=functionSignature, method=analyze_files)