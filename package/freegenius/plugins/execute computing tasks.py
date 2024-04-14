"""
FreeGenius AI Plugin - execute computing tasks

execute computing tasks

[FUNCTION_CALL]
"""

from freegenius import config, fineTunePythonCode, showRisk, confirmExecution, getPygmentsStyle
from freegenius import print1
from freegenius.utils.python_utils import PythonUtil
from freegenius.utils.single_prompt import SinglePrompt
import pygments, pprint, json
from pygments.lexers.python import PythonLexer
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import print_formatted_text
from prompt_toolkit.styles import Style

def execute_computing_task(function_args):
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
        print1("Do you want to execute it? [y]es / [N]o")
        confirmation = SinglePrompt.run(style=promptStyle, default="y")
        if not confirmation.lower() in ("y", "yes"):
            config.runPython = False
            return "[INVALID]"
    config.tempContent = PythonUtil.executePythonCode(refinedCode)
    try:
        pprint.pprint(json.loads(config.tempContent))
    except:
        print(config.tempContent)
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
    "name": "execute_computing_task",
    "description": "execute computing task or gain access to device information",
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

config.addFunctionCall(signature=functionSignature, method=execute_computing_task)
