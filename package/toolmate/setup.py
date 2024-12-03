from toolmate import config, print2

import os, shutil, argparse, pyperclip, subprocess
from pathlib import Path

from toolmate import updateApp, configFile, getOllamaServerClient
from toolmate.utils.assistant import ToolMate
from prompt_toolkit.shortcuts import set_title, clear_title


def main():
    print(f"Setting up {config.toolMateAIName} ...")

    # Create the parser
    parser = argparse.ArgumentParser(description="ToolMate AI cli options")
    # Add arguments
    parser.add_argument('-b', '--backend', action='store', dest='backend', help="configure AI backend and models; true / false")
    parser.add_argument('-cs', '--chatsystem', action='store', dest='chatsystem', help="configure chat system message; true / false")
    parser.add_argument('-d', '--developer', action='store', dest='developer', help="configure developer mode; true / false")
    parser.add_argument('-ec', '--editconfigs', action='store', dest='editconfigs', help="configure config.py; true / false")
    parser.add_argument('-k', '--apikeys', action='store', dest='apikeys', help="configure API keys; true / false")
    parser.add_argument('-mo', '--maximumoutput', action='store', dest='maximumoutput', help="configure maximum output tokens; true / false")
    parser.add_argument('-p', '--plugins', action='store', dest='plugins', help="configure plugins; true / false")
    parser.add_argument('-sg', '--speechgeneration', action='store', dest='speechgeneration', help="configure speech generation; true / false")
    parser.add_argument('-sr', '--speechrecognition', action='store', dest='speechrecognition', help="configure speech recognition; true / false")
    parser.add_argument('-t', '--temperature', action='store', dest='temperature', help="configure inference temperature; true / false")
    parser.add_argument('-ta', '--toolagent', action='store', dest='toolagent', help="configure tool selection agent; true / false")
    parser.add_argument('-ws', '--windowsize', action='store', dest='windowsize', help="configure context window size; true / false")
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

    if args.backend and args.backend.lower() == "true":
        config.toolmate.setLlmModel()
    if args.chatsystem and args.chatsystem.lower() == "true":
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
    if args.editconfigs and args.editconfigs.lower() == "true":
        config.toolmate.editConfigs()
    if args.apikeys and args.apikeys.lower() == "true":
        config.toolmate.changeAPIkeys()
    if args.maximumoutput and args.maximumoutput.lower() == "true":
        config.toolmate.setMaxTokens()
    if args.plugins and args.plugins.lower() == "true":
        config.toolmate.selectPlugins()
    if args.speechgeneration and args.speechgeneration.lower() == "true":
        config.toolmate.setTextToSpeechConfig()
    if args.speechrecognition and args.speechrecognition.lower() == "true":
        config.toolmate.setSpeechToTextConfig()
    if args.temperature and args.temperature.lower() == "true":
        config.toolmate.setTemperature()
    if args.toolagent and args.toolagent.lower() == "true":
        config.toolmate.setToolSelectionConfigs()
    if args.windowsize and args.windowsize.lower() == "true":
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
