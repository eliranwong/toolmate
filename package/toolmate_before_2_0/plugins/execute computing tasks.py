"""
ToolMate AI Plugin - execute computing tasks

execute computing tasks

[TOOL_CALL]
"""

from toolmate import config, fineTunePythonCode, showRisk, confirmExecution, getPygmentsStyle, getPromptExecutionMessage
from toolmate import print1
from toolmate.utils.python_utils import PythonUtil
from toolmate.utils.single_prompt import SinglePrompt
import pygments, pprint, json
from pygments.lexers.python import PythonLexer
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import print_formatted_text
from prompt_toolkit.styles import Style

def task(function_args):
    # retrieve argument values from a dictionary
    risk = function_args.get("risk") # required
    title = function_args.get("title") # required
    python_code = function_args.get("code") # required
    refinedCode = fineTunePythonCode(python_code)

    promptStyle = Style.from_dict({
        # User input (default text).
        "": config.terminalCommandEntryColor2,
        # Prompt.
        "indicator": config.terminalPromptIndicatorColor2,
    })

    # show pyton code for developer
    print1(config.divider)
    print1(f"Python: {title}")
    showRisk(risk)
    if config.developer or config.codeDisplay:
        print1("```")
        #print(python_code)
        # pygments python style
        tokens = list(pygments.lex(python_code, lexer=PythonLexer()))
        print_formatted_text(PygmentsTokens(tokens), style=getPygmentsStyle())
        print1("```")
    print1(config.divider)

    config.stopSpinning()
    if not config.runPython:
        return "[INVALID]"
    elif confirmExecution(risk):
        if hasattr(config, "api_server_id"):
            config.toolTextOutput = getPromptExecutionMessage(refinedCode, risk)
            return ""
        print1("Do you want to execute it? [y]es / [N]o")
        confirmation = SinglePrompt.run(style=promptStyle, default="y")
        if not confirmation.lower() in ("y", "yes"):
            config.runPython = False
            return "[INVALID]"
    config.toolTextOutput = PythonUtil.executePythonCode(refinedCode)
    if config.toolTextOutput == "[INVALID]":
        config.toolTextOutput = ""
        return "[INVALID]"
    try:
        pprint.pprint(json.loads(config.toolTextOutput))
    except:
        print(config.toolTextOutput)
    return ""

functionSignature = {
    "examples": [
        "execute computing task",
        "system command",
        "device information",
        "file access",
        "move files",
        "search files",
        "delete files",
        "convert file",
        "open folder",
        "open directory",
    ],
    "name": "task",
    "description": "Execute computing task or gain access to device information",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Generate Python code that integrates any relevant packages to resolve my request",
            },
            "title": {
                "type": "string",
                "description": "Title for the task",
            },
            "risk": {
                "type": "string",
                "description": "Assess the risk level of damaging my device upon executing the task. e.g. file deletions or similar significant impacts are regarded as 'high' level.",
                "enum": ["high", "medium", "low"],
            },
        },
        "required": ["code", "title", "risk"],
    },
}

config.addToolCall(signature=functionSignature, method=task)
