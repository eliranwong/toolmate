"""
LetMeDoIt AI Plugin - analyze files

analyze files with integrated "AutoGen Retriever"

[FUNCTION_CALL]
"""


from freegenius import config, is_valid_image_file
from freegenius import print2, print3
import os
from freegenius.autoretriever import AutoGenRetriever
from PIL import Image


def analyze_files(function_args):

    query = function_args.get("query") # required
    files = function_args.get("files") # required
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
        print2("AutoGen Retriever launched!")
        last_message = AutoGenRetriever().getResponse(files, query, True)
        config.currentMessages += last_message
        print2("AutoGen Retriever closed!")
        return ""

    return "[INVALID]"

functionSignature = {
    "intent": [
        "analyze files",
    ],
    "examples": [
        "analyze files",
    ],
    "name": "analyze_files",
    "description": "retrieve information from files",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Detailed queries about the given files",
            },
            "files": {
                "type": "string",
                "description": """Return a directory or non-image file path. Return an empty string '' if it is not given.""",
            },
        },
        "required": ["query", "files"],
    },
}

config.addFunctionCall(signature=functionSignature, method=analyze_files)