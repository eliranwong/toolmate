from toolmate import config, print2

import os, shutil, argparse, pyperclip, subprocess
from pathlib import Path

from toolmate import updateApp, configFile, getOllamaServerClient, exportOllamaModels
from toolmate.utils.assistant import ToolMate
from prompt_toolkit.shortcuts import set_title, clear_title


def main():
    print(f"Setting up {config.toolMateAIName} ...")

    # Create the parser
    parser = argparse.ArgumentParser(description="ToolMate AI setup options")
    # Add arguments
    parser.add_argument('-b', '--backend', action='store_true', dest='backend', help="configure AI backend and models")
    parser.add_argument('-cs', '--chatsystem', action='store_true', dest='chatsystem', help="configure chat system message")
    parser.add_argument('-d', '--developer', action='store', dest='developer', help="configure developer mode; true / false")
    parser.add_argument('-ed', '--editor', action='store_true', dest='editor', help="configure custom editor")
    parser.add_argument('-ec', '--editconfigs', action='store_true', dest='editconfigs', help="configure config.py")
    parser.add_argument('-em', '--exportmodels', action='store', dest='exportmodels', help="""export models, downloaded with ollama, to ~/toolmate/LLMs/gguf/; pass a list of models for the export, e.g. "['llama3.2:1b','llama3.2:3b']"; pass an empty list "[]" to export all downloaded models""")
    parser.add_argument('-k', '--apikeys', action='store_true', dest='apikeys', help="configure API keys")
    parser.add_argument('-mo', '--maximumoutput', action='store_true', dest='maximumoutput', help="configure maximum output tokens")
    parser.add_argument('-p', '--plugins', action='store_true', dest='plugins', help="configure plugins")
    parser.add_argument('-rt', '--riskthreshold', action='store_true', dest='riskthreshold', help="configure the risk threshold for user confirmation before code execution")
    parser.add_argument('-sg', '--speechgeneration', action='store_true', dest='speechgeneration', help="configure speech generation")
    parser.add_argument('-sr', '--speechrecognition', action='store_true', dest='speechrecognition', help="configure speech recognition")
    parser.add_argument('-t', '--temperature', action='store_true', dest='temperature', help="configure inference temperature")
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

    config.toolmate = ToolMate(plugins=False)

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

    if args.backend:
        config.toolmate.setLlmModel()
    if args.chatsystem:
        config.toolmate.setCustomSystemMessage()
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
        config.toolmate.editConfigs()
    if args.apikeys:
        config.toolmate.changeAPIkeys()
    if args.maximumoutput:
        config.toolmate.setMaxTokens()
    if args.plugins:
        config.toolmate.selectPlugins()
    if args.speechgeneration:
        config.toolmate.setTextToSpeechConfig()
    if args.speechrecognition:
        config.toolmate.setSpeechToTextConfig()
    if args.temperature:
        config.toolmate.setTemperature()
    if args.toolagent:
        config.toolmate.setToolSelectionConfigs()
    if args.riskthreshold:
        config.toolmate.manageCodeExecutionRisk()
    if args.windowsize:
        config.toolmate.setContextWindowSize()
    if args.wordwrap:
        if args.wordwrap.lower() == "true":
            config.wrapWords = True
            print2("Word wrap enabled!")
        elif args.wordwrap.lower() == "false":
            config.wrapWords = False
            print2("Word wrap disabled!")
        else:
            print2("Word wrap unchanged! Accept 'True' or 'False' only!")
    if args.editor:
        config.toolmate.setCustomTextEditor()

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
    if os.path.isdir(config.localStorage):
        shutil.copy(configFile, os.path.join(config.localStorage, "config_lite_backup.py" if config.isLite else "config_backup.py"))

    # clear title
    clear_title()

if __name__ == "__main__":
    main()
