"""
ToolMate AI Plugin - ask Codey

Ask Google Codey for information about coding

[TOOL_CALL]
"""

if not config.isLite:
    if os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Vertex AI" in config.enabledGoogleAPIs:

        import vertexai
        from vertexai.generative_models._generative_models import (
            HarmCategory,
            HarmBlockThreshold,
        )
        from toolmate import config
        import vertexai
        from vertexai.language_models import CodeChatModel, ChatMessage

        def ask_codey(function_args):
            config.stopSpinning()
            if function_args:
                query = function_args.get("query") # required
                config.currentMessages[-1] = {"role": "user", "content": query}
            else:
                query = config.currentMessages[-1]["content"]

            model = CodeChatModel.from_pretrained("codechat-bison-32k")
            # https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/text-chat
            parameters = {
                "temperature": config.llmTemperature,  # Temperature controls the degree of randomness in token selection; 0.0–1.0; Default: 0.0
                "max_output_tokens": 2048,  # Token limit determines the maximum amount of text output; 1–2048; Default: 1024
            }
            history = []
            user = True
            for i in config.currentMessages:
                if i["role"] == "user" if user else "assistant":
                    history.append(ChatMessage(content=i["content"], author="user" if user else "model"))
                    user = not user
            if history and history[-1].author == "user":
                history = history[:-1]
            elif not history:
                history = None
            chat = model.start_chat(
                context=config.systemMessage_palm2,
                message_history=history,
                #examples=[
                #    InputOutputTextPair(
                #        input_text="How many moons does Mars have?",
                #        output_text="The planet Mars has two moons, Phobos and Deimos.",
                #    ),
                #],
            )

            response = chat.send_message(query, **parameters)
            config.toolTextOutput = response.text.strip()
            if hasattr(config, "desktopAssistant"):
                config.desktopAssistant.printTextOutput(config.toolTextOutput)
            else:
                print(config.toolTextOutput)
            return ""

        functionSignature = {
            "examples": [
                "Ask Codey",
            ],
            "name": "ask_codey",
            "description": "Ask Codey for information about coding",
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
        config.addFunctionCall(signature=functionSignature, method=ask_codey)
        config.inputSuggestions.append("Ask Codey: ")
    else:
        print("Plugin `ask codey` not enabled! Read setup at https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Google%20Cloud%20Service%20Credential%20Setup.md")