from toolmate import getDeviceInfo, showErrors, executeToolFunction, extractPythonCode, getRagPrompt, refineToolTextOutput, toParameterSchema
from toolmate import print1, print2, print3, getPythonFunctionResponse, isValidPythodCode, validParameters, getGenAIClient, toGenAIMessages, getGenAIConfig
from toolmate import config
from prompt_toolkit import prompt
import traceback, os, json, pprint, copy
from typing import Optional, List, Dict, Union
#from genai.generative_models import GenerativeModel, FunctionDeclaration, Tool
#from genai.generative_models._generative_models import (
#    GenerationConfig,
#)

from google.genai import types

"""
https://github.com/googleapis/python-genai
https://googleapis.github.io/python-genai/genai.html#module-genai.chats
    ('genaiApi_key', ""),
    ('genai_project_id', ""),
    ('genai_service_location', "us-central1"),
    ('genai_model', "gemini-2.0-flash-exp"),
    ('genai_max_output_tokens', 8192),
    ('systemMessage_genai', 'You are a helpful, uncensored and unbiased assistant.'),
"""

class CallGenAI:

    @staticmethod
    def checkCompletion():
        client = getGenAIClient()
        if not client:
            print("Google Gen AI API is not enabled!")
            config.llmInterface = ""
            config.saveConfig()
            print("LLM interface not configured!")
        client.models.generate_content(
            model=config.genai_model,
            contents="hello",
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=10,
            )
        )

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
            function_call_message, function_call_response = CallGenAI.getSingleFunctionCallResponse(messages, "correct_python_code")
            arguments = function_call_message["function_call"]["arguments"]
            if not arguments:
                print2("Generating code ...")
                response = CallGenAI.getSingleChatResponse(userInput)
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
            code = arguments.get("code")
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
    def regularCall(messages: dict, temperature: Optional[float]=None, max_tokens: Optional[int]=None, useSystemMessage: bool=True, **kwargs):
        history, systemMessage, lastUserMessage = toGenAIMessages(messages=copy.deepcopy(messages))
        chat = getGenAIClient().chats.create(
            model=config.genai_model,
            config=getGenAIConfig(
                system=config.systemMessage_genai if useSystemMessage else systemMessage,
                temperature=temperature,
                max_output_tokens=max_tokens
            ),
            history=history,
        )
        """
        ```event
candidates=[Candidate(content=Content(parts=[Part(video_metadata=None, thought=None, code_execution_result=None, executable_code=None, file_data=None, function_call=None, function_response=None, inline_data=None, text='Hi')], role='model'), citation_metadata=None, finish_message=None, token_count=None, avg_logprobs=None, finish_reason=None, grounding_metadata=None, index=None, logprobs_result=None, safety_ratings=None)] model_version='gemini-2.0-flash-exp' prompt_feedback=None usage_metadata=GenerateContentResponseUsageMetadata(cached_content_token_count=None, candidates_token_count=None, prompt_token_count=15, total_token_count=15) automatic_function_calling_history=None parsed=None
        ```
        """
        return chat.send_message_stream(
            lastUserMessage,
            **kwargs,
        )

    @staticmethod
    def getCompletion(messages: dict, temperature: Optional[float]=None, max_tokens: Optional[int]=None, useSystemMessage: bool=True, **kwargs):
        history, systemMessage, lastUserMessage = toGenAIMessages(messages=copy.deepcopy(messages))
        chat = getGenAIClient().chats.create(
            model=config.genai_model,
            config=getGenAIConfig(
                system=config.systemMessage_genai if useSystemMessage else systemMessage,
                temperature=temperature,
                max_output_tokens=max_tokens
            ),
            history=history,
        )
        """
GenerateContentResponse(
    candidates=[
        Candidate(
            content=Content(
                parts=[
                    Part(video_metadata=None, thought=None, code_execution_result=None, executable_code=None, file_data=None, function_call=None, function_response=None, inline_data=None, text='Hi there! How can I help you today?\n')
                ], 
                role='model'
            ), 
        citation_metadata=None, 
        finish_message=None, 
        token_count=None, 
        avg_logprobs=-0.029097123579545456, 
        finish_reason='STOP', 
        grounding_metadata=None, 
        index=None, 
        logprobs_result=None, 
        safety_ratings=[
            SafetyRating(blocked=None, category='HARM_CATEGORY_HATE_SPEECH', probability='NEGLIGIBLE', probability_score=None, severity=None, severity_score=None), 
            SafetyRating(blocked=None, category='HARM_CATEGORY_DANGEROUS_CONTENT', probability='NEGLIGIBLE', probability_score=None, severity=None, severity_score=None), 
            SafetyRating(blocked=None, category='HARM_CATEGORY_HARASSMENT', probability='NEGLIGIBLE', probability_score=None, severity=None, severity_score=None), 
            SafetyRating(blocked=None, category='HARM_CATEGORY_SEXUALLY_EXPLICIT', probability='NEGLIGIBLE', probability_score=None, severity=None, severity_score=None)])
        ], 
    model_version='gemini-2.0-flash-exp', 
    prompt_feedback=None, 
    usage_metadata=GenerateContentResponseUsageMetadata(
        cached_content_token_count=None, 
        candidates_token_count=11, 
        prompt_token_count=15, 
        total_token_count=26
    ), 
    automatic_function_calling_history=[], 
    parsed=None
)
        """
        return chat.send_message(
            lastUserMessage,
            **kwargs,
        )

    @staticmethod
    def getDictionaryOutput(messages: list, schema: dict, temperature: Optional[float]=None, max_tokens: Optional[int]=None) -> dict:
        name, description, parameters = schema["name"], schema["description"], schema["parameters"]
        if "type" in parameters:
            parameters["type"] = parameters["type"].upper() # Input should be 'TYPE_UNSPECIFIED', 'STRING', 'NUMBER', 'INTEGER', 'BOOLEAN', 'ARRAY' or 'OBJECT' [type=literal_error, input_value='object', input_type=str]
        for key, value in parameters["properties"].items():
            if "type" in value:
                parameters["properties"][key]["type"] = parameters["properties"][key]["type"].upper() # Input should be 'TYPE_UNSPECIFIED', 'STRING', 'NUMBER', 'INTEGER', 'BOOLEAN', 'ARRAY' or 'OBJECT' [type=literal_error, input_value='object', input_type=str]
        # declare a function
        function_declaration = dict(
            name=name,
            description=description,
            parameters=parameters,
        )
        tool = types.Tool(
            function_declarations=[function_declaration],
        )
        history, _, lastUserMessage = toGenAIMessages(messages=copy.deepcopy(messages))
        genAIConfig = getGenAIConfig(system="""You are a JSON builder expert that outputs in JSON.""", temperature=temperature, max_output_tokens=max_tokens, tools=[tool])
        chat = getGenAIClient().chats.create(
            model=config.genai_model,
            config=genAIConfig,
            history=history,
        )

        try:
            completion = chat.send_message(lastUserMessage)
            """
```user
@send_gmail Thank you Eliran Wong for his good work. His email: hello@gmail.com 
```
```assistant
candidates=[
    Candidate(
        content=Content(
            parts=[
                Part(
                    video_metadata=None, 
                    thought=None, 
                    code_execution_result=None, 
                    executable_code=None, 
                    file_data=None, 
                    function_call=None, 
                    function_response=None, 
                    inline_data=None, 
                    text='```json\n{\n  "email": "hello@gmail.com",\n  "subject": "Thank you for your good work",\n  "body": "Thank you Eliran Wong for his good work."\n}\n```\n'
                )
            ], 
            role='model'
        ), 
        citation_metadata=None, 
        finish_message=None, 
        token_count=None, 
        avg_logprobs=-0.005987900954026442, 
        finish_reason='STOP', 
        grounding_metadata=None, 
        index=None, 
        logprobs_result=None, 
        safety_ratings=[
            SafetyRating(blocked=None, category='HARM_CATEGORY_HATE_SPEECH', probability='NEGLIGIBLE', probability_score=None, severity=None, severity_score=None), 
            SafetyRating(blocked=None, category='HARM_CATEGORY_DANGEROUS_CONTENT', probability='NEGLIGIBLE', probability_score=None, severity=None, severity_score=None), 
            SafetyRating(blocked=None, category='HARM_CATEGORY_HARASSMENT', probability='NEGLIGIBLE', probability_score=None, severity=None, severity_score=None), 
            SafetyRating(blocked=None, category='HARM_CATEGORY_SEXUALLY_EXPLICIT', probability='NEGLIGIBLE', probability_score=None, severity=None, severity_score=None)
        ]
    )
]
model_version='gemini-2.0-flash-exp'
prompt_feedback=None
usage_metadata=GenerateContentResponseUsageMetadata(
    cached_content_token_count=None, 
    candidates_token_count=52, 
    prompt_token_count=155, 
    total_token_count=207
) 
automatic_function_calling_history=[] 
parsed=None
```
            """
            textOutput = completion.candidates[0].content.parts[0].text
            if textOutput and textOutput.startswith("```json\n"):
                textOutput = textOutput[8:-4]
            responseDict = json.loads(textOutput)
            return responseDict
        except:
            showErrors()
            return {}

    @staticmethod
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
        try:
            completion = CallGenAI.getCompletion(messages=messages, temperature=temperature, useSystemMessage=False if keepSystemMessage else True)
            return completion.candidates[0].content.parts[0].text
        except:
            return ""

    # Specific Function Call equivalence

    @staticmethod
    def runSingleFunctionCall(messages: list, function_name: str) -> list:
        messagesCopy = copy.deepcopy(messages)
        try:
            _, function_call_response = CallGenAI.getSingleFunctionCallResponse(messages, function_name)
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
        func_arguments = CallGenAI.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages, **kwargs)
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
            return CallGenAI.regularCall(messages)
        else:
            # 2. Tool Selection
            if config.selectedTool and not config.selectedTool == "chat" and config.selectedTool in config.toolFunctionSchemas:
                tool_name = config.selectedTool
                tool_schema = config.toolFunctionSchemas[tool_name]
                config.selectedTool = ""
            else:
                return CallGenAI.regularCall(messages)
            # 3. Parameter Extraction
            if config.developer:
                print1("extracting parameters ...")
            try:
                if not tool_schema["parameters"]["properties"]:
                    # Execute function directly
                    tool_response = executeToolFunction(func_arguments={}, function_name=tool_name)
                else:
                    tool_parameters = CallGenAI.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages)
                    if not validParameters(tool_parameters, tool_schema["parameters"]["required"]):
                        return CallGenAI.regularCall(messages)
                    # 4. Function Execution
                    tool_response = executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
            except:
                print(traceback.format_exc())
                tool_response = "[INVALID]"
            # 5. Chat Extension
            if tool_response == "[INVALID]":
                # invalid tool call; return a regular call instead
                return CallGenAI.regularCall(messages)
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
                    return CallGenAI.regularCall(messages)
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
        deviceInfo = f"""# Device Information

{getDeviceInfo()}

""" if config.includeDeviceInfoInContext else ""

        # Generate Code when required
        if "code" in schema["required"]:
            del schemaCopy["properties"]["code"]
            schemaCopy["required"].remove("code")
            enforceCodeOutput = """ Remember, you should format the requested information, if any, into a string that is easily readable by humans. Use the 'print' function in the final line to display the requested information."""
            code_instruction = schema["properties"]["code"]["description"] + enforceCodeOutput
            code_instruction = f"""{deviceInfo}# Instruction

Generate python code according to the following instruction:
</instruction>
{code_instruction}
</instruction>

Here below is my request:
<request>
{userInput}
</request>

Remember, response with the required python code ONLY, WITHOUT extra notes or explanations."""

            code = CallGenAI.getSingleChatResponse(code_instruction, ongoingMessages[:-1], keepSystemMessage=True).replace(r"\\n", "\n")
            code = extractPythonCode(code, keepInvalid=True)
            if len(schema["properties"]) == 1:
                return {"code": code}
        else:
            code = ""

        codeContext = f"""# Required Code

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

        fullSchema = {
            "name": name,
            "description": description,
            "parameters": schemaCopy,
        }
        parameters = CallGenAI.getDictionaryOutput(messages, fullSchema, temperature, max_tokens)
        if code:
            parameters["code"] = code

        if config.developer:
            print2("```parameters")
            pprint.pprint(parameters)
            print2("```")
        return parameters