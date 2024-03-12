from freegenius import config
import traceback
from freegenius.utils.install import installmodule
from freegenius.utils.shared_utils import SharedUtil

"""
LetMeDoIt AI Plugin - auto heal python code

functionalities:
* install missing packages
* fixed broken codes

User can define the maximum number of auto-healing attempts by editing "max_consecutive_auto_heal" in config.py.
The default value of config.max_consecutive_auto_heal is 3.

[FUNCTION_CALL]
"""

def heal_python(function_args):
    # get the sql query statement
    issue = function_args.get("issue") # required
    config.print3(f"Issue: {issue}")

    fix = function_args.get("fix") # required
    missing = function_args.get("missing") # required
    if isinstance(missing, str):
        missing = eval(missing)

    try:
        if missing:
            config.print2("Installing missing packages ...")
            for i in missing:
                installmodule(f"--upgrade {i}")
        config.print2("Running improved code ...")
        if config.developer or config.codeDisplay:
            SharedUtil.displayPythonCode(fix)
        exec(SharedUtil.fineTunePythonCode(fix), globals())
        return "EXECUTED"
    except:
        return traceback.format_exc()

functionSignature = {
    "intent": [
        "generate code",
    ],
    "examples": [
        "Fix python code",
    ],
    "name": "heal_python",
    "description": "Fix python code if both original code and traceback error are provided",
    "parameters": {
        "type": "object",
        "properties": {
            "fix": {
                "type": "string",
                "description": "Improved version of python code that resolved the traceback error. Return the original code instead only if traceback shows an import error.",
            },
            "missing": {
                "type": "string",
                "description": """List of missing packages identified from import errors, e.g. "['datetime', 'requests']". Return "[]" if there is no import error in the traceback.""",
            },
            "issue": {
                "type": "string",
                "description": """Briefly explain the error""",
            },
        },
        "required": ["fix", "missing", "issue"],
    },
}

# configs particular to this plugin
# persistent
persistentConfigs = (
    ("max_consecutive_auto_heal", 5),
)
config.setConfig(persistentConfigs)

config.addFunctionCall(signature=functionSignature, method=heal_python)