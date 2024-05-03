from freegenius import showErrors, get_or_create_collection, query_vectors, showRisk, executeToolFunction, getPythonFunctionResponse, getPygmentsStyle, fineTunePythonCode, confirmExecution
from freegenius import config
from freegenius import print1, print2, print3, selectTool, check_llm_errors, getGroqClient, toParameterSchema, extractPythonCode, selectEnabledTool
import re, traceback, pprint, copy, textwrap, json, pygments
from pygments.lexers.python import PythonLexer
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import prompt
from typing import Optional
from pydantic import BaseModel

class Screening(BaseModel):
    answer: str

class CallGroq:

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
            answer = CallGroq.getSingleChatResponse(content, temperature=0.0)
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
    @check_llm_errors
    def checkCompletion():
        getGroqClient().chat.completions.create(
            model=config.groqApi_main_model,
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
            function_call_message, function_call_response = CallGroq.getSingleFunctionCallResponse(messages, "correct_python")
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

    @staticmethod
    @check_llm_errors
    def getSingleChatResponse(userInput, messages=[], temperature: Optional[float]=None, max_tokens: Optional[int]=None):
        """
        non-streaming single call
        """
        messages.append({"role": "user", "content" : userInput})
        try:
            completion = getGroqClient().chat.completions.create(
                model=config.groqApi_main_model,
                messages=messages,
                n=1,
                temperature=temperature if temperature is not None else config.llmTemperature,
                max_tokens=max_tokens if max_tokens is not None else config.groqApi_max_tokens,
                stream=False,
                **config.groqApi_main_model_additional_chat_options,
            )
            return completion.choices[0].message.content
        except:
            return ""

    @staticmethod
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
            risk = CallGroq.riskAssessment(python_code)
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
                    return CallGroq.autoCorrectPythonCode(refinedCode, trace)
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
            function_call_message, function_call_response = CallGroq.getSingleFunctionCallResponse(messages, function_name)
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

    @staticmethod
    @check_llm_errors
    def getSingleFunctionCallResponse(messages: list[dict], function_name: str, temperature: Optional[float]=None, max_tokens: Optional[int]=None):
        functionSignatures = [config.toolFunctionSchemas[function_name]]
        completion = getGroqClient().chat.completions.create(
            model=config.groqApi_main_model,
            messages=messages,
            n=1,
            temperature=temperature if temperature is not None else config.llmTemperature,
            max_tokens=max_tokens if max_tokens is not None else config.groqApi_max_tokens,
            tools=CallGroq.convertFunctionSignaturesIntoTools(functionSignatures),
            tool_choice={"type": "function", "function": {"name": function_name}},
            stream=False,
            **config.groqApi_main_model_additional_chat_options,
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
        function_call_response = CallGroq.finetuneSingleFunctionCallResponse(func_arguments, function_name)
        return function_call_message_mini, function_call_response

    @staticmethod
    @check_llm_errors
    def regularCall(messages: dict, temperature: Optional[float]=None, max_tokens: Optional[int]=None):
        return getGroqClient().chat.completions.create(
            model=config.groqApi_main_model,
            messages=messages,
            n=1,
            temperature=temperature if temperature is not None else config.llmTemperature,
            max_tokens=max_tokens if max_tokens is not None else config.groqApi_max_tokens,
            stream=True,
            **config.groqApi_main_model_additional_chat_options,
        )

    @staticmethod
    @check_llm_errors
    def getDictionaryOutput(messages: list, schema: dict, temperature: Optional[float]=None, max_tokens: Optional[int]=None) -> dict:
        completion = getGroqClient().chat.completions.create(
            model=config.groqApi_main_model,
            messages=messages,
            n=1,
            temperature=temperature if temperature is not None else config.llmTemperature,
            max_tokens=max_tokens if max_tokens is not None else config.groqApi_max_tokens,
            tools=[{"type": "function", "function": schema}],
            tool_choice={"type": "function", "function": {"name": schema["name"]}},
            stream=False,
            **config.groqApi_main_model_additional_chat_options,
        )
        responseDict = json.loads(completion.choices[0].message.tool_calls[0].function.arguments)
        return responseDict

    # Auto Function Call equivalence
    @staticmethod
    def runGeniusCall(messages: dict, noFunctionCall: bool = False):
        user_request = messages[-1]["content"]
        if config.intent_screening and config.tool_dependence > 0.0:
            # 1. Intent Screening
            noFunctionCall = True if noFunctionCall else CallGroq.isChatOnly(user_request=user_request)
        if noFunctionCall or config.tool_dependence <= 0.0:
            return CallGroq.regularCall(messages)
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
                    return CallGroq.regularCall(messages)

                # check the closest distance
                closest_distance = search_result["distances"][0][0]
                
                # when a tool is irrelevant
                if closest_distance > config.tool_dependence:
                    return CallGroq.regularCall(messages)

                # auto or manual selection
                selected_index = selectTool(search_result, closest_distance)
                if selected_index is None:
                    return CallGroq.regularCall(messages)
                elif selected_index >= len(search_result["metadatas"][0]):
                    tool_name = selectEnabledTool()
                    semantic_distance = None
                    if tool_name is None:
                        return CallGroq.regularCall(messages)
                else:
                    semantic_distance = search_result["distances"][0][selected_index]
                    metadatas = search_result["metadatas"][0][selected_index]
                    tool_name = metadatas["name"]
                
                tool_schema = config.toolFunctionSchemas[tool_name]

                if config.developer:
                    semantic_distance = "" if semantic_distance is None else f" ({semantic_distance})"
                    print3(f"Selected: {tool_name}{semantic_distance}")
            if tool_name == "chat":
                return CallGroq.regularCall(messages)
            # 3. Parameter Extraction
            if config.developer:
                print1("extracting parameters ...")
            try:
                tool_parameters = CallGroq.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages)
                if not tool_parameters:
                    if config.developer:
                        print1("Failed to extract parameters!")
                    return CallGroq.regularCall(messages)
                # 4. Function Execution
                tool_response = executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
            except:
                print(traceback.format_exc())
                tool_response = "[INVALID]"
            # 5. Chat Extension
            if tool_response == "[INVALID]":
                # invalid tool call; return a regular call instead
                return CallGroq.regularCall(messages)
            else:
                # record tool selection
                #config.currentMessages[-1]["tool"] = tool_name
                if tool_response:
                    if config.developer:
                        print2(config.divider)
                        print2("Tool output:")
                        print(tool_response)
                        print2(config.divider)
                    messages[-1]["content"] = f"""Response to the following query according to given supplementary information.

Query:
<query>
{user_request}
</query>

Supplementary information:
<supplementary_information>
{tool_response}
</supplementary_information>"""
                    return CallGroq.regularCall(messages)
                elif (not config.currentMessages[-1].get("role", "") == "assistant" and not config.currentMessages[-2].get("role", "") == "assistant") or (config.currentMessages[-1].get("role", "") == "system" and not config.currentMessages[-2].get("role", "") == "assistant"):
                    # tool function executed without chat extension
                    config.currentMessages.append({"role": "assistant", "content": config.tempContent if config.tempContent else "Done!"})
                    config.tempContent = ""
                    config.conversationStarted = True
                    return None

    @staticmethod
    def isChatOnly(user_request: str) -> bool:
        print2("```screening")
        try:
            chat_completion = getGroqClient().chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a text-based language model that evaluate the nature of my request and tell me whether you can resolve it with full confidence. Output your answer in JSON. Your answer can only be either 'yes' or 'no'.\n"
                        f" The JSON object must use the schema: {json.dumps(Screening.model_json_schema(), indent=2)}",
                    },
                    {
                        "role": "user",
                        "content": f"""Answer either 'yes' or 'no' in JSON format, in response to my request:
<request>
{user_request}
</request>

Question: Tell me honesly whether you are able to resolve the above request?
- Answer 'no' if you are asked to execute a computing task or an online search.
- Answer 'no' if you are asked for updates / news / real-time information.
- Answer 'yes' if the request is a greeting or translation.
- Answer 'yes' only if you have full information to give a direct response.

Remember, answer either 'yes' or 'no' in JSON, without extra information.""",
                    },
                ],
                model=config.groqApi_main_model,
                temperature=0,
                max_tokens=20,
                stream=False,
                response_format={"type": "json_object"},
            )
            answer = Screening.model_validate_json(chat_completion.choices[0].message.content)
        except:
            # in case JSON output is failed
            print3("Error: Unable to complete screening!")
            answer = "no"
        #print(answer) # check
        answer = True if "yes" in str(answer).lower() else False
        print3(f"""Comment: Tool may {"not " if answer else ""}be required.""")
        print2("```")
        return answer

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

            code = CallGroq.getSingleChatResponse(code_instruction, ongoingMessages[:-1], temperature, max_tokens).replace(r"\\n", "\n")
            code = extractPythonCode(code, keepInvalid=True)
            if len(schema["properties"]) == 1:
                return {"code": code}
        else:
            code = ""

        codeContext = f"""

Find required code below:
{code}""" if code else ""

        messages = ongoingMessages[:-2] + [
            {
                "role": "system",
                "content": f"""You are a JSON builder expert that outputs in JSON.""",
            },
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
        parameters = CallGroq.getDictionaryOutput(messages, fullSchema, temperature, max_tokens)
        if code:
            parameters["code"] = code

        if config.developer:
            print2("```parameters")
            pprint.pprint(parameters)
            print2("```")
        return parameters
