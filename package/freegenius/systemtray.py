import os
thisFile = os.path.realpath(__file__)
packageFolder = os.path.dirname(thisFile)
#package = os.path.basename(packageFolder)
if os.getcwd() != packageFolder:
    os.chdir(packageFolder)

from freegenius import config
config.isTermux = True if os.path.isdir("/data/data/com.termux/files/home") else False
config.freeGeniusAIFolder = packageFolder
if not hasattr(config, "freeGeniusAIName") or not config.freeGeniusAIName:
    config.freeGeniusAIName = "FreeGenius AI"
from freegenius.utils.tool_plugins import ToolStore
config.divider = "--------------------"
ToolStore.setupToolStoreClient()
os.environ["TOKENIZERS_PARALLELISM"] = config.tokenizers_parallelism

import sys, platform, shutil, webbrowser
from freegenius import startAutogenstudioServer, runFreeGeniusCommand
#from freegenius.gui.chatgui import ChatGui
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction, QGuiApplication
from pathlib import Path
from functools import partial


freeGeniusAIFile = os.path.realpath(__file__)
freeGeniusAIFolder = os.path.dirname(freeGeniusAIFile)
#with open(os.path.join(freeGeniusAIFolder, "package_name.txt"), "r", encoding="utf-8") as fileObj:
#    package = fileObj.read()
iconFile = os.path.join(freeGeniusAIFolder, "icons", "ai.png")
thisOS = platform.system()


class FreeGeniusHub(QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)

        # pre-load the main gui
        #self.chatGui = ChatGui()

        self.menu = QMenu(parent)

        #if config.developer:
        #    chatgui = QAction("Desktop Assistant [experimental]", self)
        #    chatgui.triggered.connect(self.showGui)
        #    self.menu.addAction(chatgui)
        #    self.menu.addSeparator()

        for i in ("freegenius", "letmedoit"):
            action = QAction(i, self)
            action.triggered.connect(partial(runFreeGeniusCommand, i))
            self.menu.addAction(action)
        self.menu.addSeparator()

        # submenu - servers
        submenu = QMenu()
        servers = [
            "toolserver",
            "chatserver",
            "visionserver",
        ]
        if config.customToolServer_command:
            servers.append("customtoolserver")
        if config.customChatServer_command:
            servers.append("customchatserver")
        if config.customVisionServer_command:
            servers.append("customvisionserver")
        for i in servers:
            action = QAction(i, self)
            action.triggered.connect(partial(runFreeGeniusCommand, i))
            submenu.addAction(action)

        menuAction = QAction("Servers", self)
        menuAction.setMenu(submenu)
        self.menu.addAction(menuAction)

        # submenu - cahtbots
        submenu = QMenu()
        for i in (
            "llamacpp",
            "llamacppserver",
            "ollamachat",
            "groqchat",
            "chatgpt",
            "geminipro",
            "geminiprovision",
            "palm2",
            "codey",
        ):
            action = QAction(i[:-4] if i.endswith("chat") else i, self)
            action.triggered.connect(partial(runFreeGeniusCommand, i))
            submenu.addAction(action)

        menuAction = QAction("Chatbots", self)
        menuAction.setMenu(submenu)
        self.menu.addAction(menuAction)

        # submenu - autogen agents
        submenu = QMenu()
        for i in ("autoassist", "autoretriever", "autobuilder"):
            action = QAction(i, self)
            action.triggered.connect(partial(runFreeGeniusCommand, i))
            submenu.addAction(action)

        # autogenstudio
        action = QAction("autogenstudio", self)
        action.triggered.connect(startAutogenstudioServer)
        submenu.addAction(action)

        menuAction = QAction("AutoGen Agents", self)
        menuAction.setMenu(submenu)
        self.menu.addAction(menuAction)

        # submenu - utilities
        submenu = QMenu()
        for i in (
            "rag",
            "etextedit",
            "commandprompt",
        ):
            action = QAction(i, self)
            action.triggered.connect(partial(runFreeGeniusCommand, i))
            submenu.addAction(action)

        menuAction = QAction("Utilities", self)
        menuAction.setMenu(submenu)
        self.menu.addAction(menuAction)

        # submenu - custom commands
        if hasattr(config, "customTrayCommands") and config.customTrayCommands:
            submenu = QMenu()
            for i in config.customTrayCommands:
                if not i:
                    self.menu.addSeparator()
                else:
                    action = QAction("ollama" if i == "ollamachat" else i, self)
                    action.triggered.connect(partial(runFreeGeniusCommand, i))
                    submenu.addAction(action)

        menuAction = QAction("Custom", self)
        menuAction.setMenu(submenu)
        self.menu.addAction(menuAction)

        self.menu.addSeparator()

        helpAction = QAction("Wiki", self)
        helpAction.triggered.connect(lambda: webbrowser.open("https://github.com/eliranwong/letmedoit/wiki"))
        self.menu.addAction(helpAction)

        self.menu.addSeparator()

        exitAction = QAction("Exit", self)
        exitAction.triggered.connect(self.exit)
        self.menu.addAction(exitAction)

        self.setContextMenu(self.menu)

    def exit(self):
        self.setVisible(False)
        QGuiApplication.instance().quit()

    def showGui(self):
        # to work with mutliple virtual desktops
        #self.chatGui.hide()
        #self.chatGui.show()
        ...

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    icon = QIcon(iconFile)
    trayIcon = FreeGeniusHub(icon)
    trayIcon.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()