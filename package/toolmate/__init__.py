import os, sys, platform, shutil
from importlib_metadata import version as lib_version

# check python version
# requires python 3.8+; required by package 'tiktoken'
pythonVersion = sys.version_info
if pythonVersion < (3, 8):
    print("Python version higher than 3.8 is required!")
    print("Closing ...")
    exit(1)
elif pythonVersion >= (3, 13):
    print("Some features may not work with python version newer than 3.12!")

# check package path
thisFile = os.path.realpath(__file__)
packageFolder = os.path.dirname(thisFile)
package = os.path.basename(packageFolder)

# set current directory; unnecessary; conflict with API client
#if os.getcwd() != packageFolder:
#    os.chdir(packageFolder)

# create conifg.py in case it is deleted due to errors
configFile = os.path.join(packageFolder, "config.py")
if not os.path.isfile(configFile):
    open(configFile, "a", encoding="utf-8").close()

# import config module
from toolmate import config
if not hasattr(config, "isLite"):
    try:
        lib_version("toolmate")
        config.isLite = False
    except:
        config.isLite = True
config.isTermux = True if os.path.isdir("/data/data/com.termux/files/home") and not os.getcwd().startswith("/root") else False
config.terminalEnableTermuxAPI = True if config.isTermux and shutil.which("termux-share") else False

# set up shared configs

config.toolMateAIFolder = packageFolder
config.toolMateAIFile = os.path.join(config.toolMateAIFolder, "main.py")
if not hasattr(config, "toolMateAIName") or not config.toolMateAIName:
    config.toolMateAIName = "ToolMate AI"

if not hasattr(config, "isPipUpdated"):
    config.isPipUpdated = False

# import shared utilities
from toolmate.utils.shared_utils import *

# other initiations

config.stopSpinning = stopSpinning
config.localStorage = getLocalStorage()

from toolmate.utils.config_tools import *
config.loadConfig = loadConfig
config.setConfig = setConfig
# old configs
if config.llmInterface == "chatgpt":
    config.llmInterface = "openai"

from toolmate.utils.tool_plugins import Plugins
config.addToolCall = config.addFunctionCall = Plugins.addToolCall

from toolmate.utils.vlc_utils import VlcUtil
config.isVlcPlayerInstalled = VlcUtil.isVlcPlayerInstalled()

if not hasattr(config, "isPygameInstalled"):
    try:
        # hide pygame welcome message
        os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
        import pygame
        pygame.mixer.init()
        config.isPygameInstalled = True
    except:
        config.isPygameInstalled = False
elif not config.isPygameInstalled:
    config.usePygame = False
thisPlatform = platform.system()
config.thisPlatform = "macOS" if thisPlatform == "Darwin" else thisPlatform
if config.terminalEnableTermuxAPI:
    checkPath()
    config.open = "termux-share"
    config.thisDistro = "Android Termux"
elif thisPlatform == "Linux":
    checkPath()
    config.open = "xdg-open"
    try:
        #config.thisDistro = subprocess.check_output('lsb_release -i -s', shell=True).decode('utf-8')
        config.thisDistro = get_linux_distro().get("name", "")
    except:
        config.thisDistro = ""
elif thisPlatform == "Darwin":
    checkPath()
    config.open = "open"
    config.thisDistro = ""
elif thisPlatform == "Windows":
    config.open = "start"
    config.thisDistro = ""

config.excludeConfigList = []
config.includeIpInDeviceInfoTemp = config.includeIpInDeviceInfo
config.divider = "--------------------"
config.tts = False if not config.isVlcPlayerInstalled and not config.isPygameInstalled and not config.ttsCommand and not config.elevenlabsApi else True
config.outputTextConverters = []

# save loaded configs
config.tempInterface = ""
config.saveConfig()

# environment variables
os.environ["TOKENIZERS_PARALLELISM"] = config.tokenizers_parallelism

# create shortcuts
from toolmate.utils.shortcuts import createShortcuts
createShortcuts()

# setup optional credentials
setChatGPTAPIkey()
if config.anthropicApi_key and not config.anthropicApi_key == "toolmate":
    os.environ["ANTHROPIC_API_KEY"] = config.anthropicApi_key
if not config.isLite:
    setGoogleCredentials()
    downloadNltkPackages()

# context
if isServerAlive("8.8.8.8", 53): # check internet connection
    g = geocoder.ip('me')
    config.country = g.country
    config.state = g.state
    config.dayOfWeek = getDayOfWeek()
else:
    config.country = config.state = config.dayOfWeek = "n/a"