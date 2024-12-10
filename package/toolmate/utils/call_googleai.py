from toolmate import showErrors, showRisk, executeToolFunction, getPythonFunctionResponse, getPygmentsStyle, fineTunePythonCode, confirmExecution, useChatSystemMessage, getRagPrompt
from toolmate import config
from toolmate import print1, print2, print3, validParameters, getGoogleGenAIClient, refineToolTextOutput
import re, traceback, pprint, copy, textwrap, json, pygments, codecs
from pygments.lexers.python import PythonLexer
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import prompt
from typing import Optional


def check_errors(func):
    def wrapper(*args, **kwargs):
        def finishError():
            config.stopSpinning()
            return "[INVALID]"
        try:
            return func(*args, **kwargs)
        except:
            print(traceback.format_exc())
            return finishError()
    return wrapper

@check_errors
def checkCompletion():
    getGoogleGenAIClient().chat.completions.create(
        model="gemini-1.5-flash-8b",
        messages=[{"role": "user", "content" : "hello"}],
        n=1,
        max_tokens=10,
    )

@check_errors
def riskAssessment(code):
    content = f"""You are a senior python engineer.
Assess the risk level of damaging my device upon executing the python code that I will provide for you.
Answer me either 'high', 'medium' or 'low', without giving me any extra information.
e.g. file deletions or similar significant impacts are regarded as 'high' level.
Acess the risk level of this Python code:
```
{code}
```"""
    try:
        answer = getSingleChatResponse(content, temperature=0.0, keepSystemMessage=True)
        if not answer:
            answer = "high"
        answer = re.sub("[^A-Za-z]", "", answer).lower()
        if not answer in ("high", "medium", "low"):
            answer = "high"
        return answer
    except:
        return "high"

@check_errors
def autoCorrectPythonCode(code, trace):
    for i in range(config.max_consecutive_auto_correction):
        userInput = f"Original python code:\n```\n{code}\n```\n\nTraceback:\n```\n{trace}\n```"
        messages = [{"role": "user", "content" : userInput}]
        print3(f"Auto-correction attempt: {(i + 1)}")
        function_call_message, function_call_response = CallGoogleAI.getSingleFunctionCallResponse(messages, "correct_python_code")
        code = json.loads(function_call_message["function_call"]["arguments"]).get("code")
        # display response
        print1(config.divider)
        if config.developer:
            print(function_call_response)
        else:
            print1("Executed!" if function_call_response.startswith("[EXECUTED]") else "Failed!")
        if function_call_response.startswith("[EXECUTED]"):
            break
        else:
            trace = function_call_response
        print1(config.divider)
    # return information if any
    if function_call_response.startswith("[EXECUTED]"):
        pythonFunctionResponse = function_call_response[10:]
        if not pythonFunctionResponse:
            pythonFunctionResponse = getPythonFunctionResponse()
        if pythonFunctionResponse:
            return json.dumps({"information": pythonFunctionResponse})
        else:
            return f"```executed\n{code}\n```"
    if hasattr(config, "api_server_id"):
        return "[INVALID]"
    # ask if user want to manually edit the code
    print1(f"Failed to execute the code {(config.max_consecutive_auto_correction + 1)} times in a row!")
    print1("Do you want to manually edit it? [y]es / [N]o")
    confirmation = prompt(style=config.promptStyle2, default="N")
    if confirmation.lower() in ("y", "yes"):
        config.defaultEntry = f"```python\n{code}\n```"
        return ""
    else:
        return "[INVALID]"

def convertFunctionSignaturesIntoTools(functionSignatures):
    return [{"type": "function", "function": functionSignature} for functionSignature in functionSignatures]

def getToolArgumentsFromStreams(completion):
    toolArguments = {}
    for event in completion:
        delta = event.choices[0].delta
        if delta and delta.tool_calls:
            for tool_call in delta.tool_calls:
                # handle functions
                if tool_call.function:
                    func_index = tool_call.index
                    if func_index in toolArguments:
                        toolArguments[func_index] += tool_call.function.arguments
                    else:
                        toolArguments[func_index] = tool_call.function.arguments
                # may support non functions later
    return toolArguments

@check_errors
def getSingleChatResponse(userInput, messages=[], temperature=None, prefill: Optional[str]=None, stop: Optional[list]=None, keepSystemMessage: bool=False):
    """
    non-streaming single call
    """
    if userInput:
        item = {"role": "user", "content" : userInput}
        if messages and messages[-1].get("role", "") == "assistant":
            messages.insert(-1, item)
        else:
            messages.append(item)
    chatMessages = copy.deepcopy(messages) if keepSystemMessage else useChatSystemMessage(copy.deepcopy(messages))
    if prefill is not None:
            chatMessages.append({'role': 'assistant', 'content': prefill})
    try:
        completion = getGoogleGenAIClient().chat.completions.create(
            model=config.googleaiApi_tool_model,
            messages=chatMessages,
            n=1,
            temperature=temperature if temperature is not None else config.llmTemperature,
            max_tokens=config.googleaiApi_tool_model_max_tokens,
            stop=stop if stop else None,
        )
        return completion.choices[0].message.content
    except:
        return ""

def runSingleFunctionCall(messages, function_name):
    messagesCopy = copy.deepcopy(messages)
    try:
        _, function_call_response = getSingleFunctionCallResponse(messages, function_name)
        function_call_response = function_call_response if function_call_response else config.toolTextOutput
        messages[-1]["content"] += f"""\n\nAvailable information:\n{function_call_response}"""
        config.toolTextOutput = ""
    except:
        showErrors()
        return messagesCopy
    return messages

@check_errors
def getSingleFunctionCallResponse(messages: list[dict], function_name: str, temperature=None, **kwargs):
    functionSignatures = [config.toolFunctionSchemas[function_name]]
    completion = getGoogleGenAIClient().chat.completions.create(
        model=config.googleaiApi_tool_model,
        messages=messages,
        n=1,
        temperature=temperature if temperature is not None else config.llmTemperature,
        max_tokens=config.googleaiApi_tool_model_max_tokens,
        tools=convertFunctionSignaturesIntoTools(functionSignatures),
        tool_choice={"type": "function", "function": {"name": function_name}},
        stream=False,
        **kwargs,
    )
    function_call_message = completion.choices[0].message
    tool_call = function_call_message.tool_calls[0]
    func_arguments = tool_call.function.arguments
    codecs.decode(func_arguments, "unicode_escape")
    function_call_message_mini = {
        "role": "assistant",
        "content": "",
        "function_call": {
            "name": tool_call.function.name,
            "arguments": func_arguments,
        }
    }
    function_call_response = CallGoogleAI.finetuneSingleFunctionCallResponse(func_arguments, function_name)
    return function_call_message_mini, function_call_response

def finetuneSingleFunctionCallResponse(func_arguments, function_name):
    def notifyDeveloper(func_name):
        if config.developer:
            #print1(f"running tool '{func_name}' ...")
            print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Running tool</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{func_name}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
    # ChatGPT's built-in function named "python"
    if function_name == "python":
        notifyDeveloper(function_name)
        python_code = textwrap.dedent(func_arguments)
        refinedCode = fineTunePythonCode(python_code)

        print1(config.divider)
        print2("running python code ...")
        risk = riskAssessment(python_code)
        showRisk(risk)
        if config.developer or config.codeDisplay:
            print("```")
            #print(python_code)
            # pygments python style
            tokens = list(pygments.lex(python_code, lexer=PythonLexer()))
            print_formatted_text(PygmentsTokens(tokens), style=getPygmentsStyle())
            print("```")
        print1(config.divider)

        config.stopSpinning()
        if not config.runPython:
            info = {"information": python_code}
            return json.dumps(info)
        elif confirmExecution(risk):
            print1("Do you want to continue? [y]es / [N]o")
            confirmation = prompt(style=config.promptStyle2, default="y")
            if not confirmation.lower() in ("y", "yes"):
                info = {"information": python_code}
                return json.dumps(info)
        try:
            exec(refinedCode, globals())
            function_response = getPythonFunctionResponse()
        except:
            trace = showErrors()
            print1(config.divider)
            if config.max_consecutive_auto_correction > 0:
                return autoCorrectPythonCode(refinedCode, trace)
            else:
                return "[INVALID]"
        if function_response:
            info = {"information": function_response}
            function_response = json.dumps(info)
    # known unwanted functions are handled here
    elif function_name in ("translate_text",):
        # "translate_text" has two arguments, "text", "target_language"
        # handle known and unwanted function
        function_response = "[INVALID]" 
    # handle unexpected function
    elif not function_name in config.toolFunctionMethods:
        if config.developer:
            print1(f"Unexpected function: {function_name}")
            print1(config.divider)
            print(func_arguments)
            print1(config.divider)
        function_response = "[INVALID]"
    else:
        notifyDeveloper(function_name)
        fuction_to_call = config.toolFunctionMethods[function_name]
        # convert the arguments from json into a dict
        function_args = json.loads(func_arguments)
        function_response = fuction_to_call(function_args)
    return function_response


class CallGoogleAI:

    @staticmethod
    @check_errors
    def checkCompletion():
        checkCompletion()

    @staticmethod
    @check_errors
    def autoCorrectPythonCode(code, trace):
        return autoCorrectPythonCode(code, trace)

    @staticmethod
    @check_errors
    def getSingleChatResponse(userInput, messages=[], temperature=None, prefill: Optional[str]=None, stop: Optional[list]=None, keepSystemMessage: bool=False):
        return getSingleChatResponse(userInput, messages, temperature, prefill, stop, keepSystemMessage)

    @staticmethod
    def finetuneSingleFunctionCallResponse(func_arguments, function_name):
        return finetuneSingleFunctionCallResponse(func_arguments, function_name)

    @staticmethod
    def runSingleFunctionCall(messages, function_name):
        return runSingleFunctionCall(messages, function_name)

    @staticmethod
    @check_errors
    def getSingleFunctionCallResponse(messages: list[dict], function_name: str, temperature=None, **kwargs):
        return getSingleFunctionCallResponse(messages, function_name, temperature, **kwargs)

    @staticmethod
    @check_errors
    def regularCall(messages: dict, **kwargs):
        chatMessages = useChatSystemMessage(copy.deepcopy(messages))
        return getGoogleGenAIClient().chat.completions.create(
            model=config.googleaiApi_tool_model,
            messages=chatMessages,
            n=1,
            temperature=config.llmTemperature,
            max_tokens=config.googleaiApi_tool_model_max_tokens,
            stream=True,
            **kwargs,
        )

    @staticmethod
    @check_errors
    @check_errors
    def getDictionaryOutput(messages: list, schema: dict, **kwargs) -> dict:
        completion = getGoogleGenAIClient().chat.completions.create(
            model=config.googleaiApi_tool_model,
            messages=messages,
            n=1,
            temperature=config.llmTemperature,
            max_tokens=config.googleaiApi_tool_model_max_tokens,
            tools=[{"type": "function", "function": schema}],
            tool_choice={"type": "function", "function": {"name": schema["name"]}},
            stream=False,
            **kwargs,
        )
        outputMessage = completion.choices[0].message
        if hasattr(outputMessage, "tool_calls") and outputMessage.tool_calls:
            function_arguments = outputMessage.tool_calls[0].function.arguments
            responseDict = json.loads(codecs.decode(function_arguments, "unicode_escape"))
        else:
            #print("Failed to output structered data!")
            if hasattr(outputMessage, "content") and outputMessage.content:
                return codecs.decode(outputMessage.content, "unicode_escape")
            return {}
        return responseDict

    # Auto Function Call equivalence

    @staticmethod
    def runToolCall(messages: dict):
        if not config.selectedTool:
            return CallGoogleAI.regularCall(messages)
        else:
            # 2. Tool Selection
            if config.selectedTool and not config.selectedTool == "chat" and config.selectedTool in config.toolFunctionSchemas:
                tool_name = config.selectedTool
                tool_schema = config.toolFunctionSchemas[tool_name]
                config.selectedTool = ""
            else:
                return CallGoogleAI.regularCall(messages)
            # 3. Parameter Extraction
            if config.developer:
                print1("extracting parameters ...")
            try:
                if not tool_schema["parameters"]["properties"]:
                    # Execute function directly
                    tool_parameters = {}
                    tool_response = executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
                else:
                    tool_parameters = CallGoogleAI.getDictionaryOutput(messages=messages, schema=tool_schema)
                    if isinstance(tool_parameters, str):
                        tool_response = tool_parameters
                    elif not validParameters(tool_parameters, tool_schema["parameters"]["required"]):
                        return CallGoogleAI.regularCall(messages)
                    else:
                        # 4. Function Execution
                        tool_response = executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
            except:
                print(traceback.format_exc())
                tool_response = "[INVALID]"
            # 5. Chat Extension
            if tool_response == "[INVALID]":
                # invalid tool call; return a regular call instead
                return CallGoogleAI.regularCall(messages)
            else:
                # record tool selection
                #config.currentMessages[-1]["tool"] = tool_name
                if tool_response:
                    if config.developer:
                        print2(config.divider)
                        print2("Tool output:")
                        print(tool_response)
                        print2(config.divider)
                    # update message chain
                    user_request = messages[-1]["content"]
                    messages[-1]["content"] = getRagPrompt(user_request, tool_response)
                    return CallGoogleAI.regularCall(messages)
                elif (not config.currentMessages[-1].get("role", "") == "assistant" and not config.currentMessages[-2].get("role", "") == "assistant") or (config.currentMessages[-1].get("role", "") == "system" and not config.currentMessages[-2].get("role", "") == "assistant"):
                    # tool function executed without chat extension
                    if config.toolTextOutput:
                        config.toolTextOutput = refineToolTextOutput(config.toolTextOutput)
                    config.currentMessages.append({"role": "assistant", "content": config.toolTextOutput if config.toolTextOutput else "Done!"})
                    config.toolTextOutput = ""
                    config.conversationStarted = True
                    return None

    @staticmethod
    def extractToolParameters(schema: dict, ongoingMessages: list = [], **kwargs) -> dict:
        """
        Extract action parameters
        """
        parameters = CallGoogleAI.getDictionaryOutput(messages=ongoingMessages, schema=schema, **kwargs)
        if config.developer:
            print2("```parameters")
            pprint.pprint(parameters)
            print2("```")
        return parameters
