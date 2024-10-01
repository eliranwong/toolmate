from toolmate import getDeviceInfo, showErrors, toGeminiMessages, executeToolFunction, extractPythonCode
from toolmate import print1, print2, print3, getPythonFunctionResponse, isValidPythodCode
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

            # Note: BLOCK_NONE is not allowed
            config.gemini_safety_settings={
                HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            }

        else:
            print("Vertex AI is not enabled!")
            print("Read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Google%20Cloud%20Service%20Credential%20Setup.md for setting up Google API.")
            config.llmInterface = "llamacpp"
            config.saveConfig()
            print("LLM interface changed back to 'llamacpp'")

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
    def getSingleChatResponse(userInput: str, history: Optional[list]=None, prefill: Optional[str]=None, stop: Optional[list]=None, **kwargs) -> str:
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
    def runToolCall(messages: dict):
        user_request = messages[-1]["content"]
        if not config.selectedTool:
            return CallGemini.regularCall(messages)
        else:
            # 2. Tool Selection
            if config.selectedTool and not config.selectedTool == "chat" and config.selectedTool in config.toolFunctionSchemas:
                tool_name = config.selectedTool
                tool_schema = config.toolFunctionSchemas[tool_name]
                config.selectedTool = ""
            else:
                return CallGemini.regularCall(messages)
            if tool_name in config.deviceInfoPlugins:
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
                #config.currentMessages[-1]["tool"] = tool_name
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