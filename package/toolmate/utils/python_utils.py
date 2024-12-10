from toolmate.utils.call_llm import CallLLM

from toolmate import config, getPythonFunctionResponse, fineTunePythonCode, showErrors
from toolmate import print1, extractPythonCode, displayPythonCode
import json
import io, sys
from io import StringIO

class PythonUtil:

    @staticmethod
    def showAndExecutePythonCode(code):
        validCode = extractPythonCode(code)
        if validCode:
            config.stopSpinning()
            if config.developer or config.codeDisplay:
                displayPythonCode(validCode)
            refinedCode = fineTunePythonCode(validCode)
            information = PythonUtil.executePythonCode(refinedCode)
            return information
        return json.dumps({"information": code})

    @staticmethod
    def executePythonCode(code):

        # Create a StringIO object to capture the output
        thisOutput = StringIO()
        # Redirect stdout to the StringIO object
        old_stdout = sys.stdout
        sys.stdout = thisOutput

        try:
            exec(code, globals())
        except:
            # Restore the original stdout
            sys.stdout = old_stdout

            trace = showErrors()
            print1(config.divider)
            if config.max_consecutive_auto_correction > 0:
                return CallLLM.autoCorrectPythonCode(code, trace)
            else:
                return "[INVALID]"

        # Restore the original stdout
        sys.stdout = old_stdout

        pythonFunctionResponse = thisOutput.getvalue()
        if not pythonFunctionResponse.strip():
            pythonFunctionResponse = getPythonFunctionResponse()
        if not pythonFunctionResponse:
            return f"```executed\n{code}\n```"
        return json.dumps({"information": pythonFunctionResponse})
