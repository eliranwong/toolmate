"""
LetMeDoIt AI Plugin - analyze files

analyze files with integrated "AutoGen Retriever"

[FUNCTION_CALL]
"""


from freegenius import config
import os
from freegenius.autoretriever import AutoGenRetriever
from PIL import Image


def analyze_files(function_args):
    def is_valid_image_file(file_path):
        try:
            # Open the image file
            with Image.open(file_path) as img:
                # Check if the file format is supported by PIL
                img.verify()
                return True
        except (IOError, SyntaxError) as e:
            # The file path is not a valid image file path
            return False

    query = function_args.get("query") # required
    files = function_args.get("files") # required
    if os.path.exists(files):
        if os.path.isfile(files) and is_valid_image_file(files):
            # call function "analyze image" instead if it is an image
            function_args = {
                "query": query,
                "files": [files],
            }
            config.print3("Running function: 'analyze_images'")
            return config.chatGPTApiAvailableFunctions["analyze_images"](function_args)
        config.stopSpinning()
        config.print2("AutoGen Retriever launched!")
        last_message = AutoGenRetriever().getResponse(files, query)
        config.currentMessages += last_message
        config.print2("AutoGen Retriever closed!")
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