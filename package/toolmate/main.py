from toolmate import config

import os, shutil, argparse, pyperclip
from pathlib import Path

from toolmate import updateApp, configFile, getOllamaServerClient
from toolmate.utils.assistant import ToolMate
from prompt_toolkit.shortcuts import set_title, clear_title

def set_log_file_max_lines(log_file, max_lines):
    if os.path.isfile(log_file):
        # Read the contents of the log file
        with open(log_file, "r", encoding="utf-8") as fileObj:
            lines = fileObj.readlines()
        # Count the number of lines in the file
        num_lines = len(lines)
        if num_lines > max_lines:
            # Calculate the number of lines to be deleted
            num_lines_to_delete = num_lines - max_lines
            if num_lines_to_delete > 0:
                # Open the log file in write mode and truncate it
                with open(log_file, "w", encoding="utf-8") as fileObj:
                    # Write the remaining lines back to the log file
                    fileObj.writelines(lines[num_lines_to_delete:])
            filename = os.path.basename(log_file)
            print(f"{num_lines_to_delete} old lines deleted from log file '{filename}'.")

def letmedoit():
    main("letmedoit")

def main(tempInterface=""):
    print(f"launching {config.toolMateAIName} ...")

    # Create the parser
    parser = argparse.ArgumentParser(description="ToolMate AI cli options")
    # Add arguments
    parser.add_argument("default", nargs="?", default=None, help="default entry; accepts a string; ignored when -l/rp/p/rf/f/r flag is used")
    parser.add_argument('-b', '--backend', action='store', dest='backend', help="set llm interface with -b flag; options: llamacpp/llamacppserver/ollama/groq/gemini/chatgpt/letmedoit")
    parser.add_argument('-c', '--context', action='store', dest='context', help="specify pre-defined context with -r flag; accepts a string")
    parser.add_argument('-f', '--file', action='store', dest='file', help="read file text as default entry with -f flag; accepts a file path; ignored when -l/rf flag is used")
    parser.add_argument('-i', '--ip', action='store', dest='ip', help="set 'true' to include or 'false' to exclude ip information in system message with -i flag")
    parser.add_argument('-l', '--load', action='store', dest='load', help="load file that contains saved chat records with -l flag; accepts either a chat ID or a file path; required plugin 'search chat records'")
    parser.add_argument('-n', '--nocheck', action='store', dest='nocheck', help="set 'true' to bypass completion check at startup with -n flag")
    parser.add_argument('-p', '--paste', action='store', dest='paste', help="set 'true' to paste clipboard text as default entry with -p flag")
    parser.add_argument('-r', '--run', action='store', dest='run', help="run default entry with -r flag; accepts a string; ignored when -l/rf/f flag is used")
    parser.add_argument('-rp', '--runpaste', action='store', dest='runpaste', help="set 'true' to paste and run clipboard text as default entry with -rp flag")
    parser.add_argument('-rf', '--runfile', action='store', dest='runfile', help="read file text as default entry and run with -rf flag; accepts a file path; ignored when -l flag is used")
    parser.add_argument('-u', '--update', action='store', dest='update', help="set 'true' to force or 'false' to interfacebypass automatic update with -u flag")
    parser.add_argument('-t', '--temp', action='store', dest='temp', help="set temporary llm interface with -t flag; options: llamacpp/llamacppserver/ollama/groq/gemini/chatgpt/letmedoit; all changes in configs are temporary")
    # Parse arguments
    args = parser.parse_args()
    # Check what kind of arguments were provided and perform actions accordingly

    # update to the latest version
    config.tempInterface = tempInterface
    backends = ("llamacpp", "llamacppserver", "ollama", "groq", "gemini", "chatgpt", "letmedoit")
    if args.backend:
        config.llmInterface = args.backend.lower()
    elif args.temp and args.temp.lower() in backends:
        config.tempInterface = args.temp.lower()
    if config.tempInterface:
        config.llmInterface = config.tempInterface

    # update to the latest version
    if args.update:
        if args.update.lower() == "true":
            updateApp()
    # determined by config.autoUpgrade if -u flag is not used
    elif config.autoUpgrade:
        updateApp()

    # initial completion check at startup
    config.initialCompletionCheck = False if args.nocheck and args.nocheck.lower() == "true" else True

    # include ip in system message
    config.includeIpInDeviceInfoTemp = True if args.ip and args.ip.lower() == "true" else False

    # specify pre-defined context
    if args.context:
        config.predefinedContextTemp = config.predefinedContext
        config.predefinedContext = args.context

    # priority: load > runpaste > paste > runfile > file > run > default
    if args.load:
        load = args.load.strip()
        config.defaultEntry = f"Load chat records with this ID: {load}"
        config.accept_default = True
    elif args.runpaste and args.runpaste.lower() == "true":
        config.defaultEntry = pyperclip.paste()
        config.accept_default = True
    elif args.paste and args.paste.lower() == "true":
        config.defaultEntry = pyperclip.paste()
    elif args.runfile or args.file:
        try:
            filename = args.runfile if args.runfile else args.file
            filename = os.path.expanduser(filename)
            config.defaultEntry = ""
            if os.path.isfile(filename):
                if os.path.basename(filename) == "selected_files.txt":
                    dirNo = 1
                    fileNo = 1
                    with open(filename, "r", encoding="utf-8") as fileObj:
                        for line in fileObj.readlines():
                            strippedLine = line.strip()
                            if os.path.isdir(strippedLine):
                                config.defaultEntry += f'''Folder {dirNo}: "{strippedLine}"\n'''
                                dirNo += 1
                            elif os.path.isfile(strippedLine):
                                config.defaultEntry += f'''File {fileNo}: "{strippedLine}"\n'''
                                fileNo += 1
                            elif strippedLine:
                                config.defaultEntry += line
                else:
                    with open(filename, "r", encoding="utf-8") as fileObj:
                        config.defaultEntry = fileObj.read()
            else:
                print(f"'{filename}' does not exist!")
        except:
            config.defaultEntry = ""
        config.accept_default = True if args.runfile else False
        for i in ("selected_files", "selected_text"):
            shutil.rmtree(os.path.join(os.path.expanduser('~'), config.toolMateAIName.split()[0].lower(), f"{i}.txt"), ignore_errors=True)
    elif args.run:
        config.defaultEntry = args.run.strip()
        config.accept_default = True
    elif args.default:
        config.defaultEntry = args.default.strip()
        config.accept_default = False
    else:
        config.defaultEntry = ""
        config.accept_default = False

    # set window title
    set_title(config.toolMateAIName)

    # local storage
    # check log files; remove old lines if more than 3000 lines is found in a log file
    for i in ("chats", "paths", "commands"):
        filepath = os.path.join(config.localStorage, "history", i)
        set_log_file_max_lines(filepath, 3000)
    config.toolmate = ToolMate()
    config.toolmate.startChats()
    # Do the following tasks before exit
    # backup configurations
    config.saveConfig()
    if os.path.isdir(config.localStorage):
        shutil.copy(configFile, os.path.join(config.localStorage, "config_backup.py"))
    # unload llama.cpp model to free VRAM
    try:
        config.llamacppToolModel.close()
        print("Llama.cpp model unloaded!")
    except:
        pass
    # delete temporary content
    try:
        tempFolder = os.path.join(config.toolMateAIFolder, "temp")
        shutil.rmtree(tempFolder, ignore_errors=True)
        Path(tempFolder).mkdir(parents=True, exist_ok=True)
    except:
        pass
    # clear title
    clear_title()

    if config.llmInterface == "ollama":
        getOllamaServerClient().generate(model=config.ollamaToolModel, keep_alive=0, stream=False,)
        print(f"Ollama model '{config.ollamaToolModel}' unloaded!")
    if hasattr(config, "llamacppToolModel"):
        del config.llamacppToolModel

if __name__ == "__main__":
    main()
