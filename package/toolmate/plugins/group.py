"""
ToolMate AI Plugin - group

build a group of agents, with integrated "AutoGen Agent Builder", to discuss and resolve a query
For task execution or coding purpose, use tool 'agents' instead.

[TOOL_CALL]
"""

from toolmate import config

if not config.isLite and config.online:
    from toolmate.autobuild import AutoGenBuilder
    from toolmate import print2, print3
    import re

    def group(function_args):
        config.stopSpinning()
        if function_args:
            task = function_args.get("query") # required
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
            if content is None:
                content = "Calling tools ..." if "tool_calls" in i else "..."
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
            "group chat",
        ],
        "name": "group",
        "description": "create a group of AI agents to discuss and resolve a query",
        "parameters": {
            "type": "object",
            "properties": {} if not config.tool_selection_agent else {
                "query": {
                    "type": "string",
                    "description": "Query description in as much detail as possible",
                },
                "title": {
                    "type": "string",
                    "description": "A short title to describe the query",
                },
            },
            "required": [] if not config.tool_selection_agent else ["query"],
        },
    }

    config.addFunctionCall(signature=functionSignature, method=group)