import os
thisFile = os.path.realpath(__file__)
packageFolder = os.path.dirname(thisFile)
package = os.path.basename(packageFolder)
if os.getcwd() != packageFolder:
    os.chdir(packageFolder)

from freegenius import config
config.isTermux = True if os.path.isdir("/data/data/com.termux/files/home") else False
config.freeGeniusAIFolder = packageFolder
if not hasattr(config, "freeGeniusAIName") or not config.freeGeniusAIName:
    config.freeGeniusAIName = "FreeGenius AI"
from freegenius.utils.config_tools import setConfig
config.setConfig = setConfig
## alternative to include config restoration method
#from freegenius.utils.config_tools import *
from freegenius.utils.shared_utils import SharedUtil
from freegenius.utils.tool_plugins import Plugins
config.includeIpInDeviceInfoTemp = True
config.print = config.print2 = config.print3 = print
config.addFunctionCall = Plugins.addFunctionCall
config.divider = "--------------------"
SharedUtil.setOsOpenCmd()

import sys
from freegenius.gui.chatgui import ChatGui
from PySide6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    ChatGui(standalone=True).show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()