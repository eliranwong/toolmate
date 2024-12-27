"""
ToolMate AI Plugin - search google

Search internet for keywords when LLM lacks information or when user ask about news or latest updates

# https://docs.anthropic.com/en/docs/build-with-claude/computer-use

[TOOL_CALL]
"""

from toolmate import config, getAnthropicClient, separateSystemMessage

if config.anthropicApi_key and not config.anthropicApi_key == "toolmate":

    import pyautogui
    screensize = pyautogui.size()

    def use_my_computer(_):
        config.stopSpinning()

        response = getAnthropicClient().beta.messages.create(
            model=config.anthropicApi_tool_model,
            temperature=config.llmTemperature,
            max_tokens=config.anthropicApi_tool_model_max_tokens,
            tools=[
                {
                    "type": "computer_20241022",
                    "name": "computer",
                    "display_width_px": screensize.width,
                    "display_height_px": screensize.height,
                    #"display_number": 1,
                },
                {
                    "type": "text_editor_20241022",
                    "name": "str_replace_editor"
                },
                {
                    "type": "bash_20241022",
                    "name": "bash"
                }
            ],
            messages=separateSystemMessage(config.currentMessages)[-1],
            betas=["computer-use-2024-10-22"],
        )

        config.toolTextOutput = response
        print(config.toolTextOutput)

        return ""

    functionSignature = {
        "examples": [],
        "name": "use_my_computer",
        "description": "Use Anthropic computer agent to take control of my computer to resolve my request.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }

    config.addToolCall(signature=functionSignature, method=use_my_computer)