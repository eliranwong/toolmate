from freegenius.utils.call_gemini import CallGemini
from freegenius.utils.call_ollama import CallOllama
from freegenius.utils.call_llamacpp import CallLlamaCpp
from freegenius.utils.call_chatgpt import CallChatGPT, CallLetMeDoIt

class CallLLM:

    @staticmethod
    def checkCompletion():
        if config.llmBackend == "ollama":
            return CallOllama.checkCompletion()
        elif config.llmBackend == "llamacpp":
            return CallLlamaCpp.checkCompletion()
        elif config.llmBackend == "gemini":
            return CallGemini.checkCompletion()
        elif config.llmBackend == "chatgpt":
            return CallChatGPT.checkCompletion()
        # letmedoit
        return CallLetMeDoIt.checkCompletion()

    @staticmethod
    def autoHealPythonCode(code, trace):
        if config.llmBackend == "ollama":
            return CallOllama.autoHealPythonCode(code, trace)
        elif config.llmBackend == "llamacpp":
            return CallLlamaCpp.autoHealPythonCode(code, trace)
        elif config.llmBackend == "gemini":
            return CallGemini.autoHealPythonCode(code, trace)
        # chatgpt / letmedoit
        return autoHealPythonCode(code, trace)

    @staticmethod
    def runSingleFunctionCall(messages, functionSignatures, function_name):
        if config.llmBackend == "ollama":
            return CallOllama.runSingleFunctionCall(messages, function_name)
        elif config.llmBackend == "llamacpp":
            return CallLlamaCpp.runSingleFunctionCall(messages, function_name)
        elif config.llmBackend == "gemini":
            return CallGemini.runSingleFunctionCall(messages, function_name)
        elif config.llmBackend == "chatgpt":
            return CallChatGPT.runSingleFunctionCall(messages, functionSignatures, function_name)
        # letmedoit
        return CallLetMeDoIt.runSingleFunctionCall(messages, functionSignatures, function_name)

    @staticmethod
    def getSingleChatResponse(userInput, messages=[], temperature=None):
        """
        non-streaming single call
        """
        if config.llmBackend == "ollama":
            return CallOllama.getSingleChatResponse(userInput, messages=messages, temperature=temperature)
        elif config.llmBackend == "llamacpp":
            return CallLlamaCpp.getSingleChatResponse(userInput, messages=messages, temperature=temperature)
        elif config.llmBackend == "gemini":
            history, *_ = CallLLM.toGeminiMessages(messages=messages)
            return CallGemini.getSingleChatResponse(userInput, history=history)
        elif config.llmBackend == "chatgpt":
            return CallChatGPT.getSingleChatResponse(userInput, messages=messages, temperature=temperature)
        # letmedoit
        return CallLetMeDoIt.getSingleChatResponse(userInput, messages=messages, temperature=temperature)

    @staticmethod
    def getSingleFunctionCallResponse(userInput, functionSignatures, function_name, temperature=None):
        messages=[{"role": "user", "content" : userInput}]
        if config.llmBackend == "ollama":
            return CallOllama.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmBackend == "llamacpp":
            return CallLlamaCpp.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmBackend == "gemini":
            return CallGemini.getSingleFunctionCallResponse(messages, function_name)
        elif config.llmBackend == "chatgpt":
            return CallChatGPT.getSingleFunctionCallResponse(messages, functionSignatures, function_name, temperature=temperature)
        # letmedoit
        return CallLetMeDoIt.getSingleFunctionCallResponse(messages, functionSignatures, function_name, temperature=temperature)

    @staticmethod
    def runAutoFunctionCall(messages, noFunctionCall=False):
        if config.llmBackend == "ollama":
            return CallOllama.runAutoFunctionCall(messages, noFunctionCall)
        elif config.llmBackend == "llamacpp":
            return CallLlamaCpp.runAutoFunctionCall(messages, noFunctionCall)
        elif config.llmBackend == "gemini":
            return CallGemini.runAutoFunctionCall(messages, noFunctionCall)
        elif config.llmBackend == "chatgpt":
            return CallChatGPT.runAutoFunctionCall(messages, noFunctionCall)
        # letmedoit
        return CallLetMeDoIt.runAutoFunctionCall(messages, noFunctionCall)
