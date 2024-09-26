
"""
ToolMate AI Plugin - execute termux command

execute termux command

[TOOL_CALL]
"""

from toolmate import config, showRisk, confirmExecution, getPygmentsStyle, showErrors
from toolmate import print1, runSystemCommand
from toolmate.utils.single_prompt import SinglePrompt
import textwrap, re, pygments, json, pydoc
from pygments.lexers.shell import BashLexer
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import print_formatted_text
from prompt_toolkit.styles import Style


if config.terminalEnableTermuxAPI:
    def execute_termux_command(function_args):
        # retrieve argument values from a dictionary
        risk = function_args.get("risk") # required
        title = function_args.get("title") # required
        #sharedText = function_args.get("message", "") # optional
        function_args = textwrap.dedent(function_args.get("code")).strip() # required
        sharedText = re.sub("^termux-share .*?'([^']+?)'$", r"\1", function_args)
        sharedText = re.sub('^termux-share .*?"([^"]+?)"$', r"\1", sharedText)
        sharedText = re.sub("""^[\d\D]*?subprocess.run\(\['termux-share'[^\[\]]*?'([^']+?)'\]\)[\d\D]*?$""", r"\1", sharedText)
        sharedText = re.sub('''^[\d\D]*?subprocess.run\(\["termux-share"[^\[\]]*?"([^']+?)"\]\)[\d\D]*?$''', r"\1", sharedText)
        function_args = function_args if sharedText == function_args else f'''termux-share -a send "{sharedText}"'''

        promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })

        # show Termux command for developer
        print1(config.divider)
        print1(f"Termux: {title}")
        showRisk(risk)
        if config.developer or config.codeDisplay:
            print1("```")
            #print(function_args)
            tokens = list(pygments.lex(function_args, lexer=BashLexer()))
            print_formatted_text(PygmentsTokens(tokens), style=getPygmentsStyle())
            print1("```")
        print1(config.divider)

        config.stopSpinning()
        if confirmExecution(risk):
            print1("Do you want to execute it? [y]es / [N]o")
            confirmation = SinglePrompt.run(style=promptStyle, default="y")
            if not confirmation.lower() in ("y", "yes"):
                return "[INVALID]"

        try:
            if not sharedText == function_args:
                pydoc.pipepager(sharedText, cmd="termux-share -a send")
                function_response = "Done!"
            else:
                # display both output and error
                function_response = runSystemCommand(function_args)
            print1(function_response)
        except:
            showErrors()
            print1(config.divider)
            return "[INVALID]"
        info = {"information": function_response}
        function_response = json.dumps(info)
        return json.dumps(info)

    functionSignature = {
        "examples": [
            "run Termux command",
            "run on Android",
        ],
        "name": "execute_termux_command",
        "description": "Execute Termux command on Android",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Generate Termux command to resolve my request, e.g. am start -n com.android.chrome/com.google.android.apps.chrome.Main",
                },
                "title": {
                    "type": "string",
                    "description": "title for the termux command",
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

    config.addFunctionCall(signature=functionSignature, method=execute_termux_command)