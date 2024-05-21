from freegenius import showErrors, get_or_create_collection, query_vectors, showRisk, executeToolFunction, getPythonFunctionResponse, getPygmentsStyle, fineTunePythonCode, confirmExecution
from freegenius import config
from freegenius import print1, print2, print3, getDynamicTokens, selectTool, selectEnabledTool
import re, traceback, openai, pprint, copy, textwrap, json, pygments
from pygments.lexers.python import PythonLexer
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import prompt

# token limit
# reference: https://platform.openai.com/docs/models/gpt-4
tokenLimits = {
    "gpt-4o": 128000,
    "gpt-4-turbo": 128000, # Returns a maximum of 4,096 output tokens.
    "gpt-4-turbo-preview": 128000, # Returns a maximum of 4,096 output tokens.
    "gpt-4-0125-preview": 128000, # Returns a maximum of 4,096 output tokens.
    "gpt-4-1106-preview": 128000, # Returns a maximum of 4,096 output tokens.
    "gpt-3.5-turbo": 16385, # Returns a maximum of 4,096 output tokens.
    "gpt-3.5-turbo-16k": 16385,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
}

def check_openai_errors(func):
    def wrapper(*args, **kwargs):
        def finishError():
            config.stopSpinning()
            return "[INVALID]"
        try:
            return func(*args, **kwargs)
        except openai.APIError as e:
            print("Error: Issue on OpenAI side.")
            print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
            return finishError()
        except openai.APIConnectionError as e:
            print("Error: Issue connecting to our services.")
            print("Solution: Check your network settings, proxy configuration, SSL certificates, or firewall rules.")
            return finishError()
        except openai.APITimeoutError as e:
            print("Error: Request timed out.")
            print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
            return finishError()
        except openai.AuthenticationError as e:
            print("Error: Your API key or token was invalid, expired, or revoked.")
            print("Solution: Check your API key or token and make sure it is correct and active. You may need to generate a new one from your account dashboard.")
            return finishError()
        except openai.BadRequestError as e:
            print("Error: Your request was malformed or missing some required parameters, such as a token or an input.")
            print("Solution: The error message should advise you on the specific error made. Check the [documentation](https://platform.openai.com/docs/api-reference/) for the specific API method you are calling and make sure you are sending valid and complete parameters. You may also need to check the encoding, format, or size of your request data.")
            return finishError()
        except openai.ConflictError as e:
            print("Error: The resource was updated by another request.")
            print("Solution: Try to update the resource again and ensure no other requests are trying to update it.")
            return finishError()
        except openai.InternalServerError as e:
            print("Error: Issue on OpenAI servers.")
            print("Solution: Retry your request after a brief wait and contact us if the issue persists. Check the [status page](https://status.openai.com).")
            return finishError()
        except openai.NotFoundError as e:
            print("Error: Requested resource does not exist.")
            print("Solution: Ensure you are the correct resource identifier.")
            return finishError()
        except openai.PermissionDeniedError as e:
            print("Error: You don't have access to the requested resource.")
            print("Solution: Ensure you are using the correct API key, organization ID, and resource ID.")
            return finishError()
        except openai.RateLimitError as e:
            print("Error: You have hit your assigned rate limit.")
            print("Solution: Pace your requests. Read more in OpenAI [Rate limit guide](https://platform.openai.com/docs/guides/rate-limits).")
            return finishError()
        except openai.UnprocessableEntityError as e:
            print("Error: Unable to process the request despite the format being correct.")
            print("Solution: Please try the request again.")
            return finishError()
        except:
            print(traceback.format_exc())
            return finishError()
    return wrapper

@check_openai_errors
def checkCompletion():
    config.oai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content" : "hello"}],
        n=1,
        max_tokens=10,
    )

@check_openai_errors
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
        answer = getSingleChatResponse(content, temperature=0.0)
        if not answer:
            answer = "high"
        answer = re.sub("[^A-Za-z]", "", answer).lower()
        if not answer in ("high", "medium", "low"):
            answer = "high"
        return answer
    except:
        return "high"

@check_openai_errors
def autoCorrectPythonCode(code, trace):
    for i in range(config.max_consecutive_auto_correction):
        userInput = f"Original python code:\n```\n{code}\n```\n\nTraceback:\n```\n{trace}\n```"
        messages = [{"role": "user", "content" : userInput}]
        print3(f"Auto-correction attempt: {(i + 1)}")
        function_call_message, function_call_response = CallChatGPT.getSingleFunctionCallResponse(messages, "correct_python") if config.llmInterface == "chatgpt" else CallLetMeDoIt.getSingleFunctionCallResponse(messages, "correct_python")
        # display response
        print1(config.divider)
        if config.developer:
            print(function_call_response)
        else:
            print1("Executed!" if function_call_response == "EXECUTED" else "Failed!")
        if function_call_response == "EXECUTED":
            break
        else:
            code = json.loads(function_call_message["function_call"]["arguments"]).get("code")
            trace = function_call_response
        print1(config.divider)
    # return information if any
    if function_call_response == "EXECUTED":
        pythonFunctionResponse = getPythonFunctionResponse(code)
        if pythonFunctionResponse:
            return json.dumps({"information": pythonFunctionResponse})
        else:
            return ""
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

@check_openai_errors
def getSingleChatResponse(userInput, messages=[], temperature=None):
    """
    non-streaming single call
    """
    messages.append({"role": "user", "content" : userInput})
    try:
        completion = config.oai_client.chat.completions.create(
            model=config.chatGPTApiModel,
            messages=messages,
            n=1,
            temperature=temperature if temperature is not None else config.llmTemperature,
            max_tokens=config.chatGPTApiMaxTokens,
        )
        return completion.choices[0].message.content
    except:
        return ""

def runSingleFunctionCall(messages, function_name):
    messagesCopy = copy.deepcopy(messages)
    try:
        function_call_message, function_call_response = getSingleFunctionCallResponse(messages, function_name)
        messages.append(function_call_message)
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_call_response if function_call_response else config.tempContent,
            }
        )
        config.tempContent = ""
    except:
        showErrors()
        return messagesCopy
    return messages

@check_openai_errors
def getSingleFunctionCallResponse(messages: list[dict], function_name: str, temperature=None, **kwargs):
    functionSignatures = [config.toolFunctionSchemas[function_name]]
    completion = config.oai_client.chat.completions.create(
        model=config.chatGPTApiModel,
        messages=messages,
        n=1,
        temperature=temperature if temperature is not None else config.llmTemperature,
        max_tokens=getDynamicTokens(messages, functionSignatures),
        tools=convertFunctionSignaturesIntoTools(functionSignatures),
        tool_choice={"type": "function", "function": {"name": function_name}},
        stream=False,
        **kwargs,
    )
    function_call_message = completion.choices[0].message
    tool_call = function_call_message.tool_calls[0]
    func_arguments = tool_call.function.arguments
    function_call_message_mini = {
        "role": "assistant",
        "content": "",
        "function_call": {
            "name": tool_call.function.name,
            "arguments": func_arguments,
        }
    }
    function_call_response = CallChatGPT.finetuneSingleFunctionCallResponse(func_arguments, function_name)
    return function_call_message_mini, function_call_response

def finetuneSingleFunctionCallResponse(func_arguments, function_name):
    # fine tune function call response; applied to chatgpt only
    def notifyDeveloper(func_name):
        if config.developer:
            #print1(f"running function '{func_name}' ...")
            print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Running function</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{func_name}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
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
            function_response = getPythonFunctionResponse(refinedCode)
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


class CallChatGPT:

    @staticmethod
    @check_openai_errors
    def checkCompletion():
        checkCompletion()

    @staticmethod
    @check_openai_errors
    def autoCorrectPythonCode(code, trace):
        return autoCorrectPythonCode(code, trace)

    @staticmethod
    @check_openai_errors
    def getSingleChatResponse(userInput, messages=[], temperature=None):
        return getSingleChatResponse(userInput, messages, temperature)

    @staticmethod
    def finetuneSingleFunctionCallResponse(func_arguments, function_name):
        return finetuneSingleFunctionCallResponse(func_arguments, function_name)

    @staticmethod
    def runSingleFunctionCall(messages, function_name):
        return runSingleFunctionCall(messages, function_name)

    @staticmethod
    @check_openai_errors
    def getSingleFunctionCallResponse(messages: list[dict], function_name: str, temperature=None, **kwargs):
        return getSingleFunctionCallResponse(messages, function_name, temperature, **kwargs)

    @staticmethod
    @check_openai_errors
    def regularCall(messages: dict, **kwargs):
        return config.oai_client.chat.completions.create(
            model=config.chatGPTApiModel,
            messages=messages,
            n=1,
            temperature=config.llmTemperature,
            max_tokens=getDynamicTokens(messages),
            stream=True,
            **kwargs,
        )

    @staticmethod
    @check_openai_errors
    def getDictionaryOutput(messages: list, schema: dict, **kwargs) -> dict:
        completion = config.oai_client.chat.completions.create(
            model=config.chatGPTApiModel,
            messages=messages,
            n=1,
            temperature=config.llmTemperature,
            max_tokens=getDynamicTokens(messages, [schema]),
            tools=[{"type": "function", "function": schema}],
            tool_choice={"type": "function", "function": {"name": schema["name"]}},
            stream=False,
            **kwargs,
        )
        responseDict = json.loads(completion.choices[0].message.tool_calls[0].function.arguments)
        return responseDict

    # Auto Function Call equivalence

    @staticmethod
    def runGeniusCall(messages: dict, noFunctionCall: bool = False):
        user_request = messages[-1]["content"]
        if config.intent_screening and config.tool_dependence > 0.0:
            # 1. Intent Screening
            noFunctionCall = True if noFunctionCall else CallChatGPT.isChatOnly(messages=messages)
        if noFunctionCall or config.tool_dependence <= 0.0:
            return CallChatGPT.regularCall(messages)
        else:
            # 2. Tool Selection
            if config.selectedTool and config.selectedTool in config.toolFunctionSchemas:
                tool_name = config.selectedTool
                tool_schema = config.toolFunctionSchemas[tool_name]
                config.selectedTool = ""
            else:
                if config.developer:
                    print1("selecting tool ...")
                tool_collection = get_or_create_collection(config.tool_store_client, "tools")
                search_result = query_vectors(tool_collection, user_request, config.tool_selection_max_choices)
                
                # no tool is available; return a regular call instead
                if not search_result:
                    return CallChatGPT.regularCall(messages)

                # check the closest distance
                closest_distance = search_result["distances"][0][0]
                
                # when a tool is irrelevant
                if closest_distance > config.tool_dependence:
                    return CallChatGPT.regularCall(messages)

                # auto or manual selection
                selected_index = selectTool(search_result, closest_distance)
                if selected_index is None:
                    return CallChatGPT.regularCall(messages)
                elif selected_index >= len(search_result["metadatas"][0]):
                    tool_name = selectEnabledTool()
                    semantic_distance = None
                    if tool_name is None:
                        return CallChatGPT.regularCall(messages)
                else:
                    semantic_distance = search_result["distances"][0][selected_index]
                    metadatas = search_result["metadatas"][0][selected_index]
                    tool_name = metadatas["name"]

                tool_schema = config.toolFunctionSchemas[tool_name]
                if config.developer:
                    semantic_distance = "" if semantic_distance is None else f" ({semantic_distance})"
                    print3(f"Selected: {tool_name}{semantic_distance}")
            if tool_name == "chat":
                return CallChatGPT.regularCall(messages)
            # 3. Parameter Extraction
            if config.developer:
                print1("extracting parameters ...")
            try:
                #tool_parameters = CallChatGPT.extractToolParameters(schema=tool_schema, ongoingMessages=messages)
                tool_parameters = CallChatGPT.getDictionaryOutput(messages=messages, schema=tool_schema)
                if not tool_parameters:
                    if config.developer:
                        print1("Failed to extract parameters!")
                    return CallChatGPT.regularCall(messages)
                # 4. Function Execution
                tool_response = executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
            except:
                print(traceback.format_exc())
                tool_response = "[INVALID]"
            # 5. Chat Extension
            if tool_response == "[INVALID]":
                # invalid tool call; return a regular call instead
                return CallChatGPT.regularCall(messages)
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
                    messages.append(
                        {
                            "role": "assistant",
                            "content": "",
                            "function_call": {
                                "name": tool_name,
                                "arguments": json.dumps(tool_parameters),
                            }
                        }
                    )
                    messages.append(
                        {
                            "role": "function",
                            "name": tool_name,
                            "content": tool_response if tool_response else config.tempContent,
                        }
                    )
                    config.tempContent = ""

                    return CallChatGPT.regularCall(messages)
                elif (not config.currentMessages[-1].get("role", "") == "assistant" and not config.currentMessages[-2].get("role", "") == "assistant") or (config.currentMessages[-1].get("role", "") == "system" and not config.currentMessages[-2].get("role", "") == "assistant"):
                    # tool function executed without chat extension
                    config.currentMessages.append({"role": "assistant", "content": config.tempContent if config.tempContent else "Done!"})
                    config.tempContent = ""
                    config.conversationStarted = True
                    return None

    @staticmethod
    def isChatOnly(messages: dict) -> bool:
        print2("```screening")
        properties = {
            "answer": {
                "type": "string",
                "description": """Evaluate my request to determine if you are able to resolve my request as a text-based AI:
- Answer 'no' if you are asked to execute a computing task or an online search.
- Answer 'no' if you are asked for updates / news / real-time information.
- Answer 'yes' if the request is a greeting or translation.
- Answer 'yes' only if you have full information to give a direct response.""",
                "enum": ['yes', 'no'],
            },
        }
        schema = {
            "name": "screen_user_request",
            "description": f'''Estimate user request''',
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": ["code"],
            },
        }
        output = CallChatGPT.getDictionaryOutput(messages, schema=schema)
        chatOnly = True if "yes" in str(output).lower() else False
        print3(f"""Tool may {"not " if chatOnly else ""}be required.""")
        print2("```")
        return chatOnly

    @staticmethod
    def extractToolParameters(schema: dict, ongoingMessages: list = [], **kwargs) -> dict:
        """
        Extract action parameters
        """
        parameters = CallChatGPT.getDictionaryOutput(messages=ongoingMessages, schema=schema, **kwargs)
        if config.developer:
            print2("```parameters")
            pprint.pprint(parameters)
            print2("```")
        return parameters


class CallLetMeDoIt:

    @staticmethod
    @check_openai_errors
    def checkCompletion():
        checkCompletion()

    @staticmethod
    @check_openai_errors
    def autoCorrectPythonCode(code, trace):
        return autoCorrectPythonCode(code, trace)

    @staticmethod
    @check_openai_errors
    def getSingleChatResponse(userInput, messages=[], temperature=None):
        return getSingleChatResponse(userInput, messages, temperature)

    @staticmethod
    def finetuneSingleFunctionCallResponse(func_arguments, function_name):
        return finetuneSingleFunctionCallResponse(func_arguments, function_name)

    @staticmethod
    def runSingleFunctionCall(messages, function_name):
        return runSingleFunctionCall(messages, function_name)

    @staticmethod
    @check_openai_errors
    def getSingleFunctionCallResponse(messages: list[dict], function_name: str, temperature=None, **kwargs):
        return getSingleFunctionCallResponse(messages, function_name, temperature, **kwargs)

    @staticmethod
    @check_openai_errors
    def runGeniusCall(thisMessage, noFunctionCall=False):
        functionJustCalled = False
        def runThisCompletion(thisThisMessage):
            nonlocal functionJustCalled
            if config.toolFunctionSchemas and not functionJustCalled and not noFunctionCall:
                toolFunctionSchemas = [config.toolFunctionSchemas[config.selectedTool]] if config.selectedTool and config.selectedTool in config.toolFunctionSchemas else config.toolFunctionSchemas.values()
                return config.oai_client.chat.completions.create(
                    model=config.chatGPTApiModel,
                    messages=thisThisMessage,
                    n=1,
                    temperature=config.llmTemperature,
                    max_tokens=getDynamicTokens(thisThisMessage, toolFunctionSchemas),
                    tools=convertFunctionSignaturesIntoTools(toolFunctionSchemas),
                    tool_choice={"type": "function", "function": {"name": config.selectedTool}} if config.selectedTool else config.chatGPTApiFunctionCall,
                    stream=True,
                )
            return config.oai_client.chat.completions.create(
                model=config.chatGPTApiModel,
                messages=thisThisMessage,
                n=1,
                temperature=config.llmTemperature,
                max_tokens=getDynamicTokens(thisThisMessage),
                stream=True,
            )

        while True:
            completion = runThisCompletion(thisMessage)
            config.selectedTool = ""
            try:
                # consume the first delta
                for event in completion:
                    first_delta = event.choices[0].delta
                    # check if a tool is called
                    if first_delta.tool_calls: # a tool is called
                        function_calls = [i for i in first_delta.tool_calls if i.type == "function"]
                        # non_function_calls = [i for i in first_delta.tool_calls if not i.type == "function"]
                    else: # no tool is called; same handling as tools finished calling; which break the loop later
                        functionJustCalled = True
                    # consume the first delta only at this point
                    break
                # Continue only when a function is called
                if functionJustCalled:
                    break

                # get all tool arguments, both of functions and non-functions
                toolArguments = getToolArgumentsFromStreams(completion)

                func_responses = ""
                bypassFunctionCall = False
                # handle function calls
                for func in function_calls:
                    func_index = func.index
                    func_id = func.id
                    func_name = func.function.name
                    func_arguments = toolArguments[func_index]

                    if config.developer:
                        print2(f"```{func_name}")
                        try:
                            pprint.pprint(json.loads(func_arguments))
                        except:
                            pprint.pprint(func_arguments)
                        print2("```")

                    # get function response
                    func_response = CallLetMeDoIt.finetuneSingleFunctionCallResponse(func_arguments, func_name)

                    # "[INVALID]" practically mean that it ignores previously called function and continues chat without function calling
                    if func_response == "[INVALID]":
                        bypassFunctionCall = True
                    elif func_response or config.tempContent:
                        # send the function call info and response to GPT
                        function_call_message = {
                            "role": "assistant",
                            "content": "",
                            "function_call": {
                                "name": func_name,
                                "arguments": func_arguments,
                            }
                        }
                        #lastRole = thisMessage[-1].get("role", "")
                        #if lastRole == "user":
                            #thisMessage[-1]["tool"] = func_name
                        thisMessage.append(function_call_message) # extend conversation with assistant's reply
                        thisMessage.append(
                            {
                                "tool_call_id": func_id,
                                "role": "function",
                                "name": func_name,
                                "content": func_response if func_response else config.tempContent,
                            }
                        )  # extend conversation with function response
                        config.tempContent = ""
                        if func_response:
                            func_responses += f"\n{func_response}\n{config.divider}"

                functionJustCalled = True

                # bypassFunctionCall is set to True, usually when a function is called by mistake
                if bypassFunctionCall:
                    pass
                # two cases that breaks the loop at this point
                # 1. func_responses == ""
                # 2. config.passFunctionCallReturnToChatGPT = False
                elif not config.passFunctionCallReturnToChatGPT or not func_responses:
                    if func_responses:
                        print1(f"{config.divider}\n{func_responses}")
                    # A break here means that no information from the called function is passed back to ChatGPT
                    # 1. config.passFunctionCallReturnToChatGPT is set to True
                    # 2. func_responses = "" or None; can be specified in plugins
                    break
            except:
                showErrors()
                break

        return completion