from freegenius import config, fineTunePythonCode
from freegenius import print1, print2, print3
import traceback
from freegenius import installPipPackage
from freegenius.utils.shared_utils import SharedUtil

"""
FreeGenius AI Plugin - auto correct python code

functionalities:
* install missing packages
* fixed broken codes

User can define the maximum number of auto-correctioning attempts by editing "max_consecutive_auto_correction" in config.py.
The default value of config.max_consecutive_auto_correction is 3.

[FUNCTION_CALL]
"""

def correct_python(function_args):
    # get the sql query statement
    issue = function_args.get("issue") # required
    print(f"Issue: {issue}")

    fix = function_args.get("code") # required
    missing = function_args.get("missing_modules") # required

    try:
        if missing:
            try:
                if isinstance(missing, str):
                    missing = eval(missing)
            except:
                missing = [missing]
            print2("Installing missing packages ...")
            for i in missing:
                installPipPackage(f"--upgrade {i}")
        print2("Running improved code ...")
        if config.developer or config.codeDisplay:
            SharedUtil.displayPythonCode(fix)
        exec(fineTunePythonCode(fix), globals())
        return "EXECUTED"
    except:
        return traceback.format_exc()

functionSignature = {
    "examples": [
        "fix bug",
        "correct code",
    ],
    "name": "correct_python",
    "description": "Fix python code if both original code and traceback error are provided",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Improved version of python code that resolved the traceback error. Return the original code instead only if traceback shows an import error.",
            },
            "missing_modules": {
                "type": "string",
                "description": """List of missing packages identified from import errors, e.g. "['datetime', 'requests']". Return "[]" if there is no import error in the traceback.""",
            },
            "issue": {
                "type": "string",
                "description": """Briefly explain the error""",
            },
        },
        "required": ["code", "missing_modules", "issue"],
    },
}

# configs particular to this plugin
# persistent
persistentConfigs = (
    ("max_consecutive_auto_correction", 5),
)
config.setConfig(persistentConfigs)

config.addFunctionCall(signature=functionSignature, method=correct_python)