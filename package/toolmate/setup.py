from toolmate import config, print2
from toolmate.api_client import getToolmate
from toolmate import getOllamaServerClient, exportOllamaModels, isServerAlive
from toolmate.utils.assistant import ToolMate
from prompt_toolkit.shortcuts import set_title, clear_title
from pathlib import Path
import os, shutil, argparse, re

def main():
    print(f"Setting up {config.toolMateAIName} ...")

    # Create the parser
    parser = argparse.ArgumentParser(description="ToolMate AI setup options")
    # Add arguments
    parser.add_argument('-ag', '--autogen', action='store_true', dest='autogen', help="configure AutoGen integration; applicable to AutoGen integrated tools")
    parser.add_argument('-b', '--backend', action='store_true', dest='backend', help="configure AI backend and models")
    parser.add_argument('-cs', '--chatsystem', action='store_true', dest='chatsystem', help="configure chat system message")
    parser.add_argument('-d', '--developer', action='store', dest='developer', help="configure developer mode; true / false")
    parser.add_argument('-ed', '--editor', action='store_true', dest='editor', help="configure custom editor")
    parser.add_argument('-ec', '--editconfigs', action='store_true', dest='editconfigs', help="configure config.py")
    parser.add_argument('-em', '--exportmodels', action='store', dest='exportmodels', help="""export models, downloaded with ollama, to ~/toolmate/LLMs/gguf/; pass a list of models for the export, e.g. "['llama3.2:1b','llama3.2:3b']"; pass an empty list "[]" to export all downloaded models""")
    parser.add_argument('-fb', '--fabric', action='store_true', dest='fabric', help="configure Fabric integration; applicable to Fabric integrated tools")
    parser.add_argument('-k', '--apikeys', action='store_true', dest='apikeys', help="configure API keys")
    parser.add_argument('-m', '--menu', action='store_true', dest='menu', help="setup menu")
    parser.add_argument('-mo', '--maximumoutput', action='store_true', dest='maximumoutput', help="configure maximum output tokens")
    parser.add_argument('-p', '--plugins', action='store_true', dest='plugins', help="configure plugins")
    parser.add_argument('-rt', '--riskthreshold', action='store_true', dest='riskthreshold', help="configure the risk threshold for user confirmation before code execution")
    parser.add_argument('-sg', '--speechgeneration', action='store_true', dest='speechgeneration', help="configure speech generation")
    parser.add_argument('-so', '--searchoptions', action='store_true', dest='searchoptions', help="configure search options")
    parser.add_argument('-sr', '--speechrecognition', action='store_true', dest='speechrecognition', help="configure speech recognition")
    parser.add_argument('-t', '--temperature', action='store_true', dest='temperature', help="configure inference temperature")
    parser.add_argument('-tms', '--tmsystems', action='store_true', dest='tmsystems', help="configure chat system messages for running with commands `tms1`, `tms2`, `tms3`, ... `tms20`")
    parser.add_argument('-tmt', '--tmtools', action='store_true', dest='tmtools', help="configure tools for running with commands `tmt1`, `tmt2`, `tmt3`, ... `tmt20`")
    parser.add_argument('-ta', '--toolagent', action='store_true', dest='toolagent', help="configure tool selection agent")
    parser.add_argument('-ws', '--windowsize', action='store_true', dest='windowsize', help="configure context window size")
    parser.add_argument('-ww', '--wordwrap', action='store', dest='wordwrap', help="configure word wrap; true / false")
    # Parse arguments
    args = parser.parse_args()
    # Check what kind of arguments were provided and perform actions accordingly

    # update to the latest version
    config.tempInterface = ""
    config.custom_config = ""
    config.initialCompletionCheck = False
    config.includeIpInDeviceInfoTemp = False
    config.defaultEntry = ""
    config.accept_default = False

    # set window title
    set_title(config.toolMateAIName)

    toolmate = ToolMate(plugins=True if args.tmsystems or args.tmtools or args.menu else False)

    if args.exportmodels:
        exportmodels = eval(args.exportmodels)
        if isinstance(exportmodels, list):
            exportOllamaModels(exportmodels)
        elif isinstance(exportmodels, str):
            exportOllamaModels(exportmodels.split())
        else:
            print2("""To export models, downloaded with ollama, either:
* pass a list of models for the export, e.g. "['llama3.2:1b','llama3.2:3b']"
* pass an empty list "[]" to export all downloaded models""")

    if args.menu:
        toolmate.runActions("...", setupOnly=True)
    if args.backend:
        toolmate.setLlmModel()
    if args.chatsystem:
        toolmate.setCustomSystemMessage()
    if args.developer:
        if args.developer.lower() == "true":
            config.developer = True
            print2("Developer mode enabled!")
        elif args.developer.lower() == "false":
            config.developer = False
            print2("Developer mode disabled!")
        else:
            print2("Developer mode unchanged! Accept 'True' or 'False' only!")
    if args.editconfigs:
        toolmate.editConfigs()
    if args.apikeys:
        toolmate.changeAPIkeys()
    if args.maximumoutput:
        toolmate.setMaxTokens()
    if args.plugins:
        toolmate.selectPlugins()
    if args.tmsystems:
        toolmate.setTmsMessages()
    if args.tmtools:
        toolmate.setTmtTools()
    if args.speechgeneration:
        toolmate.setTextToSpeechConfig()
    if args.speechrecognition:
        toolmate.setSpeechToTextConfig()
    if args.temperature:
        toolmate.setTemperature()
    if args.toolagent:
        toolmate.setToolSelectionConfigs()
    if args.riskthreshold:
        toolmate.manageCodeExecutionRisk()
    if args.windowsize:
        toolmate.setContextWindowSize()
    if args.wordwrap:
        if args.wordwrap.lower() == "true":
            config.wrapWords = True
            print2("Word wrap enabled!")
        elif args.wordwrap.lower() == "false":
            config.wrapWords = False
            print2("Word wrap disabled!")
        else:
            print2("Word wrap unchanged! Accept 'True' or 'False' only!")
    if args.searchoptions:
        toolmate.changeSearchSettings()
    if args.editor:
        toolmate.setCustomTextEditor()
    if args.autogen:
        toolmate.setAutoGenConfig()
    if args.fabric:
        toolmate.setFabricPatternsDirectory()

    # unload llama.cpp model to free VRAM
    try:
        config.llamacppToolModel.close()
        print("Llama.cpp model unloaded!")
    except:
        pass
    if config.llmInterface == "ollama":
        getOllamaServerClient().generate(model=config.ollamaToolModel, keep_alive=0, stream=False,)
        print(f"Ollama model '{config.ollamaToolModel}' unloaded!")
    if hasattr(config, "llamacppToolModel"):
        del config.llamacppToolModel

    # delete temporary content
    try:
        tempFolder = os.path.join(config.toolMateAIFolder, "temp")
        shutil.rmtree(tempFolder, ignore_errors=True)
        Path(tempFolder).mkdir(parents=True, exist_ok=True)
    except:
        pass

    # backup configurations
    config.saveConfig()

    host = config.toolmate_api_client_host
    port = config.toolmate_api_client_port
    if isServerAlive(re.sub("^(http://|https://)", "", host, re.IGNORECASE), port):
        print("Reloading configurations ...")
        getToolmate({"reloadsettings": True})
        print("Reloaded!")

    # clear title
    clear_title()

if __name__ == "__main__":
    main()
