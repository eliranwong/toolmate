from toolmate import config, fineTunePythonCode, displayPythonCode
from toolmate import print1, print2, print3
import traceback
from toolmate import installPipPackage
import io, sys
from io import StringIO

"""
ToolMate AI Plugin - auto correct python code

functionalities:
* install missing packages
* fixed broken codes

User can define the maximum number of auto-correctioning attempts by editing "max_consecutive_auto_correction" in config.py.
The default value of config.max_consecutive_auto_correction is 3.

[TOOL_CALL]
"""

def correct_python_code(function_args):

    # Create a StringIO object to capture the output
    thisOutput = StringIO()
    # Redirect stdout to the StringIO object
    old_stdout = sys.stdout
    sys.stdout = thisOutput

    # get the sql query statement
    issue = function_args.get("issue") # required
    print(f"Issue: {issue}")

    fix = function_args.get("code") # required
    missing = function_args.get("missing_module") # required
    if missing in ("[]", "???"):
        missing = ""

    try:
        if missing:
            try:
                print3(f"Installing missing package: {missing}")
                installPipPackage(f"--upgrade {missing}")
            except:
                print(traceback.format_exc())
        print2("Running improved code ...")
        if config.developer or config.codeDisplay:
            displayPythonCode(fix)
        exec(fineTunePythonCode(fix), globals())

        # Restore the original stdout
        sys.stdout = old_stdout

        return f"[EXECUTED]{thisOutput.getvalue().strip()}"
    except:
        # Restore the original stdout
        sys.stdout = old_stdout

        return traceback.format_exc()

functionSignature = {
    "examples": [
        "fix bug",
        "correct code",
    ],
    "name": "correct_python_code",
    "description": "Fix Python code if both the original code and the traceback error are provided",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Generate an improved version of python code that resolved the traceback error. Return the original code only if traceback shows an import error.",
            },
            "missing_module": {
                "type": "string",
                "description": """The module name identified in ModuleNotFoundError, if any. Return '' if there is no import error in the traceback.""",
            },
            "issue": {
                "type": "string",
                "description": """Briefly explain the error""",
            },
        },
        "required": ["code", "missing_module", "issue"],
    },
}

# configs particular to this plugin
# persistent
persistentConfigs = (
    ("max_consecutive_auto_correction", 5),
)
config.setConfig(persistentConfigs)

config.addFunctionCall(signature=functionSignature, method=correct_python_code)