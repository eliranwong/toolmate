"""
ToolMate AI Plugin - group

build a group of agents, with integrated "AutoGen Agent Builder", to discuss and resolve a query
For task execution or coding purpose, use tool 'agents' instead.

[TOOL_CALL]
"""

from toolmate import config

if not config.isLite and config.online:
    from toolmate.autocaptain import AutoCaptainAgent
    from toolmate import print2, print3
    import re

    def captain(function_args):
        config.stopSpinning()
        if function_args:
            task = function_args.get("task") # required
        else:
            task = config.currentMessages[-1]["content"]
        print2("AutoGen Captain Agent launched!")
        print3(f"Description: {task}")
        messages = AutoCaptainAgent().getResponse(task)
        # check last message
        theLastMessage = messages[-1].get("content", "").strip()
        if not theLastMessage or theLastMessage == "TERMINATE":
            del messages[-1]
        # add context to the message chain
        #config.currentMessages += messages
        for index, i in enumerate(messages):
            content = i.get("content", "")
            if content is None:
                content = "Calling tools ..." if "tool_calls" in i else "..."
            name = i.get("name", "")
            #if index == 0: # if you want to include device information
            #    config.currentMessages[-1]["content"] = content
            if index > 1:
                config.currentMessages.append({"role": "user", "content": f"Next speaker: {name}"})
            if index > 0:
                content = re.sub("TERMINATE$", "", content.rstrip()).rstrip()
                config.currentMessages.append({"role": "assistant", "content": f"(Speaker) {name}: {content}"})
        print2("\nAutoGen Captain Agent closed!")
        return ""

    functionSignature = {
        "examples": [
            "ask captain agent",
        ],
        "name": "captain",
        "description": "Use AutoGen Captain Agent and its tool libraries to resolve user's request",
        "parameters": {
            "type": "object",
            "properties": {} if not config.tool_selection_agent else {
                "task": {
                    "type": "string",
                    "description": "Task description in as much detail as possible",
                },
            },
            "required": [] if not config.tool_selection_agent else ["task"],
        },
    }

    config.addToolCall(signature=functionSignature, method=captain)