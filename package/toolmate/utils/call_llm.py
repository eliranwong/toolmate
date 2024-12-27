from typing import Optional
from toolmate import config, getDeviceInfo, toGeminiMessages, useChatSystemMessage
from toolmate.utils.call_ollama import CallOllama
from toolmate.utils.call_groq import CallGroq
from toolmate.utils.call_mistral import CallMistral
from toolmate.utils.call_googleai import CallGoogleAI
from toolmate.utils.call_xai import CallXAI
from toolmate.utils.call_openai_azure import CallOpenAIAzure
from toolmate.utils.call_openai_github import CallOpenAIGithub
from toolmate.utils.call_anthropic import CallAnthropic
from toolmate.utils.call_openai import CallOpenAI, CallLetMeDoIt
from toolmate.utils.call_llamacppserver import CallLlamaCppServer
import copy
if not config.isLite:
    try:
        from toolmate.utils.call_llamacpp import CallLlamaCpp
    except:
        pass
    from toolmate.utils.call_vertexai import CallVertexAI
    from toolmate.utils.call_genai import CallGenAI

class CallLLM:

    # reset message when a new chart is started or context is changed
    @staticmethod
    def resetMessages(prompt="") -> list[dict]:
        # upload Ollama model
        if config.llmInterface == "ollama":
            CallOllama.unloadModels()
        #elif config.llmInterface == "llamacpppython":
        #    CallLlamaCpp.unloadModels()

        if config.systemMessage_tool:
            # Custom Tool System Message
            config.systemMessage_tool_current = config.systemMessage_tool
        
        elif config.llmInterface in ("openai", "letmedoit", "azure", "github"):

            config.systemMessage_tool_current = f'''You’re {config.toolMateAIName}, an advanced AI assistant, capable of both engaging in conversations and executing codes on my device.
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

        else:

            # other backends
            distro = f" '{config.thisDistro}'" if config.thisDistro else ""
            config.systemMessage_tool_current = f'''You’re {config.toolMateAIName}, an advanced AI assistant, capable of both engaging in conversations and executing codes on my {config.thisPlatform} device. When you need to generate code, please make sure your code work on {config.thisPlatform}{distro}. Your functionality expands as I add more plugins to you.
Always remember that you are much more than a text-based AI. You possess both vision and speech capabilities and have direct access to my device operating system, enabling you to execute tasks at my command. Please do not state otherwise.'''

        messages = [
            {"role": "system", "content": config.systemMessage_tool_current}
        ]
        if prompt:
            messages.append({"role": "user", "content": prompt})
        return messages

    @staticmethod
    def checkCompletion(llmInterface=""):
        if not config.llmInterface:
            config.llmInterface = "llamacpppython"
            config.saveConfig()
        if not llmInterface:
            llmInterface = config.llmInterface
        if llmInterface == "ollama":
            return CallOllama.checkCompletion()
        elif llmInterface == "groq":
            return CallGroq.checkCompletion()
        elif llmInterface == "mistral":
            return CallMistral.checkCompletion()
        elif llmInterface == "llamacppserver":
            return CallLlamaCppServer.checkCompletion()
        elif llmInterface == "llamacpppython":
            return CallLlamaCpp.checkCompletion()
        elif llmInterface == "vertexai":
            return CallVertexAI.checkCompletion()
        elif llmInterface == "googleai":
            return CallGoogleAI.checkCompletion()
        elif llmInterface == "genai":
            return CallGenAI.checkCompletion()
        elif llmInterface == "xai":
            return CallXAI.checkCompletion()
        elif llmInterface == "openai":
            return CallOpenAI.checkCompletion()
        elif llmInterface == "azure":
            return CallOpenAIAzure.checkCompletion()
        elif llmInterface == "github":
            return CallOpenAIGithub.checkCompletion()
        elif llmInterface == "anthropic":
            return CallAnthropic.checkCompletion()
        # letmedoit
        return CallLetMeDoIt.checkCompletion()

    @staticmethod
    def autoCorrectPythonCode(code, trace):
        llmInterface = config.autoCorrectionInterface if config.autoCorrectionInterface else config.llmInterface
        if llmInterface == "ollama":
            return CallOllama.autoCorrectPythonCode(code, trace)
        elif llmInterface == "groq":
            return CallGroq.autoCorrectPythonCode(code, trace)
        elif llmInterface == "mistral":
            return CallMistral.autoCorrectPythonCode(code, trace)
        elif llmInterface == "llamacppserver":
            return CallLlamaCppServer.autoCorrectPythonCode(code, trace)
        elif llmInterface == "llamacpppython":
            return CallLlamaCpp.autoCorrectPythonCode(code, trace)
        elif llmInterface == "vertexai":
            return CallVertexAI.autoCorrectPythonCode(code, trace)
        elif llmInterface == "googleai":
            return CallGoogleAI.autoCorrectPythonCode(code, trace)
        elif llmInterface == "genai":
            return CallGenAI.autoCorrectPythonCode(code, trace)
        elif llmInterface == "xai":
            return CallXAI.autoCorrectPythonCode(code, trace)
        elif llmInterface == "openai":
            return CallOpenAI.autoCorrectPythonCode(code, trace)
        elif llmInterface == "azure":
            return CallOpenAIAzure.autoCorrectPythonCode(code, trace)
        elif llmInterface == "github":
            return CallOpenAIGithub.autoCorrectPythonCode(code, trace)
        elif llmInterface == "anthropic":
            return CallAnthropic.autoCorrectPythonCode(code, trace)
        # letmedoit
        return CallLetMeDoIt.autoCorrectPythonCode(code, trace)

    @staticmethod
    def runSingleFunctionCall(messages, function_name):
        if config.llmInterface == "ollama":
            return CallOllama.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "groq":
            return CallGroq.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "mistral":
            return CallMistral.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "llamacppserver":
            return CallLlamaCppServer.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "llamacpppython":
            return CallLlamaCpp.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "vertexai":
            return CallVertexAI.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "googleai":
            return CallGoogleAI.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "genai":
            return CallGenAI.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "xai":
            return CallXAI.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "openai":
            return CallOpenAI.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "azure":
            return CallOpenAIAzure.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "github":
            return CallOpenAIGithub.runSingleFunctionCall(messages, function_name)
        elif config.llmInterface == "anthropic":
            return CallAnthropic.runSingleFunctionCall(messages, function_name)
        # letmedoit
        return CallLetMeDoIt.runSingleFunctionCall(messages, function_name)

    @staticmethod
    def regularCall(messages: dict):
        chatMessages = useChatSystemMessage(copy.deepcopy(messages))
        if config.llmInterface == "ollama":
            return CallOllama.regularCall(chatMessages)
        elif config.llmInterface == "groq":
            return CallGroq.regularCall(chatMessages)
        elif config.llmInterface == "mistral":
            return CallMistral.regularCall(chatMessages)
        elif config.llmInterface == "llamacppserver":
            return CallLlamaCppServer.regularCall(chatMessages)
        elif config.llmInterface == "llamacpppython":
            return CallLlamaCpp.regularCall(chatMessages)
        elif config.llmInterface == "vertexai":
            return CallVertexAI.regularCall(chatMessages)
        elif config.llmInterface == "googleai":
            return CallGoogleAI.regularCall(chatMessages)
        elif config.llmInterface == "genai":
            return CallGenAI.regularCall(chatMessages)
        elif config.llmInterface == "xai":
            return CallXAI.regularCall(chatMessages)
        return CallOpenAI.regularCall(chatMessages)

    @staticmethod
    def getSingleChatResponse(userInput, messages=[], temperature=None, prefill: Optional[str]=None, stop: Optional[list]=[], keepSystemMessage: bool=False):
        """
        non-streaming single call
        """
        chatMessages = copy.deepcopy(messages) if keepSystemMessage else useChatSystemMessage(copy.deepcopy(messages))
        if config.llmInterface == "ollama":
            return CallOllama.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature, prefill=prefill, stop=stop, keepSystemMessage=keepSystemMessage)
        elif config.llmInterface == "groq":
            return CallGroq.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature, prefill=prefill, stop=stop, keepSystemMessage=keepSystemMessage)
        elif config.llmInterface == "mistral":
            return CallMistral.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature, prefill=prefill, stop=stop, keepSystemMessage=keepSystemMessage)
        elif config.llmInterface == "googleai":
            return CallGoogleAI.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature, keepSystemMessage=keepSystemMessage)
        elif config.llmInterface == "genai":
            return CallGenAI.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature, keepSystemMessage=keepSystemMessage)
        elif config.llmInterface == "xai":
            return CallXAI.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature, keepSystemMessage=keepSystemMessage)
        elif config.llmInterface == "llamacppserver":
            return CallLlamaCppServer.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature, keepSystemMessage=keepSystemMessage)
        elif config.llmInterface == "llamacpppython":
            return CallLlamaCpp.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature, keepSystemMessage=keepSystemMessage)
        elif config.llmInterface == "vertexai":
            history, systemMessage, lastUserMessage = toGeminiMessages(messages=chatMessages)
            if userInput.strip() and systemMessage:
                userInput = f"""# Your role\n\n{systemMessage}\n\n# My Inquiry\n\n{userInput}"""
            elif not userInput.strip() and lastUserMessage.strip() and systemMessage:
                userInput = f"""# Your role\n\n{systemMessage}\n\n# My Inquiry\n\n{lastUserMessage}"""
            elif not userInput.strip() and lastUserMessage.strip():
                userInput = lastUserMessage
            return CallVertexAI.getSingleChatResponse(userInput, history=history)
            #history, *_ = toGeminiMessages(messages=chatMessages)
            #return CallVertexAI.getSingleChatResponse(userInput, history=history)
        elif config.llmInterface == "openai":
            return CallOpenAI.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature, keepSystemMessage=keepSystemMessage)
        elif config.llmInterface == "azure":
            return CallOpenAIAzure.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature, keepSystemMessage=keepSystemMessage)
        elif config.llmInterface == "github":
            return CallOpenAIGithub.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature, keepSystemMessage=keepSystemMessage)
        elif config.llmInterface == "anthropic":
            return CallAnthropic.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature, keepSystemMessage=keepSystemMessage)
        # letmedoit
        return CallLetMeDoIt.getSingleChatResponse(userInput, messages=chatMessages, temperature=temperature, keepSystemMessage=keepSystemMessage)

    @staticmethod
    def getSingleFunctionCallResponse(messages, function_name, temperature=None):
        if isinstance(messages, str):
            messages = [{"role": "user", "content" : messages}]
        if config.llmInterface == "ollama":
            return CallOllama.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmInterface == "groq":
            return CallGroq.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmInterface == "mistral":
            return CallMistral.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmInterface == "llamacppserver":
            return CallLlamaCppServer.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmInterface == "llamacpppython":
            return CallLlamaCpp.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmInterface == "vertexai":
            return CallVertexAI.getSingleFunctionCallResponse(messages, function_name)
        elif config.llmInterface == "googleai":
            return CallGoogleAI.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmInterface == "genai":
            return CallGenAI.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmInterface == "xai":
            return CallXAI.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmInterface == "openai":
            return CallOpenAI.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmInterface == "azure":
            return CallOpenAIAzure.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmInterface == "github":
            return CallOpenAIGithub.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        elif config.llmInterface == "anthropic":
            return CallAnthropic.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)
        # letmedoit
        return CallLetMeDoIt.getSingleFunctionCallResponse(messages, function_name, temperature=temperature)

    @staticmethod
    def runToolCall(messages):
        if config.llmInterface == "ollama":
            return CallOllama.runToolCall(messages)
        elif config.llmInterface == "groq":
            return CallGroq.runToolCall(messages)
        elif config.llmInterface == "mistral":
            return CallMistral.runToolCall(messages)
        elif config.llmInterface == "llamacppserver":
            return CallLlamaCppServer.runToolCall(messages)
        elif config.llmInterface == "llamacpppython":
            return CallLlamaCpp.runToolCall(messages)
        elif config.llmInterface == "vertexai":
            return CallVertexAI.runToolCall(messages)
        elif config.llmInterface == "googleai":
            return CallGoogleAI.runToolCall(messages)
        elif config.llmInterface == "genai":
            return CallGenAI.runToolCall(messages)
        elif config.llmInterface == "xai":
            return CallXAI.runToolCall(messages)
        elif config.llmInterface == "openai":
            return CallOpenAI.runToolCall(messages)
        elif config.llmInterface == "azure":
            return CallOpenAIAzure.runToolCall(messages)
        elif config.llmInterface == "github":
            return CallOpenAIGithub.runToolCall(messages)
        elif config.llmInterface == "anthropic":
            return CallAnthropic.runToolCall(messages)
        # letmedoit
        return CallLetMeDoIt.runToolCall(messages)
