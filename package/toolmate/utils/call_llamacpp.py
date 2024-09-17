from toolmate import config, showErrors, get_or_create_collection, query_vectors, getDeviceInfo, isValidPythodCode, executeToolFunction, toParameterSchema, getCpuThreads, useChatSystemMessage
from toolmate import print1, print2, print3, selectTool, getPythonFunctionResponse, extractPythonCode, isToolRequired, encode_image, selectEnabledTool
from typing import Optional
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler
from prompt_toolkit import prompt
from pathlib import Path
from huggingface_hub import hf_hub_download
import traceback, json, re, os, pprint, copy, datetime


class CallLlamaCpp:

    @staticmethod
    def checkCompletion():

        llm_directory = os.path.join(config.localStorage, "LLMs", "gguf")
        Path(llm_directory).mkdir(parents=True, exist_ok=True)

        def loadMainModel():
            llamacppMainModel_model_path = os.path.join(llm_directory, config.llamacppMainModel_filename)
            if not config.llamacppMainModel_model_path or not os.path.isfile(config.llamacppMainModel_model_path):
                config.llamacppMainModel_model_path = llamacppMainModel_model_path
            if not os.path.isfile(config.llamacppMainModel_model_path):
                # download llava clip model
                print2("Downloading tool model ...")
                hf_hub_download(
                    repo_id=config.llamacppMainModel_repo_id,
                    filename=config.llamacppMainModel_filename,
                    local_dir=llm_directory,
                    #local_dir_use_symlinks=False,
                )
            config.llamacppMainModel = None
            cpuThreads = getCpuThreads()
            config.llamacppMainModel = Llama(
                model_path=config.llamacppMainModel_model_path,
                chat_format="chatml",
                n_ctx=config.llamacppMainModel_n_ctx,
                n_batch=config.llamacppMainModel_n_batch,
                verbose=config.llamacppMainModel_verbose,
                n_threads=cpuThreads,
                n_threads_batch=cpuThreads,
                n_gpu_layers=config.llamacppMainModel_n_gpu_layers,
                **config.llamacppMainModel_additional_model_options,
            )

        def downloadChatModel():
            llamacppChatModel_model_path = os.path.join(llm_directory, config.llamacppChatModel_filename)
            if not config.llamacppChatModel_model_path or not os.path.isfile(config.llamacppChatModel_model_path):
                config.llamacppChatModel_model_path = llamacppChatModel_model_path
            if not os.path.isfile(config.llamacppChatModel_model_path):
                # download llava clip model
                print2("Downloading chat model ...")
                hf_hub_download(
                    repo_id=config.llamacppChatModel_repo_id,
                    filename=config.llamacppChatModel_filename,
                    local_dir=llm_directory,
                    #local_dir_use_symlinks=False,
                )

        # Download main and code models
        try:
            loadMainModel()
        except:
            # restore default config
            print2("Errors! Restoring default tool model!")
            config.llamacppMainModel_ollama_tag = ""
            config.llamacppMainModel_model_path = ""
            config.llamacppMainModel_repo_id = "MaziyarPanahi/WizardLM-2-7B-GGUF"
            config.llamacppMainModel_filename = "WizardLM-2-7B.Q4_K_M.gguf"
            loadMainModel()

        try:
            downloadChatModel()
        except:
            # restore default config
            print2("Errors! Restoring default chat model!")
            config.llamacppChatModel_ollama_tag = ""
            config.llamacppChatModel_model_path = ""
            config.llamacppChatModel_repo_id = "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF"
            config.llamacppChatModel_filename = "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
            downloadChatModel()

        # Download vision model
        filename = "ggml-model-q4_k.gguf"
        llamacppVisionModel_model_path = os.path.join(llm_directory, filename)
        if not config.llamacppVisionModel_model_path or not os.path.isfile(config.llamacppVisionModel_model_path):
            config.llamacppVisionModel_model_path = llamacppVisionModel_model_path
        if not os.path.isfile(config.llamacppVisionModel_model_path):
            # download llava model
            print2(f"Downloading llava model ...")
            hf_hub_download(
                repo_id="mys/ggml_llava-v1.5-7b",
                filename=filename,
                local_dir=llm_directory,
                #local_dir_use_symlinks=False,
            )

        filename = "mmproj-model-f16.gguf"
        llamacppVisionModel_clip_model_path = os.path.join(llm_directory, filename)
        if not config.llamacppVisionModel_clip_model_path or not os.path.isfile(config.llamacppVisionModel_clip_model_path):
            config.llamacppVisionModel_clip_model_path = llamacppVisionModel_clip_model_path
        if not os.path.isfile(config.llamacppVisionModel_clip_model_path):
            # download llava clip model
            print2("Downloading clip model ...")
            hf_hub_download(
                repo_id="mys/ggml_llava-v1.5-7b",
                filename=filename,
                local_dir=llm_directory,
                #local_dir_use_symlinks=False,
            )
        
        config.saveConfig()

    @staticmethod
    def autoCorrectPythonCode(code, trace):
        for i in range(config.max_consecutive_auto_correction):
            userInput = f"""I ran this copy of python code:
```
{code}
```

However, I got the following error:
```
{trace}
```

Please generate another copy of python code that fix the error.

Remember, output the new copy of python code ONLY, without additional notes or explanation."""
            messages = [{"role": "user", "content" : userInput}]
            print3(f"Auto-correction attempt: {(i + 1)}")
            function_call_message, function_call_response = CallLlamaCpp.getSingleFunctionCallResponse(messages, "correct_python_code")
            arguments = function_call_message["function_call"]["arguments"]
            if not arguments:
                print2("Generating code ...")
                response = CallLlamaCpp.getSingleChatResponse(userInput)
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
    def regularCall(messages: dict, temperature: Optional[float]=None, max_tokens: Optional[int]=None):
        chatMessages = useChatSystemMessage(copy.deepcopy(messages))
        return config.llamacppMainModel.create_chat_completion(
            messages=chatMessages,
            temperature=temperature if temperature is not None else config.llmTemperature,
            max_tokens=max_tokens if max_tokens is not None else config.llamacppMainModel_max_tokens,
            stream=True,
            **config.llamacppMainModel_additional_chat_options,
        )

    @staticmethod
    def img_to_txt(file_path: str, query: str="Describe this image in detail please.", temperature: Optional[float]=None, max_tokens: Optional[int]=None, messages: Optional[list]=None):
        chat_handler = Llava15ChatHandler(clip_model_path=config.llamacppVisionModel_clip_model_path)
        cpuThreads = getCpuThreads()
        llm = Llama(
            model_path=config.llamacppVisionModel_model_path,
            chat_handler=chat_handler,
            logits_all=True, # needed to make llava work
            n_ctx=config.llamacppVisionModel_n_ctx, # n_ctx should be increased to accomodate the image embedding
            n_batch=config.llamacppVisionModel_n_batch,
            verbose=config.llamacppVisionModel_verbose,
            n_threads=cpuThreads,
            n_threads_batch=cpuThreads,
            n_gpu_layers=config.llamacppVisionModel_n_gpu_layers,
            **config.llamacppVisionModel_additional_model_options,
        )
        # update messages
        if messages is None:
            messages = [
                {
                    "role": "system",
                    "content": "You are an assistant who perfectly describes images.",
                },
            ]
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": encode_image(file_path)}},
                    {"type" : "text", "text": query},
                ]
            }
        )
        try:
            completion = llm.create_chat_completion(
                messages=messages,
                temperature=temperature if temperature is not None else config.llmTemperature,
                max_tokens=max_tokens if max_tokens is not None else config.llamacppVisionModel_max_tokens,
                stream=False,
                **config.llamacppVisionModel_additional_chat_options,
            )
            return completion["choices"][0]["message"].get("content", "")
        except:
            return ""

    @staticmethod
    def getDictionaryOutput(messages: list, schema: dict={}, temperature: Optional[float]=None, max_tokens: Optional[int]=None) -> dict:
        schema = toParameterSchema(schema)
        try:
            completion = config.llamacppMainModel.create_chat_completion(
                messages=messages,
                response_format={"type": "json_object", "schema": schema} if schema else {"type": "json_object"},
                temperature=temperature if temperature is not None else config.llmTemperature,
                max_tokens=max_tokens if max_tokens is not None else config.llamacppMainModel_max_tokens,
                stream=False,
                **config.llamacppMainModel_additional_chat_options,
            )
            jsonOutput = completion["choices"][0]["message"].get("content", "{}")
            jsonOutput = re.sub("^[^{]*?({.*?})[^}]*?$", r"\1", jsonOutput)
            responseDict = json.loads(jsonOutput)
            return responseDict
        except:
            showErrors()
            return {}

    @staticmethod
    def getSingleChatResponse(userInput: str, messages: list=[], temperature: Optional[float]=None, max_tokens: Optional[int]=None):
        # non-streaming single call
        if userInput:
            messages.append({"role": "user", "content" : userInput})
        chatMessages = useChatSystemMessage(copy.deepcopy(messages))
        try:
            completion = config.llamacppMainModel.create_chat_completion(
                messages=chatMessages,
                temperature=temperature if temperature is not None else config.llmTemperature,
                max_tokens=max_tokens if max_tokens is not None else config.llamacppMainModel_max_tokens,
                stream=False,
                **config.llamacppMainModel_additional_chat_options,
            )
            return completion["choices"][0]["message"].get("content", "")
        except:
            return ""

    # Specific Function call equivalence

    @staticmethod
    def runSingleFunctionCall(messages, function_name):
        messagesCopy = copy.deepcopy(messages)
        try:
            _, function_call_response = CallLlamaCpp.getSingleFunctionCallResponse(messages, function_name)
            function_call_response = function_call_response if function_call_response else config.toolTextOutput
            messages[-1]["content"] += f"""\n\nAvailable information:\n{function_call_response}"""
            config.toolTextOutput = ""
        except:
            showErrors()
            return messagesCopy
        return messages

    @staticmethod
    def getSingleFunctionCallResponse(messages: list, function_name: str, temperature: Optional[float]=None, max_tokens: Optional[int]=None):
        tool_schema = config.toolFunctionSchemas[function_name]["parameters"]
        user_request = messages[-1]["content"]
        func_arguments = CallLlamaCpp.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages, temperature=temperature, max_tokens=max_tokens)
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

    # Auto Function call equivalence

    @staticmethod
    def runGeniusCall(messages: dict, doNotUseTool: bool = False):
        user_request = messages[-1]["content"]
        if config.enable_tool_selection_agent and config.enable_tool_screening_agent and config.tool_dependence > 0.0:
            # 1. Intent Screening
            doNotUseTool = True if doNotUseTool else (not isToolRequired(user_request))
        if not config.selectedTool and (doNotUseTool or config.tool_dependence <= 0.0):
            return CallLlamaCpp.regularCall(messages)
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
                    return CallLlamaCpp.regularCall(messages)

                # check the closest distance
                closest_distance = search_result["distances"][0][0]
                
                # when a tool is irrelevant
                if closest_distance > config.tool_dependence:
                    return CallLlamaCpp.regularCall(messages)

                # auto or manual selection
                selected_index = selectTool(search_result, closest_distance)
                if selected_index is None:
                    return CallLlamaCpp.regularCall(messages)
                elif selected_index >= len(search_result["metadatas"][0]):
                    tool_name = selectEnabledTool()
                    semantic_distance = None
                    if tool_name is None:
                        return CallLlamaCpp.regularCall(messages)
                else:
                    semantic_distance = search_result["distances"][0][selected_index]
                    metadatas = search_result["metadatas"][0][selected_index]
                    tool_name = metadatas["name"]

                tool_schema = json.loads(metadatas["parameters"])
                if config.developer:
                    semantic_distance = "" if semantic_distance is None else f" ({semantic_distance})"
                    print3(f"Selected: {tool_name}{semantic_distance}")
            if tool_name == "chat":
                return CallLlamaCpp.regularCall(messages)
            elif tool_name in config.deviceInfoPlugins:
                user_request = f"""Context: Today is {config.dayOfWeek}. The current date and time here in {config.state}, {config.country} is {str(datetime.datetime.now())}.
{user_request}"""
            # 3. Parameter Extraction
            if config.developer:
                print1("extracting parameters ...")
            try:
                tool_parameters = CallLlamaCpp.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages)
                if not tool_parameters:
                    if config.developer:
                        print1("Failed to extract parameters!")
                    return CallLlamaCpp.regularCall(messages)
                # 4. Function Execution
                tool_response = executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
            except:
                print(traceback.format_exc())
                tool_response = "[INVALID]"
            # 5. Chat Extension
            if tool_response == "[INVALID]":
                # invalid tool call; return a regular call instead
                return CallLlamaCpp.regularCall(messages)
            else:
                # record tool selection
                config.currentMessages[-1]["tool"] = tool_name
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
                    return CallLlamaCpp.regularCall(messages)
                elif (not config.currentMessages[-1].get("role", "") == "assistant" and not config.currentMessages[-2].get("role", "") == "assistant") or (config.currentMessages[-1].get("role", "") == "system" and not config.currentMessages[-2].get("role", "") == "assistant"):
                    # tool function executed without chat extension
                    config.currentMessages.append({"role": "assistant", "content": config.toolTextOutput if config.toolTextOutput else "Done!"})
                    config.toolTextOutput = ""
                    config.conversationStarted = True
                    return None

    @staticmethod
    def isChatOnly(messages: dict, user_request: str) -> bool:
        
        deviceInfo = f"""\n\nMy device information:\n{getDeviceInfo()}""" if config.includeDeviceInfoInContext else ""
        answer = {
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
        schema = {
            "type": "object",
            "answer": answer,
            "required": ["answer"],
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

You will be provided with a request and you will answer either yes or no as the value of the JSON key 'answer' in the template, according to the following guidlines:
- Response {no} if you are asked to execute a computing task.
- Response {no} if you are asked to perform an internet online search.
- Response {no} if you are asked for updates / news / real-time information.
- Response {yes} if the request is kind of greeting.
- Response {yes} if you are aksed to translate.
- Response {yes} only if you have full information to give a direct response to the request.

Here is the reuqest:
<request>
{user_request}{deviceInfo}
</request>

Remember, response in JSON with the filled template ONLY.""",
            },
        ]

        output = CallLlamaCpp.getDictionaryOutput(messages_for_screening, schema=schema, temperature=0.0, max_tokens=20)
        try:
            output = output["answer"]
        except:
            return False
        return True if (not output) or str(output).lower() == "yes" else False

    @staticmethod
    def extractToolParameters_testing(schema: dict, userInput: str, ongoingMessages: list = [], temperature: Optional[float]=None, max_tokens: Optional[int]=None, **kwargs) -> dict:
        # guidance
        lm = models.LlamaCpp(
            config.llamacppMainModel_model_path,
            echo = False,
            chat_format="chatml",
            n_ctx=config.llamacppMainModel_n_ctx,
            n_batch=config.llamacppMainModel_n_batch,
            verbose=config.llamacppMainModel_verbose,
            n_gpu_layers=config.llamacppMainModel_n_gpu_layers,
            **config.llamacppMainModel_additional_model_options,
        )
        try:
            response = outputStructuredData(
                lm=lm,
                schema=schema,
                json_output=False,
                messages=ongoingMessages,
                use_system_message=False,
                request=userInput,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except:
            response = {}
        lm.reset()
        del lm
        return response

    @staticmethod
    def extractToolParameters(schema: dict, userInput: str, ongoingMessages: list = [], temperature: Optional[float]=None, max_tokens: Optional[int]=None) -> dict:
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

            code = CallLlamaCpp.getSingleChatResponse(code_instruction, ongoingMessages[:-1], temperature, max_tokens).replace(r"\\n", "\n")
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

        # schema alternative: properties if len(properties) == 1 else schema
        parameters = CallLlamaCpp.getDictionaryOutput(messages, schemaCopy, temperature=temperature, max_tokens=max_tokens)
        if code:
            parameters["code"] = code

        if config.developer:
            print2("```parameters")
            pprint.pprint(parameters)
            print2("```")
        return parameters