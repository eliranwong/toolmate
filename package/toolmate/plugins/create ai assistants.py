"""
ToolMate AI Plugin - build agents

build a group of agents to execute a task with integrated "AutoGen Agent Builder"

[TOOL_CALL]
"""


if not config.isTermux:
    try:
        from toolmate.autobuilder import AutoGenBuilder
        from toolmate import config
        from toolmate import print1, print2, print3

        def build_agents(function_args):
            if not config.openaiApiKey or config.openaiApiKey == "toolmate":
                return "OpenAI API key not found! This feature works with ChatGPT models only!"
            task = function_args.get("task") # required
            title = function_args.get("title") # required
            print2("AutoGen Agent Builder launched!")
            print3(f"Title: {title}")
            print3(f"Description: {task}")
            messages = AutoGenBuilder().getResponse(task, title)
            if not messages[-1]["content"]:
                del messages[-1]
            # add context to the message chain
            config.currentMessages += messages
            print2("\nAutoGen Agent Builder closed!")
            return ""

        functionSignature = {
            "examples": [
                "autobuilder",
                "create a team of assistants",
                "create a crew of agents",
            ],
            "name": "build_agents",
            "description": "build a group of AI assistants or agents to execute a complicated task that other functions cannot resolve",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Task description in as much detail as possible",
                    },
                    "title": {
                        "type": "string",
                        "description": "A short title to describe the task",
                    },
                },
                "required": ["task", "title"],
            },
        }

        config.addFunctionCall(signature=functionSignature, method=build_agents)
    except:
        print("Plugin `create ai assistants` not enabled! Run `pip install pyautogen[autobuild]` first!")
        pass