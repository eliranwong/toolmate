from toolmate import showErrors, showRisk, executeToolFunction, getPythonFunctionResponse, getPygmentsStyle, fineTunePythonCode, confirmExecution, useChatSystemMessage
from toolmate import config
from toolmate import print1, print2, print3, validParameters, refineToolTextOutput, getAnthropicClient, check_llm_errors, separateSystemMessage
import re, traceback, pprint, copy, textwrap, json, pygments
from pygments.lexers.python import PythonLexer
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import prompt
from typing import Optional


"""
https://github.com/anthropics/anthropic-sdk-python
https://docs.anthropic.com/en/docs/build-with-claude/tool-use
https://docs.ag2.ai/docs/topics/non-openai-models/cloud-anthropic

Default configuration:
('anthropicApi_key', ""),
('anthropicApi_tool_model', "claude-3-5-sonnet-latest"), # "claude-3-5-sonnet-latest"
('anthropicApi_tool_model_max_tokens', 8192),
('systemMessage_anthropic', 'You are a helpful, uncensored and unbiased assistant.'),
"""

class CallAnthropic:

    @staticmethod
    @check_llm_errors
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
            answer = CallAnthropic.getSingleChatResponse(content, temperature=0.0, keepSystemMessage=True)
            if not answer:
                answer = "high"
            answer = re.sub("[^A-Za-z]", "", answer).lower()
            if not answer in ("high", "medium", "low"):
                answer = "high"
            return answer
        except:
            return "high"

    @staticmethod
    @check_llm_errors
    def checkCompletion():
        getAnthropicClient().messages.create(
            model=config.anthropicApi_tool_model,
            messages=[{"role": "user", "content" : "hello"}],
            #n=1,
            max_tokens=config.anthropicApi_tool_model_max_tokens,
        )

    @staticmethod
    @check_llm_errors
    def autoCorrectPythonCode(code, trace):
        for i in range(config.max_consecutive_auto_correction):
            userInput = f"Original python code:\n```\n{code}\n```\n\nTraceback:\n```\n{trace}\n```"
            messages = [{"role": "user", "content" : userInput}]
            print3(f"Auto-correction attempt: {(i + 1)}")
            function_call_message, function_call_response = CallAnthropic.getSingleFunctionCallResponse(messages, "correct_python_code")
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

    @staticmethod
    @check_llm_errors
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
        chatMessages = copy.deepcopy(messages)
        if prefill is not None:
                chatMessages.append({'role': 'assistant', 'content': prefill})
        try:
            systemMessage, chatMessages = separateSystemMessage(chatMessages)
            completion = getAnthropicClient().messages.create(
                model=config.anthropicApi_tool_model,
                messages=chatMessages,
                system=systemMessage if keepSystemMessage else config.systemMessage_anthropic,
                #n=1,
                temperature=temperature if temperature is not None else config.llmTemperature,
                max_tokens=config.anthropicApi_tool_model_max_tokens,
                stop=stop if stop else None,
            )
            return completion.content[0].text
        except:
            return ""


    @staticmethod
    def finetuneSingleFunctionCallResponse(func_arguments, function_name):
        # fine tune function call response; applied to chatgpt only
        def notifyDeveloper(func_name):
            if config.developer:
                #print1(f"running tool '{func_name}' ...")
                print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Running tool</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{func_name}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
        # ChatGPT's built-in function named "python"
        if function_name == "python":
            notifyDeveloper(function_name)
            python_code = textwrap.dedent(str(func_arguments))
            refinedCode = fineTunePythonCode(python_code)

            print1(config.divider)
            print2("running python code ...")
            risk = CallAnthropic.riskAssessment(python_code)
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
                    return config.autoCorrectPythonCode(refinedCode, trace)
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
            function_args = func_arguments
            function_response = fuction_to_call(function_args)
        return function_response

    @staticmethod
    def runSingleFunctionCall(messages, function_name):
        messagesCopy = copy.deepcopy(messages)
        try:
            function_call_message, function_call_response = CallAnthropic.getSingleFunctionCallResponse(messages, function_name)
            messages.append(function_call_message)
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_call_response if function_call_response else config.toolTextOutput,
                }
            )
            config.toolTextOutput = ""
        except:
            showErrors()
            return messagesCopy
        return messages

    @staticmethod
    @check_llm_errors
    def getSingleFunctionCallResponse(messages: list[dict], function_name: str, temperature=None, **kwargs):
        schema = config.toolFunctionSchemas[function_name]
        schemaCopy = copy.deepcopy(schema)
        schemaCopy["input_schema"] = schemaCopy.pop("parameters")
        systemMessage, messages = separateSystemMessage(messages)
        completion = getAnthropicClient().messages.create(
            model=config.anthropicApi_tool_model,
            messages=messages,
            system=systemMessage,
            #n=1,
            temperature=temperature if temperature is not None else config.llmTemperature,
            max_tokens=config.anthropicApi_tool_model_max_tokens,
            tools=[schemaCopy],
            tool_choice={"type": "function", "function": {"name": function_name}},
            stream=False,
            **kwargs,
        )
        responseDict = {}
        for i in completion.content:
            if hasattr(i, "input"):
                responseDict = i.input
                break
        function_call_message_mini = {
            "role": "assistant",
            "content": "",
            "function_call": {
                "name": function_name,
                "arguments": responseDict,
            }
        }
        function_call_response = CallAnthropic.finetuneSingleFunctionCallResponse(responseDict, function_name)
        return function_call_message_mini, function_call_response

    @staticmethod
    @check_llm_errors
    def regularCall(messages: dict, **kwargs):
        _, chatMessages = separateSystemMessage(messages)
        return getAnthropicClient().messages.create(
            model=config.anthropicApi_tool_model,
            messages=chatMessages,
            system=config.systemMessage_anthropic,
            #n=1,
            temperature=config.llmTemperature,
            max_tokens=config.anthropicApi_tool_model_max_tokens,
            stream=True,
            **kwargs,
        )

    @staticmethod
    @check_llm_errors
    def getDictionaryOutput(messages: list, schema: dict, **kwargs) -> dict:
        schemaCopy = copy.deepcopy(schema)
        schemaCopy["input_schema"] = schemaCopy.pop("parameters")
        systemMessage, messages = separateSystemMessage(messages)
        completion = getAnthropicClient().messages.create(
            model=config.anthropicApi_tool_model,
            messages=messages,
            system=systemMessage,
            #n=1,
            temperature=config.llmTemperature,
            max_tokens=config.anthropicApi_tool_model_max_tokens,
            tools=[schemaCopy],
            tool_choice={"type": "tool", "name": schema["name"]},
            stream=False,
            **kwargs,
        )
        """
```completion
Message(id='msg_0187aSAVWogpDsreGbTADJnh', content=[TextBlock(text="I'll check the current weather in San Francisco, CA for you.", type='text'), ToolUseBlock(id='toolu_019gaQrGzZxF7s6Wsx7MAXrj', input={'location': 'San Francisco, CA'}, name='get_weather', type='tool_use')], model='claude-3-5-sonnet-20241022', role='assistant', stop_reason='tool_use', stop_sequence=None, type='message', usage=Usage(cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=403, output_tokens=71))
```
        """
        responseDict = {}
        for i in completion.content:
            if hasattr(i, "input"):
                responseDict = i.input
                break
        return responseDict

    # Auto Function Call equivalence

    @staticmethod
    def runToolCall(messages: dict):
        if not config.selectedTool:
            return CallAnthropic.regularCall(messages)
        else:
            # 2. Tool Selection
            if config.selectedTool and not config.selectedTool == "chat" and config.selectedTool in config.toolFunctionSchemas:
                tool_name = config.selectedTool
                tool_schema = config.toolFunctionSchemas[tool_name]
                config.selectedTool = ""
            else:
                return CallAnthropic.regularCall(messages)
            # 3. Parameter Extraction
            if config.developer:
                print1("extracting parameters ...")
            try:
                if not tool_schema["parameters"]["properties"]:
                    # Execute function directly
                    tool_parameters = {}
                    tool_response = executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
                else:
                    tool_parameters = CallAnthropic.getDictionaryOutput(messages=messages, schema=tool_schema)
                    if not validParameters(tool_parameters, tool_schema["parameters"]["required"]):
                        return CallAnthropic.regularCall(messages)
                    # 4. Function Execution
                    tool_response = executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
            except:
                print(traceback.format_exc())
                tool_response = "[INVALID]"
            # 5. Chat Extension
            if tool_response == "[INVALID]":
                # invalid tool call; return a regular call instead
                return CallAnthropic.regularCall(messages)
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
                            "content": tool_response if tool_response else config.toolTextOutput,
                        }
                    )
                    config.toolTextOutput = ""

                    return CallAnthropic.regularCall(messages)
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
        parameters = CallAnthropic.getDictionaryOutput(messages=ongoingMessages, schema=schema, **kwargs)
        if config.developer:
            print2("```parameters")
            pprint.pprint(parameters)
            print2("```")
        return parameters
