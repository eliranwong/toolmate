from toolmate import getDeviceInfo, showErrors, get_or_create_collection, query_vectors, toGeminiMessages, executeToolFunction, extractPythonCode, useChatSystemMessage
from toolmate import print1, print2, print3, selectTool, getPythonFunctionResponse, isValidPythodCode, selectEnabledTool
from toolmate import config
from prompt_toolkit import prompt
import traceback, os, json, pprint, copy, datetime, codecs
from typing import Optional, List, Dict, Union
import vertexai
from vertexai.generative_models import GenerativeModel, FunctionDeclaration, Tool
from vertexai.generative_models._generative_models import (
    GenerationConfig,
    HarmCategory,
    HarmBlockThreshold,
)

class CallGemini:

    @staticmethod
    def getGeminiModel(tool=None):
        config.gemini_generation_config=GenerationConfig(
            temperature=config.llmTemperature, # 0.0-1.0; default 0.9
            max_output_tokens=config.gemini_max_output_tokens, # default
            candidate_count=1,
        )
        # the latest package requires tools to be placed in the `GenerativeModel` instead of `send_message`
        # read https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling#chat-samples
        return GenerativeModel(
            model_name=config.gemini_model,
            generation_config=config.gemini_generation_config,
            tools=[tool],
        ) if tool else GenerativeModel(config.gemini_model, generation_config=config.gemini_generation_config,)

    @staticmethod
    def checkCompletion():
        if os.environ["GOOGLE_APPLICATION_CREDENTIALS"] and "Vertex AI" in config.enabledGoogleAPIs:
            # initiation
            vertexai.init()
        else:
            print("Vertex AI is disabled!")
            print("Read https://github.com/eliranwong/letmedoit/wiki/Google-API-Setup for setting up Google API.")
            config.llmInterface = "llamacpp"
            config.saveConfig()
            print("LLM interface changed back to 'llamacpp'")

        # Note: BLOCK_NONE is not allowed
        config.gemini_safety_settings={
            HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

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

Remember, give me the python code ONLY, without additional notes or explanation.""" # alternative: Please generate another copy of code that fix the errors.
            messages = [{"role": "user", "content" : userInput}]
            print3(f"Auto-correction attempt: {(i + 1)}")
            function_call_message, function_call_response = CallGemini.getSingleFunctionCallResponse(messages, "correct_python_code")
            arguments = function_call_message["function_call"]["arguments"]
            if not arguments:
                print2("Generating code ...")
                response = CallGemini.getSingleChatResponse(userInput)
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
    def regularCall(messages: dict, useSystemMessage: bool=True, **kwargs):
        history, _, lastUserMessage = toGeminiMessages(messages=messages)
        #userMessage = f"{systemMessage}\n\nHere is my request:\n{lastUserMessage}" if useSystemMessage and systemMessage else lastUserMessage
        userMessage = f"{config.systemMessage_gemini}\n\nHere is my request:\n{lastUserMessage}" if useSystemMessage and config.systemMessage_gemini else lastUserMessage
        chat = CallGemini.getGeminiModel().start_chat(history=history)
        return chat.send_message(
            userMessage,
            generation_config=config.gemini_generation_config,
            safety_settings=config.gemini_safety_settings,
            stream=True,
            **kwargs,
        )

    @staticmethod
    def getDictionaryOutput(history: list, schema: dict, userMessage: str, **kwargs) -> dict:
        name, description, parameters = schema["name"], schema["description"], schema["parameters"]

        # declare a function
        function_declaration = FunctionDeclaration(
            name=name,
            description=description,
            parameters=parameters,
        )
        tool = Tool(
            function_declarations=[function_declaration],
        )

        chat = CallGemini.getGeminiModel(tool).start_chat(history=history)

        try:
            completion = chat.send_message(
                userMessage,
                safety_settings=config.gemini_safety_settings,
                stream=False,
                **kwargs,
            )
            responseDict = dict(completion.candidates[0].content.parts[0].function_call.args)
            #if config.developer:
            #    import pprint
            #    pprint.pprint(responseDict)
            return responseDict
        except:
            showErrors()
            return {}

    @staticmethod
    def getSingleChatResponse(userInput: str, history: Optional[list]=None, **kwargs) -> str:
        # non-streaming single call
        try:
            chat = CallGemini.getGeminiModel().start_chat(history=history)
            completion = chat.send_message(
                userInput,
                generation_config=config.gemini_generation_config,
                safety_settings=config.gemini_safety_settings,
                stream=False,
                **kwargs,
            )
            return completion.candidates[0].content.parts[0].text
        except:
            return ""

    # Specific Function Call equivalence

    @staticmethod
    def runSingleFunctionCall(messages: list, function_name: str) -> list:
        messagesCopy = copy.deepcopy(messages)
        try:
            _, function_call_response = CallGemini.getSingleFunctionCallResponse(messages, function_name)
            function_call_response = function_call_response if function_call_response else config.toolTextOutput
            messages[-1]["content"] += f"""\n\nAvailable information:\n{function_call_response}"""
            config.toolTextOutput = ""
        except:
            showErrors()
            return messagesCopy
        return messages

    @staticmethod
    def getSingleFunctionCallResponse(messages: list, function_name: str, **kwargs) -> List[Union[Dict, str]]:
        tool_schema = config.toolFunctionSchemas[function_name]
        user_request = messages[-1]["content"]
        func_arguments = CallGemini.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages, **kwargs)
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
            doNotUseTool = True if doNotUseTool else CallGemini.isChatOnly(messages=messages, user_request=user_request)
        if not config.selectedTool and (doNotUseTool or config.tool_dependence <= 0.0):
            return CallGemini.regularCall(messages)
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
                    return CallGemini.regularCall(messages)

                # check the closest distance
                closest_distance = search_result["distances"][0][0]
                
                # when a tool is irrelevant
                if closest_distance > config.tool_dependence:
                    return CallGemini.regularCall(messages)

                # auto or manual selection
                selected_index = selectTool(search_result, closest_distance)
                if selected_index is None:
                    return CallGemini.regularCall(messages)
                elif selected_index >= len(search_result["metadatas"][0]):
                    tool_name = selectEnabledTool()
                    semantic_distance = None
                    if tool_name is None:
                        return CallGemini.regularCall(messages)
                else:
                    semantic_distance = search_result["distances"][0][selected_index]
                    metadatas = search_result["metadatas"][0][selected_index]
                    tool_name = metadatas["name"]

                tool_schema = config.toolFunctionSchemas[tool_name]
                if config.developer:
                    semantic_distance = "" if semantic_distance is None else f" ({semantic_distance})"
                    print3(f"Selected: {tool_name}{semantic_distance}")            
            if tool_name == "chat":
                return CallGemini.regularCall(messages)
            elif tool_name in config.deviceInfoPlugins:
                user_request = f"""Context: Today is {config.dayOfWeek}. The current date and time here in {config.state}, {config.country} is {str(datetime.datetime.now())}.
{user_request}"""
            # 3. Parameter Extraction
            if config.developer:
                print1("extracting parameters ...")
            try:
                tool_parameters = CallGemini.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages)
                if not tool_parameters:
                    if config.developer:
                        print1("Failed to extract parameters!")
                    return CallGemini.regularCall(messages)
                # 4. Function Execution
                tool_response = executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
            except:
                print(traceback.format_exc())
                tool_response = "[INVALID]"
            # 5. Chat Extension
            if tool_response == "[INVALID]":
                # invalid tool call; return a regular call instead
                return CallGemini.regularCall(messages)
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
                    return CallGemini.regularCall(messages)
                elif (not config.currentMessages[-1].get("role", "") == "assistant" and not config.currentMessages[-2].get("role", "") == "assistant") or (config.currentMessages[-1].get("role", "") == "system" and not config.currentMessages[-2].get("role", "") == "assistant"):
                    # tool function executed without chat extension
                    config.currentMessages.append({"role": "assistant", "content": config.toolTextOutput if config.toolTextOutput else "Done!"})
                    config.toolTextOutput = ""
                    config.conversationStarted = True
                    return None

    @staticmethod
    def isChatOnly(messages: dict, user_request: str) -> bool:
        print2("```screening")
        deviceInfo = f"""\n\nMy device information:\n{getDeviceInfo()}""" if config.includeDeviceInfoInContext else ""
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
        userMessage = f"""Answer either 'yes' or 'no', to tell if you are able to resolve my request below as a text-based AI:

<request>
{user_request}{deviceInfo}
</request>"""

        history, *_ = toGeminiMessages(messages=messages)

        output = CallGemini.getDictionaryOutput(history, schema=schema, userMessage=userMessage)
        chatOnly = True if "yes" in str(output).lower() else False
        print3(f"""Tool may {"not " if chatOnly else ""}be required.""")
        print2("```")
        return chatOnly

    @staticmethod
    def extractToolParameters(schema: dict, userInput: str, ongoingMessages: list = [], **kwargs) -> dict:
        """
        Extract action parameters
        """

        history, _, lastUserMessage = toGeminiMessages(messages=ongoingMessages)

        deviceInfo = f"""

Here is my device information for additional reference:
<my_device_information>
{getDeviceInfo()}
</my_device_information>""" if config.includeDeviceInfoInContext else ""

        # Generate Code when required
        if "code" in schema["parameters"]["required"]:
            enforceCodeOutput = """ Remember, you should format the requested information, if any, into a string that is easily readable by humans. Use the 'print' function in the final line to display the requested information."""
            code_instruction = schema["parameters"]["properties"]["code"]["description"] + enforceCodeOutput
            code_instruction = f"""Generate python code according to the following instruction:
</instruction>
{code_instruction}
</instruction>

Here is my request:
<request>
{userInput}
</request>{deviceInfo}

Remember, response with the required python code ONLY, WITHOUT extra notes or explanations."""
            code = CallGemini.getSingleChatResponse(code_instruction, history=history)
            if len(schema["parameters"]["properties"]) == 1:
                if code := extractPythonCode(code):
                    return {"code": codecs.decode(code, "unicode_escape")}
            code = f"""The required code is given below:
<code>
{code}
</code>"""
            code = codecs.decode(code, "unicode_escape")
        else:
            code = ""
        
        userMessage = f"""<request>
{lastUserMessage}
</request>{deviceInfo}{code}

When necessary, generate content based on your knowledge."""

        parameters = CallGemini.getDictionaryOutput(history=history, schema=schema, userMessage=userMessage, **kwargs)
        # fix linebreak
        if code and "code" in parameters:
            parameters["code"] = codecs.decode(parameters["code"], "unicode_escape")

        if config.developer:
            print2("```parameters")
            pprint.pprint(parameters)
            print2("```")
        return parameters