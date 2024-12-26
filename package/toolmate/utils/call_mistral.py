from toolmate import showErrors, showRisk, executeToolFunction, getPythonFunctionResponse, getPygmentsStyle, fineTunePythonCode, confirmExecution, useChatSystemMessage
from toolmate import config
from toolmate import print1, print2, print3, check_llm_errors, getMistralClient, toParameterSchema, extractPythonCode, validParameters, getRagPrompt, refineToolTextOutput
import re, traceback, pprint, copy, textwrap, json, pygments
from pygments.lexers.python import PythonLexer
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import prompt
from typing import Optional
from pydantic import BaseModel

def check_api_keys(func):
    def wrapper(*args, **kwargs):
        if isinstance(config.mistralApi_key, str):
            return func(*args, **kwargs)
        elif isinstance(config.mistralApi_key, list):
            for _ in range(len(config.mistralApi_key)):
                try:
                    output = func(*args, **kwargs)
                    break
                except:
                    print(f"Failed API Key: {config.mistralApi_key[0]}")
            return output
    return wrapper

class Screening(BaseModel):
    answer: str

class CallMistral:

    @staticmethod
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
            answer = CallMistral.getSingleChatResponse(content, temperature=0.0, keepSystemMessage=True)
            if not answer:
                answer = "high"
            answer = re.sub("[^A-Za-z]", "", answer).lower()
            if not answer in ("high", "medium", "low"):
                answer = "high"
            return answer
        except:
            return "high"

    @staticmethod
    def convertFunctionSignaturesIntoTools(functionSignatures):
        return [{"type": "function", "function": functionSignature} for functionSignature in functionSignatures]

    @staticmethod
    @check_api_keys
    @check_llm_errors
    def checkCompletion():
        getMistralClient().chat.complete(
            model=config.mistralApi_tool_model,
            messages=[{"role": "user", "content" : "hello"}],
            n=1,
            max_tokens=10,
        )

    @staticmethod
    def autoCorrectPythonCode(code, trace):
        for i in range(config.max_consecutive_auto_correction):
            userInput = f"Original python code:\n```\n{code}\n```\n\nTraceback:\n```\n{trace}\n```"
            messages = [{"role": "user", "content" : userInput}]
            print3(f"Auto-correction attempt: {(i + 1)}")
            function_call_message, function_call_response = CallMistral.getSingleFunctionCallResponse(messages, "correct_python_code")
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
    @check_api_keys
    @check_llm_errors
    def getSingleChatResponse(userInput, messages=[], temperature: Optional[float]=None, max_tokens: Optional[int]=None, prefill: Optional[str]=None, stop: Optional[list]=None, keepSystemMessage: bool=False):
        """
        non-streaming single call
        """
        if userInput:
            item = {"role": "user", "content" : userInput}
            if messages and messages[-1].get("role", "") == "assistant":
                messages.insert(-1, item)
            else:
                messages.append(item)
        chatMessages = useChatSystemMessage(copy.deepcopy(messages), mergeSystemIntoUserMessage=True, thisSystemMessage=config.systemMessage_tool_current if keepSystemMessage else "")
        chatMessagesCopy = None
        if prefill is not None:
            chatMessagesCopy = chatMessages + [{'role': 'assistant', 'content': prefill, "prefix": True}]
        try:
            completion = getMistralClient().chat.complete(
                model=config.mistralApi_tool_model,
                messages=chatMessagesCopy if chatMessagesCopy is not None else chatMessages,
                n=1,
                temperature=temperature if temperature is not None else config.llmTemperature,
                max_tokens=max_tokens if max_tokens is not None else config.mistralApi_tool_model_max_tokens,
                stream=False,
                stop=stop if stop else None,
                **config.mistralApi_tool_model_additional_chat_options,
            )
            return completion.choices[0].message.content
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
            python_code = textwrap.dedent(func_arguments)
            refinedCode = fineTunePythonCode(python_code)

            print1(config.divider)
            print2("running python code ...")
            risk = CallMistral.riskAssessment(python_code)
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
            function_args = json.loads(func_arguments)
            function_response = fuction_to_call(function_args)
        return function_response

    @staticmethod
    def runSingleFunctionCall(messages, function_name):
        messagesCopy = copy.deepcopy(messages)
        try:
            function_call_message, function_call_response = CallMistral.getSingleFunctionCallResponse(messages, function_name)
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
    @check_api_keys
    @check_llm_errors
    def getSingleFunctionCallResponse(messages: list[dict], function_name: str, temperature: Optional[float]=None, max_tokens: Optional[int]=None):
        functionSignatures = [config.toolFunctionSchemas[function_name]]
        completion = getMistralClient().chat.complete(
            model=config.mistralApi_tool_model,
            messages=messages,
            n=1,
            temperature=temperature if temperature is not None else config.llmTemperature,
            max_tokens=max_tokens if max_tokens is not None else config.mistralApi_tool_model_max_tokens,
            tools=CallMistral.convertFunctionSignaturesIntoTools(functionSignatures),
            tool_choice="any",
            stream=False,
            **config.mistralApi_tool_model_additional_chat_options,
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
        function_call_response = CallMistral.finetuneSingleFunctionCallResponse(func_arguments, function_name)
        return function_call_message_mini, function_call_response

    @staticmethod
    @check_api_keys
    @check_llm_errors
    def regularCall(messages: dict, temperature: Optional[float]=None, max_tokens: Optional[int]=None, chat_model: Optional[str]=None):
        chatMessages = useChatSystemMessage(copy.deepcopy(messages), mergeSystemIntoUserMessage=True)
        return getMistralClient().chat.stream(
            model=chat_model if chat_model is not None else config.mistralApi_tool_model,
            messages=chatMessages,
            n=1,
            temperature=temperature if temperature is not None else config.llmTemperature,
            max_tokens=max_tokens if max_tokens is not None else config.mistralApi_tool_model_max_tokens,
            **config.mistralApi_tool_model_additional_chat_options,
        )

    @staticmethod
    @check_api_keys
    @check_llm_errors
    def getDictionaryOutput(messages: list, schema: dict, temperature: Optional[float]=None, max_tokens: Optional[int]=None) -> dict:
        completion = getMistralClient().chat.complete(
            model=config.mistralApi_tool_model,
            messages=messages,
            n=1,
            temperature=temperature if temperature is not None else config.llmTemperature,
            max_tokens=max_tokens if max_tokens is not None else config.mistralApi_tool_model_max_tokens,
            tools=[{"type": "function", "function": schema}],
            tool_choice="any",
            stream=False,
            **config.mistralApi_tool_model_additional_chat_options,
        )
        responseDict = json.loads(completion.choices[0].message.tool_calls[0].function.arguments)
        return responseDict

    # Auto Function Call equivalence
    @staticmethod
    def runToolCall(messages: dict):
        user_request = messages[-1]["content"]
        if not config.selectedTool:
            return CallMistral.regularCall(messages)
        else:
            # 2. Tool Selection
            if config.selectedTool and not config.selectedTool == "chat" and config.selectedTool in config.toolFunctionSchemas:
                tool_name = config.selectedTool
                tool_schema = config.toolFunctionSchemas[tool_name]
                config.selectedTool = ""
            else:
                return CallMistral.regularCall(messages)
            # 3. Parameter Extraction
            if config.developer:
                print1("extracting parameters ...")
            try:
                if not tool_schema["parameters"]["properties"]:
                    # Execute function directly
                    tool_response = executeToolFunction(func_arguments={}, function_name=tool_name)
                else:
                    tool_parameters = CallMistral.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages)
                    if not validParameters(tool_parameters, tool_schema["parameters"]["required"]):
                        return CallMistral.regularCall(messages)
                    # 4. Function Execution
                    tool_response = executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
            except:
                print(traceback.format_exc())
                tool_response = "[INVALID]"
            # 5. Chat Extension
            if tool_response == "[INVALID]":
                # invalid tool call; return a regular call instead
                return CallMistral.regularCall(messages)
            else:
                # record tool selection
                #config.currentMessages[-1]["tool"] = tool_name
                if tool_response:
                    if config.developer:
                        print2(config.divider)
                        print2("Tool output:")
                        print(tool_response)
                        print2(config.divider)
                    messages[-1]["content"] = getRagPrompt(user_request, tool_response)
                    return CallMistral.regularCall(messages)
                elif (not config.currentMessages[-1].get("role", "") == "assistant" and not config.currentMessages[-2].get("role", "") == "assistant") or (config.currentMessages[-1].get("role", "") == "system" and not config.currentMessages[-2].get("role", "") == "assistant"):
                    # tool function executed without chat extension
                    if config.toolTextOutput:
                        config.toolTextOutput = refineToolTextOutput(config.toolTextOutput)
                    config.currentMessages.append({"role": "assistant", "content": config.toolTextOutput if config.toolTextOutput else "Done!"})
                    config.toolTextOutput = ""
                    config.conversationStarted = True
                    return None

    @staticmethod
    def extractToolParameters(schema: dict, userInput: str, ongoingMessages: list = [], temperature: Optional[float]=None, max_tokens: Optional[int]=None) -> dict:
        """
        Extract action parameters
        """
        name = schema["name"]
        description = schema["description"]
        schema = toParameterSchema(schema)
        schemaCopy = copy.deepcopy(schema)

        # Generate Code when required
        if "code" in schema["required"]:
            del schemaCopy["properties"]["code"]
            schemaCopy["required"].remove("code")
            enforceCodeOutput = """ Remember, you should format the requested information, if any, into a string that is easily readable by humans. Use the 'print' function in the final line to display the requested information."""
            code_instruction = schema["properties"]["code"]["description"] + enforceCodeOutput
            code_instruction = f"""Generate python code according to the following instruction:
</instruction>
{code_instruction}
</instruction>

Here is my request:
<request>
{userInput}
</request>

Remember, response with the required python code ONLY, WITHOUT extra notes or explanations."""

            #code = CallMistral.getSingleChatResponse(code_instruction, ongoingMessages[:-1], temperature, max_tokens, prefill="```python\n", stop=["```"], keepSystemMessage=True).replace(r"\\n", "\n")
            code = CallMistral.getSingleChatResponse(code_instruction, ongoingMessages[:-1], temperature, max_tokens, keepSystemMessage=True).replace(r"\\n", "\n")
            code = extractPythonCode(code, keepInvalid=True)
            if len(schema["properties"]) == 1:
                return {"code": code}
        else:
            code = ""

        codeContext = f"""

Find required code below:
{code}""" if code else ""

        messages = ongoingMessages[:-1] + [
            {
                "role": "user",
                "content": f"""Response in JSON based on the following content:

<content>
{userInput}{codeContext}
</content>

Generate content to fill up the value of each required key in the JSON, if information is not provided.

Remember, output in JSON.""",
            },
        ]
        messages = useChatSystemMessage(messages, thisSystemMessage="""You are a JSON builder expert that outputs in JSON.""")

        fullSchema = {
            "name": name,
            "description": description,
            "parameters": schemaCopy,
        }
        parameters = CallMistral.getDictionaryOutput(messages, fullSchema, temperature, max_tokens)
        if code:
            parameters["code"] = code

        if config.developer:
            print2("```parameters")
            pprint.pprint(parameters)
            print2("```")
        return parameters
