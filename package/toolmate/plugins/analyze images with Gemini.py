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

if not config.isTermux:

    from toolmate import config, print1, print2, is_valid_image_file, is_valid_image_url, startLlamacppVisionServer, stopLlamacppVisionServer, is_valid_url, runToolMateCommand, getLlamacppServerClient
    from toolmate.utils.call_chatgpt import check_openai_errors
    import os
    from openai import OpenAI
    from toolmate.geminiprovision import GeminiProVision
    from toolmate.utils.call_ollama import CallOllama

    @check_openai_errors
    def analyze_images_gemini(function_args):
        from toolmate import config

        answer = GeminiProVision(temperature=config.llmTemperature).analyze_images_gemini(function_args)
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
        "name": "analyze_images_gemini",
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

    config.addFunctionCall(signature=functionSignature, method=analyze_images_gemini)
    config.inputSuggestions.append("Describe this image in detail: ")
    config.inputSuggestions.append("Extract text from this image: ")