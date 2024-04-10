from freegenius.utils.call_llm import CallLLM

from freegenius import config, getPythonFunctionResponse, fineTunePythonCode, getPygmentsStyle, showErrors
from freegenius import print1, extractPythonCode
import json, pygments
from pygments.lexers.python import PythonLexer
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import PygmentsTokens


class PythonUtil:

    @staticmethod
    def displayPythonCode(code):
        if config.developer or config.codeDisplay:
            print1("```python")
            tokens = list(pygments.lex(code, lexer=PythonLexer()))
            print_formatted_text(PygmentsTokens(tokens), style=getPygmentsStyle())
            print1("```")

    @staticmethod
    def showAndExecutePythonCode(code):
        code = extractPythonCode(code)
        if code:
            config.stopSpinning()
            PythonUtil.displayPythonCode(code)
            refinedCode = fineTunePythonCode(code)
            information = PythonUtil.executePythonCode(refinedCode)
            return information
        return "[INVALID]"

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
            return ""
        return json.dumps({"information": pythonFunctionResponse})
