from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from toolmate import config, configFile, isServerAlive, print2, print3
from toolmate.utils.assistant import ToolMate
from toolmate.utils.tool_plugins import Plugins
from pydantic import BaseModel
import requests, argparse, json, uvicorn, re, os, signal, shutil


# Create the parser
parser = argparse.ArgumentParser(description="ToolMate AI API server cli options")
# Add arguments
parser.add_argument('-b', '--backend', action='store', dest='backend', help="AI backend")
parser.add_argument('-k', '--key', action='store', dest='key', help="specify the API key for authenticating client access")
parser.add_argument('-mo', '--maximumoutput', action='store', dest='maximumoutput', help="override default maximum output tokens; accepts non-negative integers")
parser.add_argument('-p', '--port', action='store', dest='port', help="server port")
parser.add_argument('-s', '--server', action='store', dest='server', help="server address; '0.0.0.0' by default")
parser.add_argument('-t', '--temperature', action='store', dest='temperature', help="override default inference temperature; accepted range: 0.0-2.0")
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
    instruction: str | None = "."
    chat: bool | None = False
    chatfile: str | None = None
    chatsystem: str | None = None
    maximumoutput: str | None = None
    temperature: str | None = None
    defaulttool: str | None = None
    toolagent: bool | None = None
    backupchat: bool | None = None
    backupsettings: bool | None = None
    powerdown: bool | None = None

@app.post("/api/toolmate")
async def process_instruction(request: Request, api_key: str = Depends(get_api_key) if config.toolmate_api_server_key else ""):
    wd = request.wd
    instruction = request.instruction
    chat = request.chat
    chatfile = request.chatfile
    chatsystem = request.chatsystem
    if chatsystem is not None:
        check = re.sub("^`([^`]+?)`$", r"\1", chatsystem)
        if check in config.predefinedChatSystemMessages:
            chatsystem = config.predefinedChatSystemMessages.get(check)
    maximumoutput = request.maximumoutput
    temperature = request.temperature
    defaulttool = request.defaulttool
    if defaulttool is not None:
        defaulttool = re.sub("^@", "", defaulttool)
    toolagent = request.toolagent
    backupchat = request.backupchat
    backupsettings = request.backupsettings
    powerdown = request.powerdown

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
        if maximumoutput:
            config.toolmate.setMaxTokens(customMaxtokens=current_maximumoutput)
            print3(f"Maximum output tokens restored: {current_maximumoutput}")
        if temperature:
            config.toolmate.setTemperature(temperature=current_temperature)
            print3(f"Temperature changed restored: {current_temperature}")

    if powerdown:
        os.kill(config.api_server_id, signal.SIGINT)

    return json.dumps(response)

@app.post("/api/tools")
async def process_tools(query: str, api_key: str = Depends(get_api_key) if config.toolmate_api_server_key else ""):
    if query := query.strip():
        searchPattern = query.strip()
        availableTools = Plugins.checkAvailableTools(display=False, includeRequirements=True)
        if searchPattern == "@":
            results = availableTools
        else:
            results = {key: value for key, value in availableTools.items() if re.search(searchPattern, key, re.IGNORECASE) or re.search(searchPattern, value, re.IGNORECASE)}
        return json.dumps({"results": results})

@app.post("/api/systems")
async def process_systems(query: str, api_key: str = Depends(get_api_key) if config.toolmate_api_server_key else ""):
    if query := query.strip():
        searchPattern = query.strip()
        if searchPattern == "@":
            results = config.predefinedChatSystemMessages
        else:
            results = {key: value for key, value in config.predefinedChatSystemMessages.items() if re.search(searchPattern, key, re.IGNORECASE) or re.search(searchPattern, value, re.IGNORECASE)}
        return json.dumps({"results": results})

@app.post("/api/contexts")
async def process_contexts(query: str, api_key: str = Depends(get_api_key) if config.toolmate_api_server_key else ""):
    if query := query.strip():
        searchPattern = query.strip()
        if searchPattern == "@":
            results = config.predefinedContexts
        else:
            results = {key: value for key, value in config.predefinedContexts.items() if re.search(searchPattern, key, re.IGNORECASE) or re.search(searchPattern, value, re.IGNORECASE)}
        return json.dumps({"results": results})

def main():
    host = args.server if args.server else config.toolmate_api_server_host
    port = args.port if args.port else config.toolmate_api_server_port
    if not isServerAlive(host, port):
        # configurations in API server
        config.initialCompletionCheck = False
        config.auto_tool_selection = True
        config.confirmExecution = 'none'
        config.ttsInput = False
        config.ttsOutput = False
        # backend
        backends = ("llamacpp", "llamacppserver", "ollama", "groq", "googleai", "vertexai", "chatgpt", "letmedoit")
        if args.backend and args.backend.lower() in backends:
            config.llmInterface = args.backend.lower()
        # initiate assistant
        config.toolmate = ToolMate()
        # backend-dependent configurations
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
