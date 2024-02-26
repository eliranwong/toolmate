import os, sys, platform, shutil, argparse

# requires python 3.8+; required by package 'tiktoken'
pythonVersion = sys.version_info
if pythonVersion < (3, 8):
    print("Python version higher than 3.8 is required!")
    print("Closing ...")
    exit(1)
elif pythonVersion >= (3, 12):
    print("Some features may not work with python version newer than 3.11!")

# navigate to project directory
letMeDoItFile = os.path.realpath(__file__)
letMeDoItAIFolder = os.path.dirname(letMeDoItFile)
if os.getcwd() != letMeDoItAIFolder:
    os.chdir(letMeDoItAIFolder)

# check current platform
thisPlatform = platform.system()

# set up config
# create config.py if it does not exist
configFile = os.path.join(letMeDoItAIFolder, "config.py")
if not os.path.isfile(configFile):
    open(configFile, "a", encoding="utf-8").close()

# import config and setup default
#import traceback
try:
    from freegenius import config
except:
    # write off problematic configFile
    open(configFile, "w", encoding="utf-8").close()
    from freegenius import config
import letmedoit.config
from pathlib import Path

config.letMeDoItName = "FreeGenius AI"
letmedoit.config.letMeDoItFile = config.letMeDoItFile = letMeDoItFile
letmedoit.config.letMeDoItAIFolder = config.letMeDoItAIFolder = letMeDoItAIFolder
letmedoit.config.isTermux = config.isTermux = True if os.path.isdir("/data/data/com.termux/files/home") else False

letmedoit.config.terminalColors = config.terminalColors = {
    "ansidefault": "ansidefault",
    "ansiblack": "ansiwhite",
    "ansired": "ansibrightred",
    "ansigreen": "ansibrightgreen",
    "ansiyellow": "ansibrightyellow",
    "ansiblue": "ansibrightblue",
    "ansimagenta": "ansibrightmagenta",
    "ansicyan": "ansibrightcyan",
    "ansigray": "ansibrightblack",
    "ansiwhite": "ansiblack",
    "ansibrightred": "ansired",
    "ansibrightgreen": "ansigreen",
    "ansibrightyellow": "ansiyellow",
    "ansibrightblue": "ansiblue",
    "ansibrightmagenta": "ansimagenta",
    "ansibrightcyan": "ansicyan",
    "ansibrightblack": "ansigray",
}

# package name
package = "freegenius"

def getStorageDir():
    storageDir = os.path.join(os.path.expanduser('~'), package)
    try:
        Path(storageDir).mkdir(parents=True, exist_ok=True)
    except:
        pass
    return storageDir if os.path.isdir(storageDir) else ""
letmedoit.config.getStorageDir = config.getStorageDir = getStorageDir

def restartApp():
    print(f"Restarting {config.letMeDoItName} ...")
    os.system(f"{sys.executable} {config.letMeDoItFile}")
    exit(0)
config.restartApp = restartApp

from freegenius.configs.config_tools import *
from freegenius.configs.config_essential import temporaryConfigs
from letmedoit.utils.install import installmodule
from letmedoit.utils.shared_utils import SharedUtil

# automatic update
config.pipIsUpdated = False
def updateApp(thisPackage):
    print(f"Checking '{thisPackage}' version ...")
    installed_version = SharedUtil.getPackageInstalledVersion(thisPackage)
    if installed_version is None:
        print("Installed version information is not accessible!")
    else:
        print(f"Installed version: {installed_version}")
    latest_version = SharedUtil.getPackageLatestVersion(thisPackage)
    if latest_version is None:
        print("Latest version information is not accessible at the moment!")
    elif installed_version is not None:
        print(f"Latest version: {latest_version}")
        if latest_version > installed_version:
            if thisPlatform == "Windows":
                print("Automatic upgrade feature is yet to be supported on Windows!")
                print(f"Run 'pip install --upgrade {thisPackage}' to manually upgrade this app!")
            else:
                try:
                    # upgrade package
                    installmodule(f"--upgrade {thisPackage}")
                    restartApp()
                except:
                    print(f"Failed to upgrade '{thisPackage}'!")

# import other libraries
import pprint
from letmedoit.utils.shortcuts import createShortcuts
from freegenius.core.assistant import FreeGenius
from letmedoit.utils.vlc_utils import VlcUtil
from prompt_toolkit.shortcuts import set_title, clear_title
try:
    # hide pygame welcome message
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    import pygame
    pygame.mixer.init()
    config.isPygameInstalled = True
except:
    config.isPygameInstalled = False

def setOsOpenCmd():
    config.thisPlatform = thisPlatform
    if config.terminalEnableTermuxAPI:
        config.open = "termux-share"
    elif thisPlatform == "Linux":
        config.open = "xdg-open"
    elif thisPlatform == "Darwin":
        config.open = "open"
    elif thisPlatform == "Windows":
        config.open = "start"
    # name macOS
    if config.thisPlatform == "Darwin":
        config.thisPlatform = "macOS"

def saveConfig():
    with open(configFile, "w", encoding="utf-8") as fileObj:
        for name in dir(config):
            excludeConfigList = temporaryConfigs + config.excludeConfigList
            if not name.startswith("__") and not name in excludeConfigList:
                try:
                    value = eval(f"config.{name}")
                    if not callable(value) and not str(value).startswith("<"):
                        fileObj.write("{0} = {1}\n".format(name, pprint.pformat(value)))
                except:
                    pass
config.saveConfig = saveConfig

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

def main():
    print(f"launching {config.letMeDoItName} ...")

    # Create the parser
    parser = argparse.ArgumentParser(description="FreeGenius AI cli options")
    # Add arguments
    parser.add_argument("default", nargs="?", default=None, help="default entry; accepts a string; ignored when -l/rf/f/r flag is used")
    parser.add_argument('-c', '--context', action='store', dest='context', help="specify pre-defined context with -r flag; accepts a string")
    parser.add_argument('-f', '--file', action='store', dest='file', help="read file text as default entry with -f flag; accepts a file path; ignored when -l/rf flag is used")
    parser.add_argument('-i', '--ip', action='store', dest='ip', help="set 'true' to include or 'false' to exclude ip information in system message with -i flag")
    parser.add_argument('-l', '--load', action='store', dest='load', help="load file that contains saved chat records with -l flag; accepts either a chat ID or a file path; required plugin 'search chat records'")
    parser.add_argument('-n', '--nocheck', action='store', dest='nocheck', help="set 'true' to bypass completion check at startup with -n flag")
    parser.add_argument('-r', '--run', action='store', dest='run', help="run default entry with -r flag; accepts a string; ignored when -l/rf/f flag is used")
    parser.add_argument('-rf', '--runfile', action='store', dest='runfile', help="read file text as default entry and run with -rf flag; accepts a file path; ignored when -l flag is used")
    parser.add_argument('-u', '--update', action='store', dest='update', help="set 'true' to force or 'false' to bypass automatic update with -u flag")
    # Parse arguments
    args = parser.parse_args()
    # Check what kind of arguments were provided and perform actions accordingly

    # update to the latest version
    if args.update:
        if args.update.lower() == "true":
            updateApp(package)
    # determined by config.autoUpgrade if -u flag is not used
    elif config.autoUpgrade:
        updateApp(package)

    # initial completion check at startup
    config.initialCompletionCheck = False if args.nocheck and args.nocheck.lower() == "true" else True

    # include ip in system message
    letmedoit.config.includeIpInSystemMessageTemp = config.includeIpInSystemMessageTemp = True if args.ip and args.ip.lower() == "true" else False

    # specify pre-defined context
    if args.context:
        config.predefinedContextTemp = config.predefinedContext
        config.predefinedContext = args.context

    # priority: load > runfile > file > run > default
    if args.load:
        load = args.load.strip()
        config.defaultEntry = f"Load chat records with this ID: {load}"
        config.accept_default = True
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
            shutil.rmtree(os.path.join(os.path.expanduser('~'), config.letMeDoItName.split()[0].lower(), f"{i}.txt"), ignore_errors=True)
    elif args.run:
        config.defaultEntry = args.run.strip()
        config.accept_default = True
    elif args.default:
        config.defaultEntry = args.default.strip()
        config.accept_default = False
    else:
        config.defaultEntry = ""
        config.accept_default = False

    set_title(config.letMeDoItName)
    setOsOpenCmd()
    createShortcuts()
    config.excludeConfigList = []
    config.isVlcPlayerInstalled = VlcUtil.isVlcPlayerInstalled()
    # save loaded configs
    saveConfig()
    # check log files; remove old lines if more than 3000 lines is found in a log file
    for i in ("chats", "paths", "commands"):
        filepath = os.path.join(config.historyParentFolder if config.historyParentFolder else config.letMeDoItAIFolder, "history", i)
        set_log_file_max_lines(filepath, 3000)
    FreeGenius().startChats()
    # Do the following tasks before exit
    # backup configurations
    saveConfig()
    storageDir = getStorageDir()
    if os.path.isdir(storageDir):
        shutil.copy(configFile, os.path.join(storageDir, "config_backup.py"))
    # delete temporary content
    try:
        tempFolder = os.path.join(config.letMeDoItAIFolder, "temp")
        shutil.rmtree(tempFolder, ignore_errors=True)
        Path(tempFolder).mkdir(parents=True, exist_ok=True)
    except:
        pass
    # clear title
    clear_title()

if __name__ == "__main__":
    main()
