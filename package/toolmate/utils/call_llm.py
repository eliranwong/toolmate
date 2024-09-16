from toolmate import config, getDeviceInfo, toGeminiMessages, useChatSystemMessage
from toolmate.utils.call_gemini import CallGemini
from toolmate.utils.call_ollama import CallOllama
from toolmate.utils.call_llamacpp import CallLlamaCpp
from toolmate.utils.call_llamacppserver import CallLlamaCppServer
from toolmate.utils.call_chatgpt import CallChatGPT, CallLetMeDoIt
from toolmate.utils.call_groq import CallGroq
import copy

class CallLLM:

    # reset message when a new chart is started or context is changed
    @staticmethod
    def resetMessages(prompt="") -> list[dict]:
        distro = f" '{config.thisDistro}'" if config.thisDistro else ""
        systemMessage1 = config.systemMessage_tool if config.systemMessage_tool else f'''You’re {config.toolMateAIName}, an advanced AI assistant, capable of both engaging in conversations and executing codes on my {config.thisPlatform} device. When you need to generate code, please make sure your code work on {config.thisPlatform}{distro}. Your functionality expands as I add more plugins to you.
Always remember that you are much more than a text-based AI. You possess both vision and speech capabilities and have direct access to my device operating system, enabling you to execute tasks at my command. Please do not state otherwise.'''

        systemMessage2 = config.systemMessage_tool if config.systemMessage_tool else f'''You’re {config.toolMateAIName}, an advanced AI assistant, capable of both engaging in conversations and executing codes on my device.
I am providing the basic information of my device below in case you need it:
```
{getDeviceInfo()}
```
Please use the current time and date that I have provided above as a reference point for any relative dates and times mentioned in my prompt.
You have all the necessary permissions to execute system commands and Python code on my behalf. Your functionality expands as I add more plugins to you. You respond to my prompts and perform tasks based on your own knowledge, the context I provide, as well as the additional knowledge and capabilities provided by plugins.

When replying to my requests, please follow these steps:
Step 1: Consider our previous conversations, particularly your last response, if any, as the context for these requests.
Step 2: Estimate my intent based on the request and context. The intent can be a code generation task, an executable computing task, a math-solving task, a translation task, or a question answering task.
Step 3: Reply based on the estimated intent.
Remember, do not use function call if it is a translation task.

Always remember that you are much more than a text-based AI. You possess both vision and speech capabilities and have direct access to my device's system, enabling you to execute tasks at my command. Please do not state otherwise.
'''

        systemMessage = systemMessage2 if config.llmInterface in ("chatgpt", "letmedoit") else systemMessage1

        messages = [
            {"role": "system", "content": systemMessage}
        ]
        if prompt:
            messages.append({"role": "user", "content": prompt})
        return messages

    @staticmethod
    def checkCompletion():
        if not config.llmInterface:
            config.llmInterface = "llamacpp"
            config.saveConfig()
        if config.llmInterface == "ollama":
            return CallOllama.checkCompletion()
        elif config.llmInterface == "groq":
            return CallGroq.checkCompletion()
        elif config.llmInterface == "llamacppserver":
            return CallLlamaCppServer.checkCompletion()
        elif config.llmInterface == "llamacpp":
            return CallLlamaCpp.checkCompletion()
        elif config.llmInterface == "gemini":
            return CallGemini.checkCompletion()
        elif config.llmInterface == "chatgpt":
            return CallChatGPT.checkCompletion()
        # letmedoit
        return CallLetMeDoIt.checkCompletion()

    @staticmethod
    def autoCorrectPythonCode(code, trace):
        if config.llmInterface == "ollama":
            return CallOllama.autoCorrectPythonCode(code, trace)
        elif config.llmInterface == "groq":
            return CallGroq.autoCorrectPythonCode(code, trace)
        elif config.llmInterface == "llamacppserver":
            return CallLlamaCppServer.autoCorrectPythonCode(code, trace)
        elif config.llmInterface == "llamacpp":
            return CallLlamaCpp.autoCorrectPythonCode(code, trace)
        elif config.llmInterface == "gemini":
            return CallGemini.autoCorrectPythonCode(code, trace)
        elif config.llmInterface == "chatgpt":
            return CallChatGPT.autoCorrectPythonCode(code, trace)
        # letmedoit
        return CallLetMeDoIt.autoCorrectPythonCode(code, trace)

    @staticmethod
    def runSingleFunctionCall(messages, function_name):
        if config.llmInterface == "ollama":
            return CallOllama.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "groq":
            return CallGroq.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "llamacppserver":
            return CallLlamaCppServer.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "llamacpp":
            return CallLlamaCpp.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "gemini":
            return CallGemini.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "chatgpt":
            return CallChatGPT.runSingleFunctionCall(messages, function_name)
        # letmedoit
        return CallLetMeDoIt.runSingleFunctionCall(messages, function_name)

    @staticmethod
    def regularCall(messages: dict):
        chatMessages = useChatSystemMessage(copy.deepcopy(messages))
        if config.llmInterface == "ollama":
            return CallOllama.regularCall(chatMessages)
        elif config.llmInterface == "groq":
            return CallGroq.regularCall(chatMessages)
        elif config.llmInterface == "llamacppserver":
            return CallLlamaCppServer.regularCall(chatMessages)
        elif config.llmInterface == "llamacpp":
            return CallLlamaCpp.regularCall(chatMessages)
        elif config.llmInterface == "gemini":
            return CallGemini.regularCall(chatMessages)
        return CallChatGPT.regularCall(chatMessages)

    @staticmethod
    def getSingleChatResponse(userInput, messages=[], temperature=None):
        """
        non-streaming single call
        """
        chatMessages = useChatSystemMessage(copy.deepcopy(messages))
        if config.llmInterface == "ollama":
            return CallOllama.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature)
        elif config.llmInterface == "groq":
            return CallGroq.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature)
        elif config.llmInterface == "llamacppserver":
            return CallLlamaCppServer.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature)
        elif config.llmInterface == "llamacpp":
            return CallLlamaCpp.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature)
        elif config.llmInterface == "gemini":
            history, *_ = toGeminiMessages(messages=chatMessages)
            return CallGemini.getSingleChatResponse(userInput, history=history)
        elif config.llmInterface == "chatgpt":
            return CallChatGPT.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature)
        # letmedoit
        return CallLetMeDoIt.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature)

    @staticmethod
    def getSingleFunctionCallResponse(messages, function_name, temperature=None):
        if isinstance(messages, str):
            messages = [{"role": "user", "content" : messages}]
        if config.llmInterface == "ollama":
            return CallOllama.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmInterface == "groq":
            return CallGroq.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmInterface == "llamacppserver":
            return CallLlamaCppServer.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmInterface == "llamacpp":
            return CallLlamaCpp.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmInterface == "gemini":
            return CallGemini.getSingleFunctionCallResponse(messages, function_name)
        elif config.llmInterface == "chatgpt":
            return CallChatGPT.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        # letmedoit
        return CallLetMeDoIt.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)

    @staticmethod
    def runGeniusCall(messages, doNotUseTool=False):
        if config.llmInterface == "ollama":
            return CallOllama.runGeniusCall(messages, doNotUseTool)
        elif config.llmInterface == "groq":
            return CallGroq.runGeniusCall(messages, doNotUseTool)
        elif config.llmInterface == "llamacppserver":
            return CallLlamaCppServer.runGeniusCall(messages, doNotUseTool)
        elif config.llmInterface == "llamacpp":
            return CallLlamaCpp.runGeniusCall(messages, doNotUseTool)
        elif config.llmInterface == "gemini":
            return CallGemini.runGeniusCall(messages, doNotUseTool)
        elif config.llmInterface == "chatgpt":
            return CallChatGPT.runGeniusCall(messages, doNotUseTool)
        # letmedoit
        return CallLetMeDoIt.runGeniusCall(messages, doNotUseTool)
