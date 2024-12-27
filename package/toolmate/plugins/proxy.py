"""
ToolMate AI Plugin - group

build a group of agents, with integrated "AutoGen Agent Builder", to discuss and resolve a query
For task execution or coding purpose, use tool 'agents' instead.

[TOOL_CALL]
"""

from toolmate import config

if not config.isLite and config.online:
    from toolmate.autoassist import AutoGenAssistant
    from toolmate import print2, print3
    import re

    def proxy(function_args):
        config.stopSpinning()
        if function_args:
            task = function_args.get("task") # required
        else:
            task = config.currentMessages[-1]["content"]
        print2("AutoGen Assistant Agent launched!")
        print3(f"Description: {task}")
        messages = AutoGenAssistant().getResponse(task, auto=True)
        # check last message
        theLastMessage = messages[-1].get("content", "").strip()
        if not theLastMessage or theLastMessage == "TERMINATE":
            del messages[-1]
        # add context to the message chain
        #config.currentMessages += messages
        for index, i in enumerate(messages):
            content = i.get("content", "")
            name = i.get("name", "")
            #if index == 0: # if you want to include device information
            #    config.currentMessages[-1]["content"] = content
            if index > 1:
                config.currentMessages.append({"role": "user", "content": f"Next speaker: {name}"})
            if index > 0:
                content = re.sub("TERMINATE$", "", content.rstrip()).rstrip()
                config.currentMessages.append({"role": "assistant", "content": f"(Speaker) {name}: {content}"})
        print2("\nAutoGen Assistant Agent closed!")
        return ""

    functionSignature = {
        "examples": [
            "execute a code",
        ],
        "name": "proxy",
        "description": "use an AutoGen assistant and AutoGen code executor to fulfill a task",
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

    config.addToolCall(signature=functionSignature, method=proxy)