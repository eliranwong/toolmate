from toolmate import showErrors, get_or_create_collection, query_vectors, getDeviceInfo, isValidPythodCode, executeToolFunction, toParameterSchema, selectEnabledTool, useChatSystemMessage
from toolmate import print1, print2, print3, selectTool, getPythonFunctionResponse, extractPythonCode, isValidPythodCode, isToolRequired
from toolmate import config, getOllamaServerClient
import shutil, re, traceback, json, ollama, pprint, copy, datetime
from typing import Optional
from toolmate.utils.download import Downloader
from ollama import Options
from prompt_toolkit import prompt


def check_ollama_errors(func):
    def wrapper(*args, **kwargs):
        def finishError():
            config.stopSpinning()
            return "[INVALID]"
        try:
            return func(*args, **kwargs)
        except ollama.ResponseError as e:
            print1('Error:', e.error)
            return finishError()
        except:
            print(traceback.format_exc())
            return finishError()
    return wrapper


class CallOllama:

    @staticmethod
    @check_ollama_errors
    def checkCompletion():
        if shutil.which("ollama"):
            for i in (config.ollamaMainModel, config.ollamaChatModel, config.ollamaVisionModel):
                Downloader.downloadOllamaModel(i)
        else:
            print("Ollama not found! Install it first!")
            print("Check https://ollama.com")
            config.llmInterface = "llamacpp"
            config.saveConfig()
            print("LLM interface changed back to 'llamacpp'")
            #print("Restarting 'ToolMate AI' ...")
            #restartApp()

    @staticmethod
    def autoCorrectPythonCode(code, trace):
        for i in range(config.max_consecutive_auto_correction):
            userInput = f"""I encountered these errors:
```
{trace}
```

When I run the following python code:
```
{code}
```

Please rewrite the code to make it work.

Remember, give me the python code ONLY, without additional notes or explanation.
"""
            messages = [{"role": "user", "content" : userInput}]
            print3(f"Auto-correction attempt: {(i + 1)}")

            function_call_message, function_call_response = CallOllama.getSingleFunctionCallResponse(messages, "correct_python_code")
            arguments = function_call_message["function_call"]["arguments"]
            if not arguments:
                print2("Generating code ...")
                response = CallOllama.getSingleChatResponse(userInput)
                python_code = extractPythonCode(response)
                if isValidPythodCode(python_code):
                    arguments = {
                        "code": python_code,
                        "missing": [],
                        "issue": "",
                    }
                    function_call_response = executeToolFunction(arguments, "correct_python_code")
                else:
                    continue

            # display response
            print1(config.divider)
            if config.developer:
                print(function_call_response)
            else:
                print1("Executed!" if function_call_response == "EXECUTED" else "Failed!")
            if function_call_response == "EXECUTED":
                break
            else:
                code = arguments.get("code")
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

    @staticmethod
    @check_ollama_errors
    def regularCall(messages: dict, temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_batch: Optional[int]=None, num_predict: Optional[int]=None):
        chatMessages = useChatSystemMessage(copy.deepcopy(messages))
        return getOllamaServerClient().chat(
            keep_alive=config.ollamaMainModel_keep_alive,
            model=config.ollamaMainModel,
            messages=chatMessages,
            stream=True,
            options=Options(
                temperature=temperature if temperature is not None else config.llmTemperature,
                num_ctx=num_ctx if num_ctx is not None else config.ollamaMainModel_num_ctx,
                num_batch=num_batch if num_batch is not None else config.ollamaMainModel_num_batch,
                num_predict=num_predict if num_predict is not None else config.ollamaMainModel_num_predict,
                **config.ollamaMainModel_additional_options,
            ),
        )

    @staticmethod
    @check_ollama_errors
    def getDictionaryOutput(messages: list, temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_batch: Optional[int]=None, num_predict: Optional[int]=None):
        #pprint.pprint(messages)
        try:
            completion = getOllamaServerClient().chat(
                keep_alive=config.ollamaMainModel_keep_alive,
                model=config.ollamaMainModel,
                messages=messages,
                format="json",
                stream=False,
                options=Options(
                    temperature=temperature if temperature is not None else config.llmTemperature,
                    num_ctx=num_ctx if num_ctx is not None else config.ollamaMainModel_num_ctx,
                    num_batch=num_batch if num_batch is not None else config.ollamaMainModel_num_batch,
                    num_predict=num_predict if num_predict is not None else config.ollamaMainModel_num_predict,
                    **config.ollamaMainModel_additional_options,
                ),
            )
            jsonOutput = completion["message"]["content"]
            jsonOutput = re.sub("^[^{]*?({.*?})[^}]*?$", r"\1", jsonOutput)
            responseDict = json.loads(jsonOutput)
            #if config.developer:
            #    pprint.pprint(responseDict)
            return responseDict
        except:
            showErrors()
            return {}

    @staticmethod
    @check_ollama_errors
    def getSingleChatResponse(userInput: str, messages: list=[], temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_batch: Optional[int]=None, num_predict: Optional[int]=None, model: Optional[str]=None):
        # non-streaming single call
        if userInput:
            messages.append({"role": "user", "content" : userInput})
        chatMessages = useChatSystemMessage(copy.deepcopy(messages))
        try:
            completion = getOllamaServerClient().chat(
                keep_alive=config.ollamaMainModel_keep_alive,
                model=model if model is not None else config.ollamaMainModel,
                messages=chatMessages,
                stream=False,
                options=Options(
                    temperature=temperature if temperature is not None else config.llmTemperature,
                    num_ctx=num_ctx if num_ctx is not None else config.ollamaMainModel_num_ctx,
                    num_batch=num_batch if num_batch is not None else config.ollamaMainModel_num_batch,
                    num_predict=num_predict if num_predict is not None else config.ollamaMainModel_num_predict,
                    **config.ollamaMainModel_additional_options,
                ),
            )
            return completion["message"]["content"]
        except:
            return ""

    # Specific Function Call equivalence

    @staticmethod
    def runSingleFunctionCall(messages, function_name):
        messagesCopy = copy.deepcopy(messages)
        try:
            _, function_call_response = CallOllama.getSingleFunctionCallResponse(messages, function_name)
            function_call_response = function_call_response if function_call_response else config.toolTextOutput
            messages[-1]["content"] += f"""\n\nAvailable information:\n{function_call_response}"""
            config.toolTextOutput = ""
        except:
            showErrors()
            return messagesCopy
        return messages

    @staticmethod
    @check_ollama_errors
    def getSingleFunctionCallResponse(messages: list, function_name: str, temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_batch: Optional[int]=None, num_predict: Optional[int]=None):
        tool_schema = config.toolFunctionSchemas[function_name]["parameters"]
        user_request = messages[-1]["content"]
        func_arguments = CallOllama.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages, temperature=temperature, num_ctx=num_ctx, num_batch=num_batch, num_predict=num_predict)
        function_call_response = executeToolFunction(func_arguments=func_arguments, function_name=function_name)
        function_call_message_mini = {
            "role": "assistant",
            "content": "",
            "function_call": {
                "name": function_name,
                "arguments": func_arguments,
            }
        }
        return function_call_message_mini, function_call_response

    # Auto Function Call equivalence

    @staticmethod
    def runGeniusCall(messages: dict, doNotUseTool: bool = False):
        user_request = messages[-1]["content"]
        if config.enable_tool_selection_agent and config.enable_tool_screening_agent and config.tool_dependence > 0.0:
            # 1. Intent Screening
            if config.developer:
                print1("screening ...")
            doNotUseTool = True if doNotUseTool else (not isToolRequired(user_request))
        if not config.selectedTool and (doNotUseTool or config.tool_dependence <= 0.0):
            return CallOllama.regularCall(messages)
        else:
            # 2. Tool Selection
            if config.selectedTool and config.selectedTool in config.toolFunctionSchemas:
                tool_name = config.selectedTool
                tool_schema = config.toolFunctionSchemas[tool_name]["parameters"]
                config.selectedTool = ""
            else:
                if config.developer:
                    print1("selecting tool ...")
                tool_collection = get_or_create_collection(config.tool_store_client, "tools")
                search_result = query_vectors(tool_collection, user_request, config.tool_selection_max_choices)
                
                # no tool is available; return a regular call instead
                if not search_result:
                    return CallOllama.regularCall(messages)

                # check the closest distance
                closest_distance = search_result["distances"][0][0]
                
                # when a tool is irrelevant
                if closest_distance > config.tool_dependence:
                    return CallOllama.regularCall(messages)

                # auto or manual selection
                selected_index = selectTool(search_result, closest_distance)
                if selected_index is None:
                    return CallOllama.regularCall(messages)
                elif selected_index >= len(search_result["metadatas"][0]):
                    tool_name = selectEnabledTool()
                    semantic_distance = None
                    if tool_name is None:
                        return CallOllama.regularCall(messages)
                else:
                    semantic_distance = search_result["distances"][0][selected_index]
                    metadatas = search_result["metadatas"][0][selected_index]
                    tool_name = metadatas["name"]

                tool_schema = json.loads(metadatas["parameters"])
                if config.developer:
                    semantic_distance = "" if semantic_distance is None else f" ({semantic_distance})"
                    print3(f"Selected: {tool_name}{semantic_distance}")
            if tool_name == "chat":
                return CallOllama.regularCall(messages)
            elif tool_name in config.deviceInfoPlugins:
                user_request = f"""Context: Today is {config.dayOfWeek}. The current date and time here in {config.state}, {config.country} is {str(datetime.datetime.now())}.
{user_request}"""
            # 3. Parameter Extraction
            if config.developer:
                print1("extracting parameters ...")
            try:
                tool_parameters = CallOllama.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages)
                if not tool_parameters:
                    if config.developer:
                        print1("Failed to extract parameters!")
                    return CallOllama.regularCall(messages)
                # 4. Function Execution
                tool_response = executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
            except:
                print(traceback.format_exc())
                tool_response = "[INVALID]"
            # 5. Chat Extension
            if tool_response == "[INVALID]":
                # invalid tool call; return a regular call instead
                return CallOllama.regularCall(messages)
            else:
                # record tool selection
                config.currentMessages[-1]["tool"] = tool_name
                if tool_response:
                    if config.developer:
                        print2(config.divider)
                        print2("Tool output:")
                        print(tool_response)
                        print2(config.divider)
                    messages[-1]["content"] = f"""Describe the query and response below in your own words in detail, without comment about your ability.

My query:
{user_request}

Your response:
{tool_response}"""
                    return CallOllama.regularCall(messages)
                elif (not config.currentMessages[-1].get("role", "") == "assistant" and not config.currentMessages[-2].get("role", "") == "assistant") or (config.currentMessages[-1].get("role", "") == "system" and not config.currentMessages[-2].get("role", "") == "assistant"):
                    # tool function executed without chat extension
                    config.currentMessages.append({"role": "assistant", "content": config.toolTextOutput if config.toolTextOutput else "Done!"})
                    config.toolTextOutput = ""
                    config.conversationStarted = True
                    return None

    @staticmethod
    def isChatOnly(messages: dict, user_request: str) -> bool:
        
        deviceInfo = f"""\n\nMy device information:\n{getDeviceInfo()}""" if config.includeDeviceInfoInContext else ""
        schema = {
            "answer": {
                "type": "string",
                "description": """Evaluate my request to determine if it is within your capabilities as a text-based AI:
- Answer 'no' if you are asked to execute a computing task or an online search.
- Answer 'no' if you are asked for updates / news / real-time information.
- Answer 'yes' if the request is a greeting or translation.
- Answer 'yes' only if you have full information to give a direct response.""",
                "enum": ['yes', 'no'],
            },
        }
        template = {"answer": ""}
        messages_for_screening = messages[:-2] + [
            {
                "role": "system",
                "content": f"""You are a JSON builder expert. You response to my request according to the following schema:

{schema}""",
            },
            {
                "role": "user",
                "content": f"""Use the following template in your response:

{template}

Answer either yes or no as the value of the JSON key 'answer' in the template, based on the following request:

<request>
{user_request}{deviceInfo}
</request>

Remember, response in JSON with the filled template ONLY.""",
            },
        ]

        output = CallOllama.getDictionaryOutput(messages_for_screening, temperature=0.0, num_predict=20)
        return True if "yes" in str(output).lower() else False

    @staticmethod
    def extractToolParameters(schema: dict, userInput: str, ongoingMessages: list = [], temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_batch: Optional[int]=None, num_predict: Optional[int]=None) -> dict:
        """
        Extract action parameters
        """
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

            code = CallOllama.getSingleChatResponse(code_instruction, ongoingMessages[:-1]).replace(r"\\n", "\n")
            code = extractPythonCode(code, keepInvalid=True)
            if len(schema["properties"]) == 1:
                return {"code": code}
        else:
            code = ""

        codeContext = f"""

Find required code below:
{code}""" if code else ""

        properties = schemaCopy["properties"]
        template = {property: "" if properties[property]['type'] == "string" else [] for property in properties}
        
        messages = ongoingMessages[:-2] + [
            {
                "role": "system",
                "content": f"""You are a JSON builder expert. You response to my input according to the following schema:

{properties}""",
            },
            {
                "role": "user",
                "content": f"""Use the following template in your response:

{template}

Base the value of each key, in the template, on the following content and your generation:

<content>
{userInput}{codeContext}
</content>

Generate content to fill up the value of each required key in the JSON, if information is not provided.

Remember, response in JSON with the filled template ONLY.""",
            },
        ]

        parameters = CallOllama.getDictionaryOutput(messages, temperature=temperature, num_ctx=num_ctx, num_batch=num_batch, num_predict=num_predict)
        if code:
            parameters["code"] = code

        if config.developer:
            print2("```parameters")
            pprint.pprint(parameters)
            print2("```")
        return parameters