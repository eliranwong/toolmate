"""
ToolMate AI Plugin - share

share text or previous generated result on Android

[TOOL_CALL]
"""

if config.isTermux:

    from toolmate import config, stopSpinning
    import pydoc

    def share(function_args):
        content = config.currentMessages[-1]["content"]
        config.stopSpinning()
        pydoc.pipepager(content, cmd="termux-share -a send")
        return ""

    functionSignature = {
        "examples": [],
        "name": "share",
        "description": f'''Share text or previous generated result with other apps''',
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }

    config.addFunctionCall(signature=functionSignature, method=share)