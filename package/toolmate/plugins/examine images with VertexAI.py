"""
ToolMate AI Plugin - analyze images

analyze images

Platform: llamacpp, ollama
Model: llava <- customizable
To customise:
Change in config.py:
llamacppVisionModel_model_path
llamacppVisionModel_clip_model_path
ollamaVisionModel

Platform: gemini
Model: Gemini Pro Vision

Platform: chaptgpt, letmedoit
Model "gpt-4o"
Reference: https://platform.openai.com/docs/guides/vision

[TOOL_CALL]
"""

from toolmate import config

if not config.isLite and config.online:

    from toolmate.utils.call_openai import check_openai_errors
    from toolmate.geminiprovision import GeminiProVision

    @check_openai_errors
    def examine_images_vertexai(function_args):
        from toolmate import config

        answer = GeminiProVision(temperature=config.llmTemperature).examine_images_vertexai(function_args)
        if answer:
            config.toolTextOutput = answer
            return ""
        else:
            return "[INVALID]"

    functionSignature = {
        "examples": [
            "describe image",
            "compare images",
            "analyze image",
        ],
        "name": "examine_images_vertexai",
        "description": "Describe or compare images with Gemini",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Questions or requests that users ask about the given images",
                },
                "image_filepath": {
                    "type": "string",
                    "description": """Return a list of image paths or urls, e.g. '["image1.png", "/tmp/image2.png", "https://letmedoit.ai/image.png"]'. Return '[]' if image path is not provided.""",
                },
            },
            "required": ["query", "image_filepath"],
        },
    }

    config.addToolCall(signature=functionSignature, method=examine_images_vertexai)
