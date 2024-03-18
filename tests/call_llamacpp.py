from freegenius import config
from freegenius.utils.shared_utils import SharedUtil
from freegenius.utils.download import Downloader
import re, json, traceback, pprint
from typing import Optional
from prompt_toolkit import print_formatted_text, HTML
from llama_cpp import Llama


class CallLlamaCpp:

    @staticmethod
    def checkCompletion():
        config.llamacppDefaultModel = Llama.from_pretrained(
            repo_id=config.llamacppDefaultModel_repo_id,
            filename=config.llamacppDefaultModel_filename,
            chat_format="chatml",
            n_ctx=config.llamacppDefaultModel_n_ctx,
            verbose=False,
        )
        config.llamacppCodeModel = Llama.from_pretrained(
            repo_id=config.llamacppCodeModel_repo_id,
            filename=config.llamacppCodeModel_filename,
            chat_format="chatml",
            n_ctx=config.llamacppCodeModel_n_ctx,
            verbose=False,
        )

    @staticmethod
    def regularCall(messages: dict, temperature: Optional[float]=None, max_tokens: Optional[int]=None, **kwargs):
        return config.llamacppDefaultModel.create_chat_completion(
            messages=messages,
            temperature=temperature if temperature is not None else config.llmTemperature,
            max_tokens=max_tokens if max_tokens is not None else config.llamacppDefaultModel_max_tokens,
            stream=True,
            **kwargs,
        )

    @staticmethod
    def getResponseDict(messages: list, schema: dict={}, temperature: Optional[float]=None, max_tokens: Optional[int]=None, **kwargs) -> dict:
        #pprint.pprint(messages)
        try:
            completion = config.llamacppDefaultModel.create_chat_completion(
                messages=messages,
                response_format={"type": "json_object", "schema": schema} if schema else {"type": "json_object"},
                temperature=temperature if temperature is not None else config.llmTemperature,
                max_tokens=max_tokens if max_tokens is not None else config.llamacppDefaultModel_max_tokens,
                stream=False,
                **kwargs,
            )
            jsonOutput = completion["choices"][0]["message"].get("content", "{}")
            jsonOutput = re.sub("^[^{]*?({.*?})[^}]*?$", r"\1", jsonOutput)
            responseDict = json.loads(jsonOutput)
            if config.developer:
                pprint.pprint(responseDict)
            return responseDict
        except:
            print(traceback.format_exc())
            return {}

    @staticmethod
    def getSingleChatResponse(userInput: str, temperature: Optional[float]=None, max_tokens: Optional[int]=None, **kwargs):
        # non-streaming single call
        try:
            completion = config.llamacppDefaultModel.create_chat_completion(
                messages=[{"role": "user", "content" : userInput}],
                temperature=temperature if temperature is not None else config.llmTemperature,
                max_tokens=max_tokens if max_tokens is not None else config.llamacppDefaultModel_max_tokens,
                stream=False,
                **kwargs,
            )
            return completion["choices"][0]["message"].get("content", "")
        except:
            return ""

    # Specific Function call equivalence

    @staticmethod
    def runSingleFunctionCall(messages, function_name):
        messagesCopy = messages[:]
        try:
            _, function_call_response = CallLlamaCpp.getSingleFunctionCallResponse(messages, function_name)
            function_call_response = function_call_response if function_call_response else config.tempContent
            messages[-1]["content"] += f"""\n\nAvailable information:\n{function_call_response}"""
            config.tempContent = ""
        except:
            SharedUtil.showErrors()
            return messagesCopy
        return messages

    @staticmethod
    def getSingleFunctionCallResponse(messages: list, function_name: str, temperature: Optional[float]=None, max_tokens: Optional[int]=None, **kwargs):
        tool_schema = config.chatGPTApiFunctionSignatures[function_name]["parameters"]
        user_request = messages[-1]["content"]
        func_arguments = CallLlamaCpp.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages, temperature=temperature, max_tokens=max_tokens, **kwargs)
        function_call_response = CallLlamaCpp.executeToolFunction(func_arguments=func_arguments, function_name=function_name)
        function_call_message_mini = {
            "role": "assistant",
            "content": "",
            "function_call": {
                "name": function_name,
                "arguments": func_arguments,
            }
        }
        return function_call_message_mini, function_call_response

    # Auto Function call equivalence

    @staticmethod
    def runAutoFunctionCall(messages: dict, noFunctionCall: bool = False):
        user_request = messages[-1]["content"]
        if config.intent_screening:
            # 1. Intent Screening
            if config.developer:
                config.print("screening ...")
            noFunctionCall = True if noFunctionCall else CallLlamaCpp.screen_user_request(messages=messages, user_request=user_request)
        if noFunctionCall:
            return CallLlamaCpp.regularCall(messages)
        else:
            # 2. Tool Selection
            if config.developer:
                config.print("selecting tool ...")
            tool_collection = SharedUtil.get_or_create_collection("tools")
            search_result = SharedUtil.query_vectors(tool_collection, user_request)
            if not search_result:
                # no tool is available; return a regular call instead
                return CallLlamaCpp.regularCall(messages)
            semantic_distance = search_result["distances"][0][0]
            if semantic_distance > config.tool_dependence:
                return CallLlamaCpp.regularCall(messages)
            metadatas = search_result["metadatas"][0][0]
            tool_name, tool_schema = metadatas["name"], json.loads(metadatas["parameters"])
            if config.developer:
                config.print3(f"Selected: {tool_name} ({semantic_distance})")
            # 3. Parameter Extraction
            if config.developer:
                config.print("extracting parameters ...")
            try:
                tool_parameters = CallLlamaCpp.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages)
                # 4. Function Execution
                tool_response = CallLlamaCpp.executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
            except:
                print(traceback.format_exc())
                tool_response = "[INVALID]"
            # 5. Chat Extension
            if tool_response == "[INVALID]":
                # invalid tool call; return a regular call instead
                return CallLlamaCpp.regularCall(messages)
            elif tool_response:
                if config.developer:
                    config.print2(config.divider)
                    config.print2("Tool output:")
                    print(tool_response)
                    config.print2(config.divider)
                messages[-1]["content"] = f"""Response to the following query according to given supplementary information.

Query:
<query>
{user_request}
</query>

Supplementary information:
<supplementary_information>
{tool_response}
</supplementary_information>"""
                return CallLlamaCpp.regularCall(messages)
            else:
                # tool function executed without chat extension
                config.currentMessages.append({"role": "assistant", "content": "Done!"})
                return None

    @staticmethod
    def screen_user_request(messages: dict, user_request: str) -> bool:
        # disable for now
        return False

    @staticmethod
    def screen_user_request2(messages: dict, user_request: str) -> bool:
        
        deviceInfo = f"""\n\nMy device information:\n{SharedUtil.getDeviceInfo()}""" if config.includeDeviceInfoInContext else ""
        schema = {
            "answer": {
                "type": "string",
                "description": """Either 'yes' or 'no':
- Answer 'no' if you are asked to execute a computing task.
- Answer 'no' if you are asked to perform an internet online search.
- Answer 'no' if you are asked for updates / news / real-time information.
- Answer 'yes' if the request is a greeting or translation.
- Answer 'yes' only if you have full information to give a direct response.""",
                "enum": ['yes', 'no'],
            },
        }
        template = {"answer": ""}
        yes = {'answer': 'yes'}
        no = {'answer': 'no'}
        messages_for_screening = messages[:-2] + [
            {
                "role": "system",
                "content": f"""You are a JSON builder expert that outputs in JSON.""",
            },
            {
                "role": "user",
                "content": f"""Use the following template in your response:

{template}

Answer either yes or no as the value of the JSON key 'answer' in the template, based on the following request:

<request>
{user_request}{deviceInfo}
</request>

- Output {no} if you are asked to execute a computing task.
- Output {no} if you are asked to perform an internet online search.
- Output {no} if you are asked for updates / news / real-time information.
- Output {yes} if the request is a greeting or translation.
- Output {yes} only if you have full information to give a direct response.

Remember, response in JSON with the filled template ONLY.""",
            },
        ]

        output = CallLlamaCpp.getResponseDict(messages_for_screening, schema=schema, temperature=0.0, max_tokens=20)
        try:
            output = output["answer"]
        except:
            return False
        return True if (not output) or str(output).lower() == "yes" else False

    @staticmethod
    def extractToolParameters(schema: dict, userInput: str, ongoingMessages: list = [], temperature: Optional[float]=None, max_tokens: Optional[int]=None, **kwargs) -> dict:
        """
        Extract action parameters
        """
        deviceInfo = f"""\n\nMy device information:\n{SharedUtil.getDeviceInfo()}""" if config.includeDeviceInfoInContext else ""
        if "code" in schema["properties"]:
            enforceCodeOutput = """ Remember, you should format the requested information, if any, into a string that is easily readable by humans. Use the 'print' function in the final line to display the requested information."""
            schema["properties"]["code"]["description"] += enforceCodeOutput
            code_instruction = f"""\n\nParticularly, generate python code as the value of the JSON key "code" based on the following instruction:\n{schema["properties"]["code"]["description"]}"""
        else:
            code_instruction = ""

        properties = schema["properties"]
        messages = ongoingMessages[:-2] + [
            {
                "role": "system",
                "content": f"""You are a JSON builder expert that outputs in JSON.""",
            },
            {
                "role": "user",
                "content": f"""Response in JSON based on the following content:

<content>
{userInput}{deviceInfo}
</content>

Generate content to fill up the value of each required key in the JSON, if information is not provided.{code_instruction}

Remember, output in JSON.""",
            },
        ]

        # schema alternative: properties if len(properties) == 1 else schema
        parameters = CallLlamaCpp.getResponseDict(messages, properties, temperature=temperature, max_tokens=max_tokens, **kwargs)

        # enforce code generation
        if (len(properties) == 1 or "code" in schema["required"]) and "code" in parameters and (not isinstance(parameters.get("code"), str) or not parameters.get("code").strip() or not SharedUtil.isValidPythodCode(parameters.get("code").strip())):
            messages = ongoingMessages[:-2] + [
                {
                    "role": "system",
                    "content": f"""You are a JSON builder expert that outputs in JSON.""",
                },
                {
                    "role": "user",
                    "content": f"""Generate code based on the following instruction:

{properties["code"]["description"]}

Here is my request:

<request>
{userInput}
</request>{deviceInfo}

Remember, output in JSON.""",
                },
            ]

            # switch to a dedicated model for code generation
            llamacppDefaultModel_repo_id = config.llamacppDefaultModel_repo_id
            llamacppDefaultModel_filename = config.llamacppDefaultModel_filename
            llamacppDefaultModel_n_ctx = config.llamacppDefaultModel_n_ctx
            llamacppDefaultModel_max_tokens = config.llamacppDefaultModel_max_tokens

            config.llamacppDefaultModel_repo_id = config.llamacppCodeModel_repo_id
            config.llamacppDefaultModel_filename = config.llamacppCodeModel_filename
            config.llamacppDefaultModel_n_ctx = config.llamacppCodeModel_n_ctx
            config.llamacppDefaultModel_max_tokens = config.llamacppCodeModel_max_tokens            

            code = CallLlamaCpp.getResponseDict(messages, properties["code"], temperature=temperature)
            parameters["code"] = code["code"]

            config.llamacppDefaultModel_repo_id = llamacppDefaultModel_repo_id
            config.llamacppDefaultModel_filename = llamacppDefaultModel_filename
            config.llamacppDefaultModel_n_ctx = llamacppDefaultModel_n_ctx
            config.llamacppDefaultModel_max_tokens = llamacppDefaultModel_max_tokens

        return parameters

    @staticmethod
    def executeToolFunction(func_arguments: dict, function_name: str):
        def notifyDeveloper(func_name):
            if config.developer:
                #config.print(f"running function '{func_name}' ...")
                print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Running function</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{func_name}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
        if not function_name in config.chatGPTApiAvailableFunctions:
            if config.developer:
                config.print(f"Unexpected function: {function_name}")
                config.print(config.divider)
                print(func_arguments)
                config.print(config.divider)
            function_response = "[INVALID]"
        else:
            notifyDeveloper(function_name)
            function_response = config.chatGPTApiAvailableFunctions[function_name](func_arguments)
        return function_response