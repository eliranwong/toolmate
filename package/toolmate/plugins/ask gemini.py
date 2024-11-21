"""
ToolMate AI Plugin - ask gemini pro

Ask Google Gemini Pro for information

[TOOL_CALL]
"""

if os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Vertex AI" in config.enabledGoogleAPIs and not config.isLite:

    import vertexai
    from vertexai.generative_models._generative_models import (
        HarmCategory,
        HarmBlockThreshold,
    )
    from toolmate import config
    from toolmate.utils.call_gemini import CallVertexAI

    def ask_gemini(function_args):
        config.stopSpinning()
        if function_args:
            query = function_args.get("query") # required
            config.currentMessages[-1] = {"role": "user", "content": query}
        else:
            query = config.currentMessages[-1]["content"]
        completion = CallVertexAI.regularCall(config.currentMessages)
        config.toolmate.streamCompletion(completion, openai=False)
        return ""

    functionSignature = {
        "examples": [
            "Ask Gemini",
        ],
        "name": "ask_gemini",
        "description": "Ask Gemini to chat or provide information",
        "parameters": {
            "type": "object",
            "properties": {} if not config.tool_selection_agent else {
                "query": {
                    "type": "string",
                    "description": "The original request in detail, including any supplementary information",
                },
            },
            "required": [] if not config.tool_selection_agent else ["query"],
        },
    }

    # initiation
    vertexai.init()

    # Note: BLOCK_NONE is not allowed
    config.gemini_safety_settings={
        HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }
    config.addFunctionCall(signature=functionSignature, method=ask_gemini)
    config.inputSuggestions.append("Ask Gemini: ")
else:
    print("Plugin `ask gemini` not enabled! Read setup at https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Google%20Cloud%20Service%20Credential%20Setup.md")