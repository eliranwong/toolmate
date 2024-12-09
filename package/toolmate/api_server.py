from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from toolmate import config, configFile, isServerAlive, print2, print3, getOllamaServerClient, getLlms, unloadLocalModels, changeModel, changeBackendAndModel, getCurrentModel
from toolmate.utils.assistant import ToolMate
from toolmate.utils.tool_plugins import Plugins
from toolmate.utils.call_llm import CallLLM
from toolmate.utils.config_essential import temporaryConfigs
from importlib_metadata import version as lib_version
from pydantic import BaseModel
import requests, argparse, json, uvicorn, re, os, signal, shutil, sys, pprint


# Create the parser
parser = argparse.ArgumentParser(description="ToolMate AI API server cli options")
# Add arguments
parser.add_argument('-b', '--backend', action='store', dest='backend', help="AI backend")
parser.add_argument('-k', '--key', action='store', dest='key', help="specify the API key for authenticating client access")
parser.add_argument('-m', '--model', action='store', dest='model', help="AI model; override backend option if the model's backend is different")
parser.add_argument('-mo', '--maximumoutput', action='store', dest='maximumoutput', help="override default maximum output tokens; accepts non-negative integers")
parser.add_argument('-p', '--port', action='store', dest='port', help="server port")
parser.add_argument('-s', '--server', action='store', dest='server', help="server address; '0.0.0.0' by default")
parser.add_argument('-t', '--temperature', action='store', dest='temperature', help="override default inference temperature; accepted range: 0.0-2.0")
parser.add_argument('-ws', '--windowsize', action='store', dest='windowsize', help="override default context window size; applicable to backends `llama.cpp` amd `ollama` only; accepts non-negative integers")
# Parse arguments
args = parser.parse_args()

# app object
app = FastAPI()

api_key_header = APIKeyHeader(name="X-API-Key") 

# Function to check the API key
async def get_api_key(api_key: str = Depends(api_key_header)):
    correct_key = args.key if args.key else config.toolmate_api_server_key
    if api_key != correct_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

class Request(BaseModel):
    wd: str
    backend: str | None = None
    model: str | None = None
    instruction: str | None = "."
    chat: bool | None = False
    chatfile: str | None = None
    chatsystem: str | None = None
    windowsize: str | None = None
    maximumoutput: str | None = None
    temperature: str | None = None
    defaulttool: str | None = None
    toolagent: bool | None = None
    backupchat: bool | None = None
    backupsettings: bool | None = None
    reloadsettings: bool | None = None
    powerdown: bool | None = None

@app.post("/api/toolmate")
async def process_instruction(request: Request, api_key: str = Depends(get_api_key) if config.toolmate_api_server_key else ""):
    wd = request.wd
    backend = request.backend
    model = request.model
    instruction = request.instruction
    chat = request.chat
    chatfile = request.chatfile
    chatsystem = request.chatsystem
    if chatsystem is not None:
        check = re.sub("^`([^`]+?)`$", r"\1", chatsystem)
        if check in config.predefinedChatSystemMessages:
            chatsystem = config.predefinedChatSystemMessages.get(check)
    windowsize = request.windowsize
    maximumoutput = request.maximumoutput
    temperature = request.temperature
    defaulttool = request.defaulttool
    if defaulttool is not None:
        defaulttool = re.sub("^@", "", defaulttool)
    toolagent = request.toolagent
    backupchat = request.backupchat
    backupsettings = request.backupsettings
    reloadsettings = request.reloadsettings
    powerdown = request.powerdown

    # reload configurations
    if reloadsettings:
        config.loadConfig(configFile)
        print2("Configurations reloaded!")

    # change backend
    current_llmInterface = config.llmInterface
    current_ollamaToolModel = config.ollamaToolModel
    if model and backend:
        changeBackendAndModel(backend, model)
    if model and not backend:
        changeModel(model)
    elif backend and backend.lower() in getLlms().keys():
        config.llmInterface = backend.lower()
        print3(f"Backend configured: {config.llmInterface}")
    # when backend or model is change
    if (not current_llmInterface == config.llmInterface and current_llmInterface == "ollama") or (not current_ollamaToolModel == config.ollamaToolModel):
        getOllamaServerClient().generate(model=config.ollamaToolModel, keep_alive=0, stream=False,)
        print(f"Ollama model '{config.ollamaToolModel}' unloaded!")
    elif (not current_llmInterface == config.llmInterface and current_llmInterface == "llamacpp"):
        try:
            config.llamacppToolModel.close()
            print("Llama.cpp model unloaded!")
        except:
            pass
        if hasattr(config, "llamacppToolModel"):
            del config.llamacppToolModel
    if not current_llmInterface == config.llmInterface:
        try:
            CallLLM.checkCompletion()
        except:
            print3(f"Failed to configure backend: {config.llmInterface}")
            config.llmInterface = current_llmInterface
            print3(f"Backend changed back to: {config.llmInterface}")
        if not config.llmInterface:
            config.llmInterface = current_llmInterface

    # override chat system message agent once
    if chatsystem:
        current_chatsystem = config.toolmate.getCurrentChatSystemMessage()
        config.toolmate.setCustomSystemMessage(customChatMessage=chatsystem)
        print3(f"Chat system message changed for this request: {chatsystem}")

    # override tool selection agent once
    if toolagent is not None:
        current_toolagent = config.tool_selection_agent
        config.tool_selection_agent = toolagent
        print3(f"Tool selection agent changed for this request: {toolagent}")

    # override default tool once
    if defaulttool and defaulttool in config.allEnabledTools:
        current_defaulttool = config.defaultTool
        config.defaultTool = defaulttool
        print3(f"Default tool changed for this request: {defaulttool}")

    # override context window size; applicable to backends `ollama` and `llama.cpp` only
    if windowsize and config.llmInterface in ("llamacpp", "ollama"):
        current_windowsize = config.toolmate.getCurrentContextWindowSize()
        try:
            windowsize = int(windowsize)
            if windowsize < 0:
                print2("No change in context window size! Negative values not accepted!")
            else:
                config.toolmate.setContextWindowSize(customContextWindowSize=windowsize)
                print3(f"Context window size changed for this request: {windowsize}")
        except:
            print2("No change in context window size! Non-integer values not accepted!")
    elif windowsize:
        print2("No change in context window size! This option applicable to backends `llama.cpp` and `ollama` only!")

    # override maximum output tokens once
    if maximumoutput:
        current_maximumoutput = config.toolmate.getCurrentMaxTokens(showMessage=False)
        try:
            maximumoutput = int(maximumoutput)
            if maximumoutput < 0:
                print2("No change in maximum output tokens! Negative values not accepted!")
            else:
                config.toolmate.setMaxTokens(customMaxtokens=maximumoutput)
                print3(f"Maximum output tokens changed for this request: {maximumoutput}")
        except:
            print2("No change in maximum output tokens! Non-integer values not accepted!")
    
    # override current temperature once
    if temperature:
        current_temperature = config.llmTemperature
        try:
            temperature = float(temperature)
            if temperature < 0.0 or temperature > 2.0:
                print2("No change in temperature! Given value is out of acceptted range 0.0-2.0!")
            else:
                config.toolmate.setTemperature(temperature=temperature)
                print3(f"Temperature changed for this request: {temperature}")
        except:
            print2("No change in temperature! Non-float values not accepted!")

    if os.path.isdir(wd):
        os.chdir(wd)
    if chatfile and os.path.isfile(chatfile):
        config.currentMessages = config.toolmate.loadMessages(chatfile)
        chat = True
    if not instruction == ".":
        if not chat:
            config.currentMessages = config.toolmate.resetMessages()
        config.toolmate.runMultipleActions(instruction)
    response = [i for i in config.currentMessages if i.get("role", "") in ("user", "assistant")]

    # save current conversation
    if backupchat:
        config.toolmate.saveChat(config.currentMessages)
    
    # persist changes or restore server configurations
    if backupsettings:
        config.saveConfig()
        if os.path.isdir(config.localStorage):
            shutil.copy(configFile, os.path.join(config.localStorage, "config_lite_backup.py" if config.isLite else "config_backup.py"))
    else:
        if chatsystem:
            config.toolmate.setCustomSystemMessage(customChatMessage=current_chatsystem)
            print3(f"Chat system message restored: {current_chatsystem}")
        if toolagent is not None:
            config.tool_selection_agent = current_toolagent
            print3(f"Tool selection agent restored: {current_toolagent}")
        if defaulttool and defaulttool in config.allEnabledTools:
            config.defaultTool = current_defaulttool
            print3(f"Default tool restored: {current_defaulttool}")
        if windowsize and config.llmInterface in ("llamacpp", "ollama"):
            config.toolmate.setContextWindowSize(customContextWindowSize=current_windowsize)
            print3(f"Context window size restored: {current_windowsize}")
        if maximumoutput:
            config.toolmate.setMaxTokens(customMaxtokens=current_maximumoutput)
            print3(f"Maximum output tokens restored: {current_maximumoutput}")
        if temperature:
            config.toolmate.setTemperature(temperature=current_temperature)
            print3(f"Temperature changed restored: {current_temperature}")

    if powerdown:
        unloadLocalModels()
        # kill server process
        os.kill(config.api_server_id, signal.SIGINT)

    return json.dumps(response)

@app.post("/api/status")
async def process_status(query: str, api_key: str = Depends(get_api_key) if config.toolmate_api_server_key else ""):
    if query := query.strip():
        try:
            tmversion = lib_version("toolmate")
        except:
            tmversion = f"""{lib_version("toolmate_lite")} (lite)"""
        if query == "info":
            info = {
                "Toolmate version": tmversion,
                "Python version": sys.version,
                "Python interpreter": sys.executable,
                "Library": config.toolMateAIFolder,
                "User data": config.localStorage,
                "Server host": config.this_api_server_host,
                "Server port": config.this_api_server_port,
                "AI Backend": config.llmInterface,
                "AI Model": getCurrentModel(),
                "Context window size": config.toolmate.getCurrentContextWindowSize(),
                "Maximum output token": config.toolmate.getCurrentMaxTokens(showMessage=False),
                "Temperature": config.llmTemperature,
                "Chat system message": config.toolmate.getCurrentChatSystemMessage(),
                "Tool system message": config.systemMessage_tool_current,
                "Tool agent": config.tool_selection_agent,
                "Default tool": config.defaultTool,
            }
        elif query == "models":
            info = getLlms()
        elif query == "configs":
            info = []
            for name in dir(config):
                excludeConfigList = temporaryConfigs + config.excludeConfigList
                if not name.startswith("__") and not name in excludeConfigList:
                    try:
                        value = eval(f"config.{name}")
                        if not callable(value) and not str(value).startswith("<"):
                            info.append("{0} = {1}".format(name, pprint.pformat(value)))
                    except:
                        pass
            return "\n".join(info)
        return json.dumps(info)

@app.post("/api/tools")
async def process_tools(query: str, api_key: str = Depends(get_api_key) if config.toolmate_api_server_key else ""):
    if searchPattern := query.strip():
        availableTools = Plugins.checkAvailableTools(display=False, includeRequirements=True)
        if searchPattern == "@":
            results = availableTools
        else:
            results = {key: value for key, value in availableTools.items() if re.search(searchPattern, key, re.IGNORECASE) or re.search(searchPattern, value, re.IGNORECASE)}
        return json.dumps({"results": results})

@app.post("/api/systems")
async def process_systems(query: str, api_key: str = Depends(get_api_key) if config.toolmate_api_server_key else ""):
    if searchPattern := query.strip():
        if searchPattern == "@":
            results = config.predefinedChatSystemMessages
        else:
            results = {key: value for key, value in config.predefinedChatSystemMessages.items() if re.search(searchPattern, key, re.IGNORECASE) or re.search(searchPattern, value, re.IGNORECASE)}
        return json.dumps({"results": results})

@app.post("/api/contexts")
async def process_contexts(query: str, api_key: str = Depends(get_api_key) if config.toolmate_api_server_key else ""):
    if searchPattern := query.strip():
        if searchPattern == "@":
            results = config.predefinedContexts
        else:
            results = {key: value for key, value in config.predefinedContexts.items() if re.search(searchPattern, key, re.IGNORECASE) or re.search(searchPattern, value, re.IGNORECASE)}
        return json.dumps({"results": results})

def main():
    config.this_api_server_host = host = args.server if args.server else config.toolmate_api_server_host
    config.this_api_server_port = port = args.port if args.port else config.toolmate_api_server_port
    if not isServerAlive(host, port):
        # configurations in API server
        config.initialCompletionCheck = False
        config.auto_tool_selection = True
        config.confirmExecution = 'none'
        config.ttsInput = False
        config.ttsOutput = False
        # backend
        if args.backend and args.backend.lower() in getLlms().keys():
            config.llmInterface = args.backend.lower()
            print3(f"Backend configured: {config.llmInterface}")
        if args.model:
            changeModel(args.model)
        # initiate assistant
        config.toolmate = ToolMate()
        # backend-dependent configurations
        if args.windowsize and args.windowsize.strip() and config.llmInterface in ("llamacpp", "ollama"):
            try:
                windowsize = int(args.windowsize)
                if windowsize < 0:
                    print2("No change in context window size! Negative values not accepted!")
                else:
                    config.toolmate.setContextWindowSize(customContextWindowSize=windowsize)
                    print3(f"Context window size configured: {windowsize}")
            except:
                print2("No change in context window size! Non-integer values not accepted!")
        elif args.windowsize:
            print2("No change in context window size! This option applicable to backends `llama.cpp` and `ollama` only!")
        if args.maximumoutput and args.maximumoutput.strip():
            try:
                maximumoutput = int(args.maximumoutput)
                if maximumoutput < 0:
                    print2("No change in maximum output tokens! Negative values not accepted!")
                else:
                    config.toolmate.setMaxTokens(customMaxtokens=maximumoutput)
                    print3(f"Maximum output tokens configured: {maximumoutput}")
            except:
                print2("No change in maximum output tokens! Non-integer values not accepted!")
        if args.temperature and args.temperature.strip():
            try:
                temperature = float(args.temperature)
                if temperature < 0.0 or temperature > 2.0:
                    print2("No change in temperature! Given value is out of acceptted range 0.0-2.0!")
                else:
                    config.toolmate.setTemperature(temperature=temperature)
                    print3(f"Temperature configured: {temperature}")
            except:
                print2("No change in temperature! Non-float values not accepted!")
        # say hi to test
        config.toolmate.runMultipleActions("Hi!")
        config.conversationStarted = True
        # start server
        config.api_server_id = os.getpid() # this line have to be placed in front of uvicorn.run(...)
        uvicorn.run(app, host=host, port=port)
    else:
        print2(f"Toolmate AI is up and running at {host}:{port}. Enjoy!")
        #print3("Read more: https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/ToolMate%20API%20Server.md")

if __name__ == '__main__':
    main()
