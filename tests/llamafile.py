# keep for reference; does not output in JSON consistently

class CallLlamaFile:
    # not workable yet; may not support it

    @staticmethod
    def runGeniusCall(messages: dict, noFunctionCall: bool = False):
        user_request = messages[-1]["content"]
        if config.intent_screening and config.tool_dependence > 0.0:
            # 1. Intent Screening
            if config.developer:
                print1("screening ...")
            noFunctionCall = True if noFunctionCall else CallOllama.screen_user_request(messages=messages, user_request=user_request, model=config.ollamaMainModel)
        if noFunctionCall:
            return CallOllama.regularCall(messages)
        else:
            # 2. Tool Selection
            if config.developer:
                print1("selecting tool ...")
            tool_collection = SharedUtil.get_or_create_collection("tools")
            search_result = SharedUtil.query_vectors(tool_collection, user_request)
            if not search_result:
                # no tool is available; return a regular call instead
                return CallOllama.regularCall(messages)
            semantic_distance = search_result["distances"][0][0]
            if semantic_distance > config.tool_dependence:
                return CallOllama.regularCall(messages)
            metadatas = search_result["metadatas"][0][0]
            tool_name, tool_schema = metadatas["name"], json.loads(metadatas["parameters"])
            if config.developer:
                print3(f"Selected: {tool_name} ({semantic_distance})")
            # 3. Parameter Extraction
            if config.developer:
                print1("extracting parameters ...")
            try:
                tool_parameters = CallOllama.extractToolParameters(schema=tool_schema, userInput=user_request, ongoingMessages=messages)
                # 4. Function Execution
                tool_response = CallOllama.executeToolFunction(func_arguments=tool_parameters, function_name=tool_name)
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

Query:
{user_request}

Response:
{tool_response}"""
                return CallOllama.regularCall(messages)
            else:
                # tool function executed without chat extension
                config.currentMessages.append({"role": "assistant", "content": config.tempContent if config.tempContent else "Done!"})
                config.tempContent = ""
                return None

    @staticmethod
    def regularCall(messages: dict):
        llamaFileClient = OpenAI(
            base_url="http://localhost:8080/v1", #make sure that Llamafile server is running on 8080
            api_key = "sk-no-key-required"
        )
        return llamaFileClient.chat.completions.create(
            model="LLaMA_CPP",
            messages=messages,
            n=1,
            temperature=config.llmTemperature,
            #max_tokens=SharedUtil.getDynamicTokens(messages),
            stream=True,
        )

    @staticmethod
    def screen_user_request(messages: dict, user_request: str, model: str) -> bool:
        # disable it for now
        return False

    @staticmethod
    def getDictionaryOutput(messages, **kwargs):
        #pprint.pprint(messages)
        try:
            llamaFileClient = OpenAI(
                base_url="http://localhost:8080/v1", #make sure that Llamafile server is running on 8080
                api_key = "sk-no-key-required"
            )
            completion = llamaFileClient.chat.completions.create(
                model="LLaMA_CPP",
                response_format = {"type": "json_object"},
                messages=messages,
                n=1,
                temperature=config.llmTemperature,
                #max_tokens=SharedUtil.getDynamicTokens(messages),
                stream=False,
                **kwargs,
            )
            jsonOutput = completion.choices[0].message.content

            jsonOutput = re.sub("^[^{]*?({.*?})[^}]*?$", r"\1", jsonOutput)
            responseDict = json.loads(jsonOutput)
            if config.developer:
                pprint.pprint(responseDict)
            return responseDict
        except:
            print(traceback.format_exc())
            return {}

    @staticmethod
    def extractToolParameters(schema: dict, userInput: str, ongoingMessages: list = []) -> dict:
        """
        Extract action parameters
        """
        
        deviceInfo = f"""\n\nMy device information:\n{SharedUtil.getDeviceInfo()}""" if config.includeDeviceInfoInContext else ""
        if "code" in schema["properties"]:
            enforceCodeOutput = """ Remember, you should format the requested information, if any, into a string that is easily readable by humans. Use the 'print' function in the final line to display the requested information."""
            schema["properties"]["code"]["description"] += enforceCodeOutput

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

Remember, generate values when required and answer in JSON with the filled template ONLY.""",
            },
        ]

        parameters = CallOllama.getDictionaryOutput(messages)

        # enforce code generation
        if "code" in schema["required"] and "code" in parameters and not parameters.get("code").strip():
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
            ollamaMainModel = config.ollamaMainModel
            config.ollamaMainModel = config.ollamaChatModel
            code = CallOllama.getDictionaryOutput(messages)
            parameters["code"] = code["code"]
            config.ollamaMainModel = ollamaMainModel
        return parameters

    @staticmethod
    def executeToolFunction(func_arguments, function_name):
        def notifyDeveloper(func_name):
            if config.developer:
                #print1(f"running function '{func_name}' ...")
                print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>Running function</{config.terminalPromptIndicatorColor2}> <{config.terminalCommandEntryColor2}>'{func_name}'</{config.terminalCommandEntryColor2}> <{config.terminalPromptIndicatorColor2}>...</{config.terminalPromptIndicatorColor2}>"))
        if not function_name in config.toolFunctionMethods:
            if config.developer:
                print1(f"Unexpected function: {function_name}")
                print1(config.divider)
                print(func_arguments)
                print1(config.divider)
            function_response = "[INVALID]"
        else:
            notifyDeveloper(function_name)
            function_response = config.toolFunctionMethods[function_name](func_arguments)
        return function_response