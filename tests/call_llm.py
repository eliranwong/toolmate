from freegenius import config
from freegenius.utils.call_chatgpt import CallChatGPT
from freegenius.utils.call_ollama import CallOllama
from freegenius.utils.call_llamacpp import CallLlamaCpp

class CallLLM:

    @staticmethod
    def checkCompletion():
        if config.llmBackend == "ollama":
            return CallOllama.checkCompletion()
        elif config.llmBackend == "llamacpp":
            return CallLlamaCpp.checkCompletion()
        # chatgpt
        return CallChatGPT.checkCompletion()

    @staticmethod
    def runSingleFunctionCall(messages, functionSignatures, function_name):
        if config.llmBackend == "ollama":
            return CallOllama.runSingleFunctionCall(messages, function_name)
        elif config.llmBackend == "llamacpp":
            return CallLlamaCpp.runSingleFunctionCall(messages, function_name)
        # chatgpt
        return CallChatGPT.runSingleFunctionCall(messages, functionSignatures, function_name)

    @staticmethod
    def getSingleChatResponse(userInput, temperature=None):
        """
        non-streaming single call
        """
        if config.llmBackend == "ollama":
            return CallOllama.getSingleChatResponse(userInput, temperature)
        elif config.llmBackend == "llamacpp":
            return CallLlamaCpp.getSingleChatResponse(userInput, temperature)
        # chatgpt
        return CallChatGPT.getSingleChatResponse(userInput, temperature)

    @staticmethod
    def getSingleFunctionCallResponse(userInput, functionSignatures, function_name, temperature=None):
        messages=[{"role": "user", "content" : userInput}]
        if config.llmBackend == "ollama":
            return CallOllama.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmBackend == "llamacpp":
            return CallLlamaCpp.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        # chatgpt
        return CallChatGPT.getSingleFunctionCallResponse(messages, functionSignatures, function_name, temperature=temperature)

    @staticmethod
    def runAutoFunctionCall(messages, noFunctionCall=False):
        if config.llmBackend == "ollama":
            return CallOllama.runAutoFunctionCall(messages, noFunctionCall)
        elif config.llmBackend == "llamacpp":
            return CallLlamaCpp.runAutoFunctionCall(messages, noFunctionCall)
        # chatgpt
        return CallChatGPT.runAutoFunctionCall(messages, noFunctionCall)