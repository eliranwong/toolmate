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
from freegenius.utils.shared_utils import SharedUtil
from freegenius.utils.tool_plugins import Plugins
from freegenius.utils.tool_plugins import ToolStore
from freegenius import print1, print2, print3
config.divider = "--------------------"
ToolStore.setupToolStoreClient()
os.environ["TOKENIZERS_PARALLELISM"] = config.tokenizers_parallelism

import sys, platform, shutil, webbrowser
from freegenius.gui.chatgui import ChatGui
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction, QGuiApplication
from pathlib import Path
from functools import partial


freeGeniusAIFile = os.path.realpath(__file__)
freeGeniusAIFolder = os.path.dirname(freeGeniusAIFile)
with open(os.path.join(freeGeniusAIFolder, "package_name.txt"), "r", encoding="utf-8") as fileObj:
    package = fileObj.read()
iconFile = os.path.join(freeGeniusAIFolder, "icons", "systemtray.png")
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

        commandPrefix = [
            package,
            "llamacpp",
            "ollamachat",
            "chatgpt",
            "geminipro",
            "geminiprovision",
            "palm2",
            "codey",
            "autoassist",
            "autoretriever",
            "autobuilder",
            "rag",
        ]
        commandSuffix = [
            "etextedit",
            "commandprompt",
        ]

        commands = commandPrefix + config.customTrayCommands + commandSuffix if hasattr(config, "customTrayCommands") and config.customTrayCommands else commandPrefix + commandSuffix

        for i in commands:
            action = QAction(i, self)
            action.triggered.connect(partial(self.runLetMeDoItCommand, i))
            self.menu.addAction(action)

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

    def runLetMeDoItCommand(self, command):
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