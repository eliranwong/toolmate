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
from freegenius.utils.tool_plugins import ToolStore
config.divider = "--------------------"
ToolStore.setupToolStoreClient()
os.environ["TOKENIZERS_PARALLELISM"] = config.tokenizers_parallelism

import sys, platform, shutil, webbrowser
from freegenius import startAutogenstudioServer
from freegenius.gui.chatgui import ChatGui
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction, QGuiApplication
from pathlib import Path
from functools import partial


freeGeniusAIFile = os.path.realpath(__file__)
freeGeniusAIFolder = os.path.dirname(freeGeniusAIFile)
with open(os.path.join(freeGeniusAIFolder, "package_name.txt"), "r", encoding="utf-8") as fileObj:
    package = fileObj.read()
iconFile = os.path.join(freeGeniusAIFolder, "icons", "ai.png")
thisOS = platform.system()


class SystemTrayIcon(QSystemTrayIcon):

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

        for i in (package, "letmedoit"):
            action = QAction(i, self)
            action.triggered.connect(partial(self.runFreeGeniusCommand, i))
            self.menu.addAction(action)
        self.menu.addSeparator()

        # submenu - servers
        submenu = QMenu()
        for i in (
            "chatserver",
            "visionserver",
        ):
            action = QAction(i, self)
            action.triggered.connect(partial(self.runFreeGeniusCommand, i))
            submenu.addAction(action)

        menuAction = QAction("Servers", self)
        menuAction.setMenu(submenu)
        self.menu.addAction(menuAction)

        # submenu - cahtbots
        submenu = QMenu()
        for i in (
            "llamacpp",
            "ollamachat",
            "groqchat",
            "chatgpt",
            "geminipro",
            "geminiprovision",
            "palm2",
            "codey",
        ):
            action = QAction(i[:-4] if i.endswith("chat") else i, self)
            action.triggered.connect(partial(self.runFreeGeniusCommand, i))
            submenu.addAction(action)

        menuAction = QAction("Chatbots", self)
        menuAction.setMenu(submenu)
        self.menu.addAction(menuAction)

        # submenu - autogen agents
        submenu = QMenu()
        for i in ("autoassist", "autoretriever", "autobuilder"):
            action = QAction(i, self)
            action.triggered.connect(partial(self.runFreeGeniusCommand, i))
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
            action.triggered.connect(partial(self.runFreeGeniusCommand, i))
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
                    action.triggered.connect(partial(self.runFreeGeniusCommand, i))
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
        self.chatGui.hide()
        self.chatGui.show()

    def runFreeGeniusCommand(self, command):
        def createShortcutFile(filePath, content):
            with open(filePath, "w", encoding="utf-8") as fileObj:
                fileObj.write(content)

        shortcut_dir = os.path.join(freeGeniusAIFolder, "shortcuts")
        Path(shortcut_dir).mkdir(parents=True, exist_ok=True)

        # The following line does not work on Windows
        commandPath = os.path.join(os.path.dirname(sys.executable), command)

        if thisOS == "Windows":
            opencommand = "start"
            filePath = os.path.join(shortcut_dir, f"{command}.bat")
            if not os.path.isfile(filePath):
                filenames = {
                    package: "main.py",
                    "etextedit": "eTextEdit.py",
                }
                systemTrayFile = os.path.join(freeGeniusAIFolder, filenames.get(command, f"{command}.py"))
                content = f'''powershell.exe -NoExit -Command "{sys.executable} '{systemTrayFile}'"'''
                createShortcutFile(filePath, content)
        elif thisOS == "Darwin":
            opencommand = "open"
            filePath = os.path.join(shortcut_dir, f"{command}.command")
            if not os.path.isfile(filePath):
                content = f"""#!/bin/bash
cd {freeGeniusAIFolder}
{commandPath}"""
                createShortcutFile(filePath, content)
                os.chmod(filePath, 0o755)
        elif thisOS == "Linux":
            opencommand = ""
            for i in ("gio launch", "dex", "exo-open", "xdg-open"):
                # Remarks:
                # 'exo-open' comes with 'exo-utils'
                # 'gio' comes with 'glib2'
                if shutil.which(i.split(" ", 1)[0]):
                    opencommand = i
                    break
            filePath = os.path.join(shortcut_dir, f"{command}.desktop")
            if not os.path.isfile(filePath):
                content = f"""[Desktop Entry]
Version=1.0
Type=Application
Terminal=true
Path={freeGeniusAIFolder}
Exec={commandPath}
Icon={iconFile}
Name={command}"""
                createShortcutFile(filePath, content)
        if opencommand:
            os.system(f"{opencommand} {filePath}")

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    icon = QIcon(iconFile)
    trayIcon = SystemTrayIcon(icon)
    trayIcon.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()