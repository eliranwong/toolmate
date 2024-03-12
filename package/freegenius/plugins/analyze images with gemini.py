"""
LetMeDoIt AI Plugin - analyze images with gemini

analyze images with model "gemini pro vision"

reference: https://platform.openai.com/docs/guides/vision

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.geminiprovision import GeminiProVision

def analyze_images_with_gemini(function_args):
    answer = GeminiProVision(temperature=config.llmTemperature).analyze_images(function_args)
    if answer:
        config.tempContent = answer
    return "[INVALID]" if not answer else ""

functionSignature = {
    "intent": [
        "analyze files",
    ],
    "examples": [
        "analyze image with Gemini",
    ],
    "name": "analyze_images_with_gemini",
    "description": "Use Gemini Pro Vision to describe or analyze images",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Questions or requests that users ask about the given images",
            },
            "files": {
                "type": "string",
                "description": """Return a list of image paths or urls, e.g. '["image1.png", "/tmp/image2.png", "https://letmedoit.ai/image.png"]'. Return '[]' if image path is not provided.""",
            },
        },
        "required": ["query", "files"],
    },
}

config.addFunctionCall(signature=functionSignature, method=analyze_images_with_gemini)
config.inputSuggestions.append("Ask Gemini Pro Vision to describe this image in detail: ")