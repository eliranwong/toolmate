from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from toolmate import config, configFile, isServerAlive, print2, print3, getOllamaServerClient, getLlms, unloadLocalModels, changeModel, changeBackendAndModel, getCurrentModel, get_wan_ip, get_local_ip, getFabricPatternSystem
from toolmate.utils.assistant import ToolMate
from toolmate.utils.tool_plugins import Plugins
from toolmate.utils.call_llm import CallLLM
from toolmate.utils.config_essential import temporaryConfigs
from importlib_metadata import version as lib_version
from pydantic import BaseModel
import argparse, json, uvicorn, re, os, signal, sys, pprint


# Create the parser
parser = argparse.ArgumentParser(description=f"ToolMate AI API server `tmserver` cli options; run `tmconfigs` to view configurations; run `tmsetup` to edit configurations; run `tmsetup -h` to check for setup options; configurations are stored in `{configFile}`")
# Add arguments
parser.add_argument('-b', '--backend', action='store', dest='backend', help="AI backend")
parser.add_argument('-k', '--key', action='store', dest='key', help="specify the API key for authenticating client access")
parser.add_argument('-m', '--model', action='store', dest='model', help="AI model; override backend option if the model's backend is different")
parser.add_argument('-mo', '--maximumoutput', action='store', dest='maximumoutput', type=int, help="override default maximum output tokens; accepts non-negative integers")
parser.add_argument('-p', '--port', action='store', dest='port', type=int, help="server port")
parser.add_argument('-rt', '--riskthreshold', action='store', dest='riskthreshold', type=int, help="risk threshold for user confirmation before code execution; 0 - always require confirmation; 1 - require confirmation only when risk level is medium or higher; 2 - require confirmation only when risk level is high or higher; 3 or higher - no confirmation required")
parser.add_argument('-s', '--server', action='store', dest='server', help="server address; '0.0.0.0' by default")
parser.add_argument('-t', '--temperature', action='store', dest='temperature', type=float, help="override default inference temperature; acceptable range: 0.0-2.0")
parser.add_argument('-ws', '--windowsize', action='store', dest='windowsize', type=int, help="override default context window size; applicable to backends `llama.cpp` amd `ollama` only; accepts non-negative integers")
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
    chatpattern: str | None = None
    chatsystem: str | None = None
    windowsize: int | None = None
    maximumoutput: int | None = None
    temperature: float | None = None
    defaulttool: str | None = None
    toolagent: bool | None = None
    riskthreshold: int | None = None
    execute: bool | None = None
    improveprompt: bool | None = None
    autorag: bool | None = None
    groupexecuteindocker: bool | None = None
    groupexecutiontimeout: int | None = None
    groupoaiassistant: bool | None = None
    groupagents: int | None = None
    grouprounds: int | None = None
    imagehd: bool | None = None
    imageheight: int | None = None
    imagewidth: int | None = None
    imagesteps: int | None = None
    markdown: bool | None = None
    wordwrap: bool | None = None
    backupconversation: bool | None = None
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
    chatpattern = request.chatpattern
    chatsystem = request.chatsystem
    if chatsystem is not None:
        check = re.sub("^`([^`]+?)`$", r"\1", chatsystem)
        if check in config.predefinedChatSystemMessages:
            chatsystem = config.predefinedChatSystemMessages.get(check)
        elif system := getFabricPatternSystem(check):
            chatsystem = system
    elif chatpattern:
        chatsystem = getFabricPatternSystem(chatpattern)
    windowsize = request.windowsize
    maximumoutput = request.maximumoutput
    temperature = request.temperature
    defaulttool = request.defaulttool
    if defaulttool is not None:
        defaulttool = re.sub("^@", "", defaulttool)
    toolagent = request.toolagent
    riskthreshold = request.riskthreshold
    improveprompt = request.improveprompt
    execute = request.execute
    autorag = request.autorag
    groupexecuteindocker = request.groupexecuteindocker
    groupexecutiontimeout = request.groupexecutiontimeout
    groupoaiassistant = request.groupoaiassistant
    groupagents = request.groupagents
    grouprounds = request.grouprounds
    imagehd = request.imagehd
    imageheight = request.imageheight
    imagewidth = request.imagewidth
    imagesteps = request.imagesteps
    markdown = request.markdown
    wordwrap = request.wordwrap
    backupconversation = request.backupconversation
    backupsettings = request.backupsettings
    reloadsettings = request.reloadsettings
    powerdown = request.powerdown

    # reload configurations
    if reloadsettings:
        config.loadConfig(configFile)
        print2("Configurations reloaded!")
        Plugins.runPlugins()
        print2("Plugins reloaded!")

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
        getOllamaServerClient().generate(model=current_ollamaToolModel, keep_alive=0, stream=False,)
        print(f"Ollama model '{current_ollamaToolModel}' unloaded!")
    elif (not current_llmInterface == config.llmInterface and current_llmInterface == "llamacpppython"):
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

    # toggle tool selection agent once
    if toolagent:
        current_toolagent = config.tool_selection_agent
        config.tool_selection_agent = not config.tool_selection_agent
        print3(f"Tool selection agent changed for this request: {config.tool_selection_agent}")

    # toggle user prompt improvement once
    if improveprompt:
        current_improveInputEntry = config.improveInputEntry
        config.improveInputEntry = not config.improveInputEntry
        print3(f"Tool selection agent changed for this request: {config.improveInputEntry}")

    # override default tool once
    if defaulttool and defaulttool in config.allEnabledTools:
        current_defaulttool = config.defaultTool
        config.defaultTool = defaulttool
        print3(f"Default tool changed for this request: {defaulttool}")

    # override context window size; applicable to backends `ollama` and `llama.cpp` only
    if windowsize is not None:
        if config.llmInterface in ("llamacpppython", "ollama"):
            current_windowsize = config.toolmate.getCurrentContextWindowSize()
            if windowsize < 0:
                print2("No change in context window size! Negative values not accepted!")
            else:
                config.toolmate.setContextWindowSize(customContextWindowSize=windowsize)
                print3(f"Context window size changed for this request: {windowsize}")
        else:
            print2("No change in context window size! This option is applicable to backends `llama.cpp` and `ollama` only!")

    # override maximum output tokens once
    if maximumoutput is not None:
        current_maximumoutput = config.toolmate.getCurrentMaxTokens(showMessage=False)
        if maximumoutput < 0:
            print2("No change in maximum output tokens! Negative values not accepted!")
        else:
            config.toolmate.setMaxTokens(customMaxtokens=maximumoutput)
            print3(f"Maximum output tokens changed for this request: {maximumoutput}")

    # override current temperature once
    if temperature:
        current_temperature = config.llmTemperature
        if temperature < 0.0 or temperature > 2.0:
            print2("No change in temperature! Given value is out of acceptted range 0.0-2.0!")
        else:
            config.toolmate.setTemperature(temperature=temperature)
            print3(f"Temperature changed for this request: {temperature}")

    # override AutoGen utilities configurations
    if autorag:
        current_autorag = config.rag_useAutoRetriever
        config.rag_useAutoRetriever = autorag
    if groupexecuteindocker:
        current_groupexecuteindocker = config.code_execution_use_docker
        config.code_execution_use_docker = groupexecuteindocker
    if groupoaiassistant:
        current_groupoaiassistant = config.use_oai_assistant
        config.use_oai_assistant = groupoaiassistant
    if groupagents:
        current_groupagents = config.max_agents
        config.max_agents = groupagents
    if groupexecutiontimeout:
        current_groupexecutiontimeout = config.code_execution_timeout
        config.code_execution_timeout = groupexecutiontimeout
    if grouprounds:
        current_grouprounds = config.max_group_chat_round
        config.max_group_chat_round = grouprounds

    # override image parameters
    if imagehd:
        current_imagehd = config.imagehd
        config.imagehd = imagehd
    if imageheight and imageheight > 0:
        config.imageheight = imageheight
    if imagewidth and imagewidth > 0:
        config.imagewidth = imagewidth
    if imagesteps and imagesteps > 0:
        config.imagesteps = imagesteps

    # override risk threshold
    if execute or (riskthreshold is not None and riskthreshold >= 0):
        current_riskThreshold = config.riskThreshold
        config.riskThreshold = 3 if execute else riskthreshold
        print3(f"Risk threshold changed for this request: {config.riskThreshold}")

    # Main work
    if os.path.isdir(wd):
        os.chdir(wd)
    if chatfile and os.path.isfile(chatfile):
        config.currentMessages = config.toolmate.loadMessages(chatfile)
        chat = True
    if not instruction == ".":
        if not chat:
            config.currentMessages = config.toolmate.resetMessages()
        config.toolmate.runMultipleActions(instruction)
    if execute:
        config.toolmate.runMultipleActions("@command" if "```command" in config.currentMessages[-1].get("content", "") else "@execute_python_code")
    response = [i for i in config.currentMessages if i.get("role", "") in ("user", "assistant")]

    # save current conversation
    if backupconversation:
        config.toolmate.saveChat(config.currentMessages)
    
    # persist changes or restore server configurations
    if backupsettings:
        if markdown:
            config.toolmate_api_client_markdown = not config.toolmate_api_client_markdown
        if wordwrap:
            config.wrapWords = not config.wrapWords
        config.saveConfig()
    else:
        if autorag:
            config.rag_useAutoRetriever = current_autorag
            print3(f"Auto-retriever option restored: {current_autorag}")
        if groupexecuteindocker:
            config.code_execution_use_docker = current_groupexecuteindocker
            print3(f"Group chat code execution in docker restored: {current_groupexecuteindocker}")
        if groupexecutiontimeout:
            config.code_execution_timeout = current_groupexecutiontimeout
            print3(f"Group chat timeout for each code execution restored: {current_groupexecutiontimeout}")
        if groupoaiassistant:
            config.use_oai_assistant = current_groupoaiassistant
            print3(f"OpenAI assistant option restored: {current_groupoaiassistant}")
        if groupagents:
            config.max_agents = current_groupagents
            print3(f"Group chat maximum agents restored: {current_groupagents}")
        if grouprounds:
            config.max_group_chat_round = current_grouprounds
            print3(f"Group chat maximum rounds restored: {current_grouprounds}")
        if imagehd:
            config.imagehd = current_imagehd
        if imageheight and imageheight > 0:
            config.imageheight = None
        if imagewidth and imagewidth > 0:
            config.imagewidth = None
        if imagesteps and imagesteps > 0:
            config.imagesteps = None
        if chatsystem:
            config.toolmate.setCustomSystemMessage(customChatMessage=current_chatsystem)
            print3(f"Chat system message restored: {current_chatsystem}")
        if toolagent:
            config.tool_selection_agent = current_toolagent
            print3(f"Tool selection agent restored: {current_toolagent}")
        if improveprompt:
            config.improveInputEntry = current_improveInputEntry
            print3(f"Tool selection agent restored: {current_improveInputEntry}")
        if defaulttool and defaulttool in config.allEnabledTools:
            config.defaultTool = current_defaulttool
            print3(f"Default tool restored: {current_defaulttool}")
        if windowsize and config.llmInterface in ("llamacpppython", "ollama"):
            config.toolmate.setContextWindowSize(customContextWindowSize=current_windowsize)
            print3(f"Context window size restored: {current_windowsize}")
        if maximumoutput:
            config.toolmate.setMaxTokens(customMaxtokens=current_maximumoutput)
            print3(f"Maximum output tokens restored: {current_maximumoutput}")
        if temperature:
            config.toolmate.setTemperature(temperature=current_temperature)
            print3(f"Temperature changed restored: {current_temperature}")
        if execute or riskthreshold is not None:
            config.riskThreshold = current_riskThreshold
            print3(f"Risk threshold restored: {current_riskThreshold}")

    if powerdown:
        unloadLocalModels()
        # kill server process
        os.kill(config.api_server_id, signal.SIGINT)

    return json.dumps(response)

@app.post("/api/status")
async def process_status(query: str, api_key: str = Depends(get_api_key) if config.toolmate_api_server_key else ""):
    if query := query.strip():
        if query == "information":
            try:
                tmversion = lib_version("toolmate")
            except:
                tmversion = f"""{lib_version("toolmate_lite")} (lite)"""
            info = {
                "Toolmate version": tmversion,
                "Python version": sys.version,
                "Python interpreter": sys.executable,
                "Path - configurations": configFile,
                "Path - library": config.toolMateAIFolder,
                "Path - user data": config.localStorage,
                "IP address (wan)": get_wan_ip(),
                "IP address (local)": get_local_ip(),
                "Server host": config.this_api_server_host,
                "Server port": config.this_api_server_port,
                "AI Backend": config.llmInterface,
                "AI Model": getCurrentModel(),
                "Model context window size": config.toolmate.getCurrentContextWindowSize(),
                "Model maximum output token": config.toolmate.getCurrentMaxTokens(showMessage=False),
                "Model temperature": config.llmTemperature,
                "System message - chat": config.toolmate.getCurrentChatSystemMessage(),
                "System message - tool": config.systemMessage_tool_current,
                "Tool agent": config.tool_selection_agent,
                "Tool risk threshold": config.riskThreshold,
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
        if args.riskthreshold is not None and args.riskthreshold >= 0:
            config.riskThreshold = args.riskthreshold
        if args.windowsize is not None:
            if config.llmInterface in ("llamacpppython", "ollama"):
                if args.windowsize < 0:
                    print2("No change in context window size! Negative values not accepted!")
                else:
                    config.toolmate.setContextWindowSize(customContextWindowSize=args.windowsize)
                    print3(f"Context window size configured: {args.windowsize}")
            else:
                print2("No change in context window size! This option applicable to backends `llama.cpp` and `ollama` only!")
        if args.maximumoutput is not None:
            if args.maximumoutput < 0:
                print2("No change in maximum output tokens! Negative values not accepted!")
            else:
                config.toolmate.setMaxTokens(customMaxtokens=args.maximumoutput)
                print3(f"Maximum output tokens configured: {args.maximumoutput}")
        if args.temperature is not None:
            if args.temperature < 0.0 or args.temperature > 2.0:
                print2("No change in temperature! Given value is out of acceptable range 0.0-2.0!")
            else:
                config.toolmate.setTemperature(temperature=args.temperature)
                print3(f"Temperature configured: {args.temperature}")
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
