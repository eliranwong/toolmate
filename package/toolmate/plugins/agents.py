"""
ToolMate AI Plugin - build agents

build a group of agents to execute a task with integrated "AutoGen Agent Builder"

[TOOL_CALL]
"""

from toolmate import config

if not config.isLite and config.online:
    try:
        from toolmate.autobuild import AutoGenBuilder
        from toolmate import print2, print3
        import re

        def agents(function_args):
            config.stopSpinning()
            if function_args:
                task = function_args.get("task") # required
                title = function_args.get("title", "") # optional
            else:
                task = config.currentMessages[-1]["content"]
                title = ""
            print2("AutoGen Agent Builder launched!")
            if title:
                print3(f"Title: {title}")
            print3(f"Description: {task}")
            messages = AutoGenBuilder().getResponse(task, title)
            # check last message
            theLastMessage = messages[-1].get("content", "").strip()
            if not theLastMessage or theLastMessage == "TERMINATE":
                del messages[-1]
            # add context to the message chain
            #config.currentMessages += messages
            for index, i in enumerate(messages):
                content = i.get("content", "")
                if index == len(messages) - 1:
                    content = re.sub("TERMINATE$", "", content.rstrip()).rstrip()
                name = i.get("name", "")
                if index == 0:
                    config.currentMessages[-1]["content"] = content
                elif index > 1:
                    config.currentMessages.append({"role": "user", "content": f"Next speaker: {name}"})
                if index > 0:
                    config.currentMessages.append({"role": "assistant", "content": f"(Speaker) {name}: {content}"})
            print2("\nAutoGen Agent Builder closed!")
            return ""

        functionSignature = {
            "examples": [
                "autobuilder",
                "create a team of assistants",
                "create a crew of agents",
            ],
            "name": "agents",
            "description": "create a group of AI agents to execute a complicated task that other functions cannot resolve",
            "parameters": {
                "type": "object",
                "properties": {} if not config.tool_selection_agent else {
                    "task": {
                        "type": "string",
                        "description": "Task description in as much detail as possible",
                    },
                    "title": {
                        "type": "string",
                        "description": "A short title to describe the task",
                    },
                },
                "required": [] if not config.tool_selection_agent else ["task"],
            },
        }

        config.addFunctionCall(signature=functionSignature, method=agents)
    except:
        print("Plugin `create agents` not enabled! Run `pip install autogen[autobuild]` first!")