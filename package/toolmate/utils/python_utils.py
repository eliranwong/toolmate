from toolmate.utils.call_llm import CallLLM

from toolmate import config, getPythonFunctionResponse, fineTunePythonCode, showErrors
from toolmate import print1, extractPythonCode, displayPythonCode
import json


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
        try:
            exec(code, globals())
            pythonFunctionResponse = getPythonFunctionResponse(code)
        except:
            trace = showErrors()
            print1(config.divider)
            if config.max_consecutive_auto_correction > 0:
                return CallLLM.autoCorrectPythonCode(code, trace)
            else:
                return "[INVALID]"
        if not pythonFunctionResponse:
            return f"```executed\n{code}\n```"
        return json.dumps({"information": pythonFunctionResponse})
