"""
ToolMate AI Plugin - ask gemini pro

Ask Google Gemini Pro for information

[TOOL_CALL]
"""

from toolmate import config, getGenAIClient

if not config.isLite and config.online:
    import os
    if getGenAIClient() is not None and not config.isLite:

        from toolmate import config
        from toolmate.utils.call_genai import CallGenAI

        def genai(function_args):
            config.stopSpinning()
            if function_args:
                query = function_args.get("query") # required
                config.currentMessages[-1] = {"role": "user", "content": query}
            else:
                query = config.currentMessages[-1]["content"]
            completion = CallGenAI.regularCall(config.currentMessages)
            config.toolmate.streamCompletion(completion, openai=False)
            return ""

        functionSignature = {
            "examples": [
                "Ask Gemini",
            ],
            "name": "genai",
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

        config.addToolCall(signature=functionSignature, method=genai)
        config.inputSuggestions.append("Ask Gemini: ")
    else:
        print("Plugin `ask gemini` not enabled! Read setup at https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Google%20Cloud%20Service%20Credential%20Setup.md")