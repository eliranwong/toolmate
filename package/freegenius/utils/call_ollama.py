from freegenius import showErrors, get_or_create_collection, query_vectors, getDeviceInfo, isValidPythodCode, executeToolFunction, toParameterSchema
from freegenius import print1, print2, print3, selectTool, restartApp
from freegenius import config
import shutil, re, traceback, json, ollama
from typing import Optional
from freegenius.utils.download import Downloader
from ollama import Options


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
            for i in (config.ollamaDefaultModel, config.ollamaCodeModel):
                Downloader.downloadOllamaModel(i)
        else:
            print("Ollama not found! Install it first!")
            print("Check https://ollama.com")
            config.llmBackend = "llamacpp"
            config.saveConfig()
            print("LLM backend changed back to 'llamacpp'")
            print("Restarting 'FreeGenius AI' ...")
            restartApp()

    @staticmethod
    @check_ollama_errors
    def autoHealPythonCode(code, trace):
        ...

    @staticmethod
    @check_ollama_errors
    def regularCall(messages: dict, temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_predict: Optional[int]=None, **kwargs):
        return ollama.chat(
            keep_alive=config.ollamaDefaultModel_keep_alive,
            model=config.ollamaDefaultModel,
            messages=messages,
            stream=True,
            options=Options(
                temperature=temperature if temperature is not None else config.llmTemperature,
                num_ctx=num_ctx if num_ctx is not None else config.ollamaDefaultModel_num_ctx,
                num_predict=num_predict if num_predict is not None else config.ollamaDefaultModel_num_predict,
            ),
            **kwargs,
        )

    @staticmethod
    @check_ollama_errors
    def getResponseDict(messages: list, temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_predict: Optional[int]=None, **kwargs):
        #pprint.pprint(messages)
        try:
            completion = ollama.chat(
                #keep_alive=config.ollamaDefaultModel_keep_alive,
                model=config.ollamaDefaultModel,
                messages=messages,
                format="json",
                stream=False,
                options=Options(
                    temperature=temperature if temperature is not None else config.llmTemperature,
                    num_ctx=num_ctx if num_ctx is not None else config.ollamaDefaultModel_num_ctx,
                    num_predict=num_predict if num_predict is not None else config.ollamaDefaultModel_num_predict,
                ),
                **kwargs,
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
    def getSingleChatResponse(userInput: str, messages: list=[], temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_predict: Optional[int]=None, **kwargs):
        # non-streaming single call
        messages.append({"role": "user", "content" : userInput})
        try:
            completion = ollama.chat(
                model=config.ollamaDefaultModel,
                messages=messages,
                stream=False,
                options=Options(
                    temperature=temperature if temperature is not None else config.llmTemperature,
                    num_ctx=num_ctx if num_ctx is not None else config.ollamaDefaultModel_num_ctx,
                    num_predict=num_predict if num_predict is not None else config.ollamaDefaultModel_num_predict,
                ),
                **kwargs,
            )
            return completion["message"]["content"]
        except:
            return ""

    # Specific Function Call equivalence

    @staticmethod
    def runSingleFunctionCall(messages, function_name):
        messagesCopy = messages[:]
        try:
            _, function_call_response = CallOllama.getSingleFunctionCallResponse(messages, function_name)
            function_call_response = function_call_response if function_call_response else config.tempContent
            messages[-1]["content"] += f"""\n\nAvailable information:\n{function_call_response}"""
            config.tempContent = ""
        except:
            showErrors()
            return messagesCopy
        return messages

    @staticmethod
    @check_ollama_errors
    def getSingleFunctionCallResponse(messages: list, function_name: str, temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_predict: Optional[int]=None, **kwargs):
        tool_schema = config.toolFunctionSchemas[function_name]["parameters"]
        user_request = messages[-1]["content"]
        func_arguments = CallOllama.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages, temperature=temperature, num_ctx=num_ctx, num_predict=num_predict, **kwargs)
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
    def runAutoFunctionCall(messages: dict, noFunctionCall: bool = False):
        user_request = messages[-1]["content"]
        if config.intent_screening:
            # 1. Intent Screening
            if config.developer:
                print1("screening ...")
            noFunctionCall = True if noFunctionCall else CallOllama.screen_user_request(messages=messages, user_request=user_request)
        if noFunctionCall or config.tool_dependence <= 0.0:
            return CallOllama.regularCall(messages)
        else:
            # 2. Tool Selection
            if config.developer:
                print1("selecting tool ...")
            tool_collection = get_or_create_collection("tools")
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
            else:
                semantic_distance = search_result["distances"][0][selected_index]
                metadatas = search_result["metadatas"][0][selected_index]

            tool_name, tool_schema = metadatas["name"], json.loads(metadatas["parameters"])
            if config.developer:
                print3(f"Selected: {tool_name} ({semantic_distance})")
            # 3. Parameter Extraction
            if config.developer:
                print1("extracting parameters ...")
            try:
                tool_parameters = CallOllama.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages)
                # 4. Function Execution
                tool_response = executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
            except:
                print(traceback.format_exc())
                tool_response = "[INVALID]"
            # 5. Chat Extension
            if tool_response == "[INVALID]":
                # invalid tool call; return a regular call instead
                return CallOllama.regularCall(messages)
            elif tool_response:
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
            else:
                # tool function executed without chat extension
                config.currentMessages.append({"role": "assistant", "content": "Done!"})
                return None

    @staticmethod
    def screen_user_request(messages: dict, user_request: str) -> bool:
        
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

        output = CallOllama.getResponseDict(messages_for_screening, temperature=0.0, num_predict=20)
        return True if "yes" in str(output).lower() else False

    @staticmethod
    def extractToolParameters(schema: dict, userInput: str, ongoingMessages: list = [], temperature: Optional[float]=None, num_ctx: Optional[int]=None, num_predict: Optional[int]=None, **kwargs) -> dict:
        """
        Extract action parameters
        """
        
        schema = toParameterSchema(schema)
        deviceInfo = f"""\n\nMy device information:\n{getDeviceInfo()}""" if config.includeDeviceInfoInContext else ""
        if "code" in schema["properties"]:
            enforceCodeOutput = """ Remember, you should format the requested information, if any, into a string that is easily readable by humans. Use the 'print' function in the final line to display the requested information."""
            schema["properties"]["code"]["description"] += enforceCodeOutput
            code_instruction = f"""\n\nParticularly, generate python code as the value of the JSON key "code" based on the following instruction:\n{schema["properties"]["code"]["description"]}"""
        else:
            code_instruction = ""

        properties = schema["properties"]
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
{userInput}{deviceInfo}
</content>

Generate content to fill up the value of each required key in the JSON, if information is not provided.{code_instruction}

Remember, response in JSON with the filled template ONLY.""",
            },
        ]

        parameters = CallOllama.getResponseDict(messages, temperature=temperature, num_ctx=num_ctx, num_predict=num_predict, **kwargs)

        # enforce code generation
        if (len(properties) == 1 or "code" in schema["required"]) and "code" in parameters and (not isinstance(parameters.get("code"), str) or not parameters.get("code").strip() or not isValidPythodCode(parameters.get("code").strip())):
            template = {"code": ""}
            messages = ongoingMessages[:-2] + [
                {
                    "role": "system",
                    "content": f"""You are a JSON builder expert. You response to my input according to the following schema:

{properties["code"]}""",
                },
                {
                    "role": "user",
                    "content": f"""Use the following template in your response:

{template}

Fill in the value of key "code", in the template, by code generation:

{properties["code"]["description"]}

Here is my request:

<request>
{userInput}
</request>{deviceInfo}

Remember, answer in JSON with the filled template ONLY.""",
                },
            ]

            # switch to a dedicated model for code generation
            ollamaDefaultModel = config.ollamaDefaultModel
            ollamaDefaultModel_num_ctx = config.ollamaDefaultModel_num_ctx
            ollamaDefaultModel_num_predict = config.ollamaDefaultModel_num_predict

            config.ollamaDefaultModel = config.ollamaCodeModel
            config.ollamaDefaultModel_num_ctx = config.ollamaCodeModel_num_ctx
            config.ollamaDefaultModel_num_predict = config.ollamaCodeModel_num_predict

            code = CallOllama.getResponseDict(messages, temperature=temperature, num_ctx=num_ctx, num_predict=num_predict, **kwargs)
            parameters["code"] = code["code"]

            config.ollamaDefaultModel = ollamaDefaultModel
            config.ollamaDefaultModel_num_ctx = ollamaDefaultModel_num_ctx
            config.ollamaDefaultModel_num_predict = ollamaDefaultModel_num_predict

        return parameters