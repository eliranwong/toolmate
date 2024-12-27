"""
ToolMate AI Plugin - ask chatgpt

Ask ChatGPT for conversation only; no function calling

[TOOL_CALL]
"""


from toolmate import config

if config.online:

    from toolmate import print1, useChatSystemMessage
    from toolmate.utils.call_openai import CallOpenAI
    import copy

    try:
        CallOpenAI.checkCompletion()

        def o1(function_args):
            config.stopSpinning()
            if function_args:
                query = function_args.get("query") # required
                config.currentMessages[-1] = {"role": "user", "content": query}
            else:
                query = config.currentMessages[-1]["content"]

            # read beta limitations at https://platform.openai.com/docs/guides/reasoning/beta-limitations
            chatMessages = useChatSystemMessage(copy.deepcopy(config.currentMessages))
            chatMessages = [i for i in chatMessages if not i.get("role", "") == "system"] # beta doesn't support system message
            completion = config.oai_client.chat.completions.create(
                model="o1-preview",
                messages=chatMessages,
                max_completion_tokens=32768,
            )
            config.toolTextOutput = completion.choices[0].message.content
            print1(config.toolTextOutput)
            return ""

        functionSignature = {
            "examples": [
                "Ask o1",
            ],
            "name": "o1",
            "description": "Ask reasoning model o1 to chat or provide information",
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

        config.addToolCall(signature=functionSignature, method=o1)
        config.inputSuggestions.append("Ask o1: ")

    except:
        print("Plugin `ask o1` not enabled! Check if your OpenAI API key is valid!")