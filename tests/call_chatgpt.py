from freegenius import config
from freegenius.utils.shared_utils import SharedUtil
from openai import OpenAI
import openai, traceback, textwrap, json, pygments
from pygments.lexers.python import PythonLexer
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import prompt


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
            #HealthCheck.changeAPIkey()
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


class CallChatGPT:

    @staticmethod
    @check_openai_errors
    def checkCompletion():
        SharedUtil.setAPIkey()
        config.oai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content" : "hello"}],
            n=1,
            max_tokens=10,
        )

    @staticmethod
    @check_openai_errors
    def getSingleChatResponse(userInput, temperature=None):
        """
        non-streaming single call
        """
        try:
            completion = OpenAI().chat.completions.create(
                model=config.chatGPTApiModel,
                messages=[{"role": "user", "content" : userInput}],
                n=1,
                temperature=temperature if temperature is not None else config.llmTemperature,
                max_tokens=config.chatGPTApiMaxTokens,
            )
            return completion.choices[0].message.content
        except:
            return ""

    @staticmethod
    def runSingleFunctionCall(messages, functionSignatures, function_name):
        messagesCopy = messages[:]
        try:
            function_call_message, function_call_response = CallChatGPT.getSingleFunctionCallResponse(messages, functionSignatures, function_name)
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
            SharedUtil.showErrors()
            return messagesCopy
        return messages

    @staticmethod
    @check_openai_errors
    def getSingleFunctionCallResponse(messages, functionSignatures, function_name, temperature=None):
        completion = config.oai_client.chat.completions.create(
            model=config.chatGPTApiModel,
            messages=messages,
            max_tokens=SharedUtil.getDynamicTokens(messages, functionSignatures),
            temperature=temperature if temperature is not None else config.llmTemperature,
            n=1,
            tools=SharedUtil.convertFunctionSignaturesIntoTools(functionSignatures),
            tool_choice={"type": "function", "function": {"name": function_name}},
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

    @staticmethod
    def finetuneSingleFunctionCallResponse(func_arguments, function_name):
        # fine tune function call response; applied to chatgpt only
        def notifyDeveloper(func_name):
            if config.developer:
                #config.print(f"running function '{func_name}' ...")
                print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Running function</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{func_name}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
        # ChatGPT's built-in function named "python"
        if function_name == "python":
            notifyDeveloper(function_name)
            python_code = textwrap.dedent(func_arguments)
            refinedCode = SharedUtil.fineTunePythonCode(python_code)

            config.print(config.divider)
            config.print2("running python code ...")
            risk = SharedUtil.riskAssessment(python_code)
            SharedUtil.showRisk(risk)
            if config.developer or config.codeDisplay:
                print("```")
                #print(python_code)
                # pygments python style
                tokens = list(pygments.lex(python_code, lexer=PythonLexer()))
                print_formatted_text(PygmentsTokens(tokens), style=SharedUtil.getPygmentsStyle())
                print("```")
            config.print(config.divider)

            config.stopSpinning()
            if not config.runPython:
                info = {"information": python_code}
                return json.dumps(info)
            elif SharedUtil.confirmExecution(risk):
                config.print("Do you want to continue? [y]es / [N]o")
                confirmation = prompt(style=config.promptStyle2, default="y")
                if not confirmation.lower() in ("y", "yes"):
                    info = {"information": python_code}
                    return json.dumps(info)
            try:
                exec(refinedCode, globals())
                function_response = SharedUtil.getPythonFunctionResponse(refinedCode)
            except:
                trace = SharedUtil.showErrors()
                config.print(config.divider)
                if config.max_consecutive_auto_heal > 0:
                    return SharedUtil.autoHealPythonCode(refinedCode, trace)
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
        elif not function_name in config.chatGPTApiAvailableFunctions:
            if config.developer:
                config.print(f"Unexpected function: {function_name}")
                config.print(config.divider)
                print(func_arguments)
                config.print(config.divider)
            function_response = "[INVALID]"
        else:
            notifyDeveloper(function_name)
            fuction_to_call = config.chatGPTApiAvailableFunctions[function_name]
            # convert the arguments from json into a dict
            function_args = json.loads(func_arguments)
            function_response = fuction_to_call(function_args)
        return function_response

    @staticmethod
    @check_openai_errors
    def runAutoFunctionCall(thisMessage, noFunctionCall=False):
        functionJustCalled = False
        def runThisCompletion(thisThisMessage):
            nonlocal functionJustCalled
            if config.chatGPTApiFunctionSignatures and not functionJustCalled and not noFunctionCall:
                return config.oai_client.chat.completions.create(
                    model=config.chatGPTApiModel,
                    messages=thisThisMessage,
                    n=1,
                    temperature=config.llmTemperature,
                    max_tokens=SharedUtil.getDynamicTokens(thisThisMessage, config.chatGPTApiFunctionSignatures.values()),
                    tools=SharedUtil.convertFunctionSignaturesIntoTools([config.chatGPTApiFunctionSignatures[config.runSpecificFuntion]] if config.runSpecificFuntion and config.runSpecificFuntion in config.chatGPTApiFunctionSignatures else config.chatGPTApiFunctionSignatures.values()),
                    tool_choice={"type": "function", "function": {"name": config.runSpecificFuntion}} if config.runSpecificFuntion else config.chatGPTApiFunctionCall,
                    stream=True,
                )
            return config.oai_client.chat.completions.create(
                model=config.chatGPTApiModel,
                messages=thisThisMessage,
                n=1,
                temperature=config.llmTemperature,
                max_tokens=SharedUtil.getDynamicTokens(thisThisMessage),
                stream=True,
            )

        while True:
            completion = runThisCompletion(thisMessage)
            config.runSpecificFuntion = ""
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
                toolArguments = SharedUtil.getToolArgumentsFromStreams(completion)

                func_responses = ""
                bypassFunctionCall = False
                # handle function calls
                for func in function_calls:
                    func_index = func.index
                    func_id = func.id
                    func_name = func.function.name
                    func_arguments = toolArguments[func_index]

                    # get function response
                    func_response = CallChatGPT.finetuneSingleFunctionCallResponse(func_arguments, func_name)

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
                        config.print(f"{config.divider}\n{func_responses}")
                    # A break here means that no information from the called function is passed back to ChatGPT
                    # 1. config.passFunctionCallReturnToChatGPT is set to True
                    # 2. func_responses = "" or None; can be specified in plugins
                    break
            except:
                SharedUtil.showErrors()
                break

        return completion