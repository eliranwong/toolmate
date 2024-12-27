import os, re, subprocess
from toolmate import config
localStorage = config.localStorage
if os.getcwd() != localStorage:
    os.chdir(localStorage)

try:
    from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QMessageBox
    from PySide6.QtGui import QIcon, QAction, QGuiApplication
    from PySide6.QtCore import QEvent
except:
    print("Module 'gui' not found! Run 'pip install toolmate[gui]' first!")
    exit()

import sys, platform, webbrowser, shutil, pyperclip
from toolmate import startAutogenstudioServer, runToolMateCommand, isServerAlive, print2, getCliOutput
from toolmate.gui.desktop_assistant import DesktopAssistant
#from pathlib import Path
from functools import partial
#from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard
from toolmate.utils.tts_utils import TTSUtil

toolMateAIFile = os.path.realpath(__file__)
toolMateAIFolder = os.path.dirname(toolMateAIFile)
#with open(os.path.join(toolMateAIFolder, "package_name.txt"), "r", encoding="utf-8") as fileObj:
#    package = fileObj.read()
iconFile = os.path.join(toolMateAIFolder, "icons", "ai.png")
thisOS = platform.system()


class ToolMateHub(QSystemTrayIcon):

    def showDesktopAssistant(self):
        # to work with mutliple virtual desktops
        config.desktopAssistant.hide()
        config.desktopAssistant.show()
        config.desktopAssistant.centralWidget.userInputMultiline.setFocus()

    def startApiServer(self):
        host = config.toolmate_api_client_host
        port = config.toolmate_api_client_port_desktop
        if not isServerAlive(re.sub("^(http://|https://)", "", host, re.IGNORECASE), port):
            configFile = os.path.join(config.toolMateAIFolder, "config.py")
            if (os.path.getsize(configFile) == 0 or not hasattr(config, "llmInterface") or not config.llmInterface) and shutil.which("tmsetup"):
                os.system("tmsetup")
            if shutil.which("toolmateserver"):
                print("Loading ToolMate AI ...")
                if shutil.which("nohup"):
                    cli = f'''{shutil.which("nohup")} "{shutil.which("toolmateserver")}" -p {port} > ~/toolmate/nohup-api-server.out 2>&1 &'''
                    os.system(cli)
                else:
                    subprocess.Popen(shutil.which(f"toolmateserver -p {port}"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # wait until the server is up
                while not isServerAlive(re.sub("^(http://|https://)", "", host, re.IGNORECASE), port):
                    pass
                print("ToolMate AI server is now running ...")
            else:
                #print("Failed to connect ToolMate AI! Run `toolmateserver` first!")
                QMessageBox.information(self, "ToolMate AI", "Failed to connect ToolMate AI! Run `toolmateserver` first!")

    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)

        # start API server if it is not running
        self.startApiServer()

        # pre-load desktop assistant gui
        config.desktopAssistant = DesktopAssistant()

        #self.clipboard = PyperclipClipboard()
        self.menu = QMenu(parent)

        #if config.developer:
        chatgui = QAction("Desktop Assistant", self)
        chatgui.triggered.connect(self.showDesktopAssistant)
        self.menu.addAction(chatgui)
        self.menu.addSeparator()

        action = QAction("ToolMate Terminal", self)
        action.triggered.connect(partial(runToolMateCommand, "toolmate"))
        self.menu.addAction(action)
        self.menu.addSeparator()

        """for i in ("toolmate", "letmedoit"):
            action = QAction(i, self)
            action.triggered.connect(partial(runToolMateCommand, i))
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
            action.triggered.connect(partial(runToolMateCommand, i))
            submenu.addAction(action)

        menuAction = QAction("Servers", self)
        menuAction.setMenu(submenu)
        self.menu.addAction(menuAction)

        # submenu - cahtbots
        submenu = QMenu()
        for i in (
            "llamacpppython",
            "llamacppserver",
            "ollamachat",
            "groqchat",
            "openai",
            "geminipro",
            "geminiprovision",
            "palm2",
            "codey",
        ):
            action = QAction(i[:-4] if i.endswith("chat") else i, self)
            action.triggered.connect(partial(runToolMateCommand, i))
            submenu.addAction(action)

        menuAction = QAction("Chatbots", self)
        menuAction.setMenu(submenu)
        self.menu.addAction(menuAction)"""

        # submenu - researches
        submenu = QMenu()

        action = QAction("NotebookLM", self)
        action.triggered.connect(lambda: webbrowser.open("https://notebooklm.google.com/"))
        submenu.addAction(action)

        for key, value in config.customUrls.items():
            action = QAction(key, self)
            action.triggered.connect(partial(webbrowser.open, value))
            submenu.addAction(action)

        menuAction = QAction("Researches", self)
        menuAction.setMenu(submenu)
        self.menu.addAction(menuAction)

        # submenu - autogen agents
        submenu = QMenu()
        for i in ("autoassist", "autoretrieve", "autobuild", "autocaptain"):
            action = QAction(i, self)
            action.triggered.connect(partial(runToolMateCommand, i))
            submenu.addAction(action)

        # autogenstudio
        action = QAction("autogenstudio", self)
        action.triggered.connect(startAutogenstudioServer)
        submenu.addAction(action)

        menuAction = QAction("AutoGen Agents", self)
        menuAction.setMenu(submenu)
        self.menu.addAction(menuAction)

        # submenu - clipboard
        """submenu = QMenu()

        action = QAction("read", self)
        action.triggered.connect(self.readClipboard)
        submenu.addAction(action)

        action = QAction("prompt", self)
        action.triggered.connect(lambda: runToolMateCommand("toolmate -p true -u false -n true -i false"))
        submenu.addAction(action)

        action = QAction("summarize", self)
        action.triggered.connect(lambda: runToolMateCommand("toolmate -rp true -u false -n true -i false -c 'Let me Summarize'"))
        submenu.addAction(action)

        action = QAction("explain", self)
        action.triggered.connect(lambda: runToolMateCommand("toolmate -rp true -u false -n true -i false -c 'Let me Explain'"))
        submenu.addAction(action)

        action = QAction("translate", self)
        action.triggered.connect(lambda: runToolMateCommand("toolmate -rp true -u false -n true -i false -c 'Let me Translate'"))
        submenu.addAction(action)

        action = QAction("edit", self)
        action.triggered.connect(lambda: runToolMateCommand("etextedit -p true"))
        submenu.addAction(action)

        menuAction = QAction("Clipboard", self)
        menuAction.setMenu(submenu)
        self.menu.addAction(menuAction)

        # submenu - utilities
        submenu = QMenu()

        action = QAction("perplexica", self)
        action.triggered.connect(self.launchPerplexica)
        submenu.addAction(action)

        if hasattr(config, "searx_tabs"):
            action = QAction("searxng", self)
            action.triggered.connect(lambda: webbrowser.open(f"http://{config.searx_server}:{config.searx_port}"))
            submenu.addAction(action)

        for i in (
            #"rag",
            "etextedit",
            "commandprompt",
        ):
            action = QAction(i, self)
            action.triggered.connect(partial(runToolMateCommand, i))
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
                    action.triggered.connect(partial(runToolMateCommand, i))
                    submenu.addAction(action)

        menuAction = QAction("Custom", self)
        menuAction.setMenu(submenu)
        self.menu.addAction(menuAction)"""

        self.menu.addSeparator()

        action = QAction("Edit Configurations", self)
        action.triggered.connect(partial(runToolMateCommand, "tmsetup -m"))
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

        # show desktop assistant on startup
        config.desktopAssistant.show()
        config.desktopAssistant.centralWidget.userInputMultiline.setFocus()

    def exit(self):
        self.setVisible(False)
        QGuiApplication.instance().quit()

    def readClipboard(self):
        if config.terminalEnableTermuxAPI:
            clipboardText = getCliOutput("termux-clipboard-get")
        else:
            clipboardText = self.clipboard.get_data().text
        TTSUtil.play(re.sub(config.tts_doNotReadPattern, "", clipboardText))

    def launchPerplexica(self):
        current_dir = os.getcwd()
        if config.perplexica_directory and not os.path.isdir(config.perplexica_directory):
            config.perplexica_directory = ""
            config.saveConfig()
        if not config.perplexica_directory:
            perplexica_directory = os.path.join(config.localStorage, "Perplexica")
            if os.path.isdir(perplexica_directory):
                config.perplexica_directory = perplexica_directory
                config.saveConfig()
            elif shutil.which("git") and shutil.which("docker") and thisOS == "Linux":
                os.chdir(config.localStorage)
                print2("Setting up 'Perplexica' ...")
                try:
                    os.system(f"{shutil.which('git')} clone https://github.com/ItzCrazyKns/Perplexica.git")
                    os.chdir(perplexica_directory)
                    os.system(f"{shutil.which('docker')} compose up -d")
                    config.perplexica_directory = perplexica_directory
                    config.saveConfig()
                except:
                    print2("Failed setting up Perplexica! Read: https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Perplexica%20Integration.md for manual setup.")
                    webbrowser.open("https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Perplexica%20Integration.md")
        if config.perplexica_directory:
            if not isServerAlive(config.perplexica_ip, config.perplexica_port):
                os.chdir(config.perplexica_directory)
                os.system(f"{shutil.which('docker')} compose up -d")
            while not isServerAlive(config.perplexica_ip, config.perplexica_port):
                ...
            webbrowser.open(f"http://{config.perplexica_ip}:{config.perplexica_port}")
        else:
            QMessageBox.information(self.menu, "ToolMate AI", "Perplexica not found!")
        os.chdir(current_dir)


class TM(QApplication):
    
    def __init__(self, argv):
        super().__init__(argv)
        config.mainWindowHidden = False
        self.lastInsertedText = ""

    # Open Desktop Assistant on application activate
    def event(self, event):
        if event.type() == QEvent.ApplicationActivate and hasattr(config, "desktopAssistant") and (not config.desktopAssistant.isVisible() or not config.desktopAssistant.isActiveWindow()):
            config.desktopAssistant.show()
            clipboardText = pyperclip.paste()
            insertedText = f"# Context\n\n{clipboardText}" if clipboardText else ""
            if config.pasteTextOnWindowActivation and insertedText and not (insertedText == self.lastInsertedText) and not config.desktopAssistant.centralWidget.userInputMultiline.toPlainText().endswith(insertedText):
                config.desktopAssistant.centralWidget.userInputMultiline.insertPlainText(insertedText)
                self.lastInsertedText = insertedText
        """
#!/usr/bin/env bash

# work with text selection
# Install `xsel` and `xdotool`
# > apt install xsel xdotool
# To use this script, users need to:
# 1. Launch "Settings"
# 2. Go to "Keyboard" > "Keyboard Shortcuts" > "View and Customise Shortcuts" > "Custom Shortcuts"
# 3. Select "+" to add a custom shortcut and enter the following information, e.g.:

# Name: ToolMate AI
# Command: /home/username/toolmate/ToolMate
# Shortcut: Ctrl + Alt + L

selected_text=$(echo "$(xsel -o)" | sed 's/"/\"/g')
echo $selected_text | xsel --clipboard
toolmate=$(xdotool search --name "ToolMate AI")
xdotool windowmap $toolmate
xdotool windowactivate $toolmate
#xdotool type --window $toolmate $selected_text
        """
        return super().event(event)


def main():
    #app = QApplication(sys.argv)
    app = TM(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    icon = QIcon(iconFile)
    trayIcon = ToolMateHub(icon)
    trayIcon.show()

    # unload llama.cpp model to free VRAM
    try:
        config.llamacppToolModel.close()
        print("Llama.cpp model unloaded!")
    except:
        pass

    sys.exit(app.exec())

if __name__ == "__main__":
    main()