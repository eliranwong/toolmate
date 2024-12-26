from toolmate import config, convertOutputText
from toolmate.utils.call_llm import CallLLM
from toolmate.gui.worker import QtApiResponseStreamer
from toolmate.utils.tts_utils import TTSUtil
import getpass, requests, json

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QCompleter, QMainWindow, QWidget, QMessageBox, QPlainTextEdit, QProgressBar, QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QComboBox, QPushButton

class CentralWidget(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set up interface
        self.setupUI()
        # set up variables
        self.setupVariables()
    
    def setupVariables(self):
        # username
        self.user = getpass.getuser().split(" ")[0].capitalize()
        self.assistant = config.toolMateAIName.split(" ")[0]
        # load LetMeDoIt AI system message
        config.currentMessages=CallLLM.resetMessages()
        # thread pool
        self.threadpool = QThreadPool()
        # scroll bar
        self.contentScrollBar = self.contentView.verticalScrollBar()
        # operations
        self.newSession = True
        self.lastResponse = ""

    def setupUI(self):
        # a layout with left and right columns and a splitter placed between them
        layout000 = QHBoxLayout()
        self.setLayout(layout000)
        
        widgetLt = QWidget()
        layout000Lt = QVBoxLayout()
        widgetLt.setLayout(layout000Lt)

        widgetRt = QWidget()
        layout000Rt = QVBoxLayout()
        rtTop = QWidget()
        rtTopLayout = QVBoxLayout()
        rtTop.setLayout(rtTopLayout)
        rtBottom = QWidget()
        rtBottomLayout = QVBoxLayout()
        rtBottom.setLayout(rtBottomLayout)
        rtSplitter = QSplitter(Qt.Vertical, self)
        rtSplitter.addWidget(rtTop)
        rtSplitter.addWidget(rtBottom)
        layout000Rt.addWidget(rtSplitter)

        widgetRt.setLayout(layout000Rt)
        
        splitter = QSplitter(Qt.Horizontal, self)
        splitter.addWidget(widgetLt)
        splitter.addWidget(widgetRt)
        layout000.addWidget(splitter)

        # add widgets to left column later
        widgetLt.hide()

        # widgets
        # user input
        self.userInput = QLineEdit()
        self.userInputMultiline = QPlainTextEdit()
        self.userInputMultiline.setPlaceholderText("Enter your request here ...")
        completer = QCompleter([f"@{i}" for i in self.getAllTools()]+["tm -exec", "tmc -exec"])
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setFilterMode(Qt.MatchContains)
        self.userInput.setCompleter(completer)
        self.userInput.setPlaceholderText("Find a tool here ...")
        self.userInput.mousePressEvent = lambda _ : self.userInput.selectAll()
        self.userInput.setClearButtonEnabled(True)
        self.sendButton = QPushButton("Send")
        self.sendButton.clicked.connect(self.submit)
        # content view
        self.contentView = QPlainTextEdit()
        self.contentView.setReadOnly(True)
        self.setFontSize()
        # progress bar
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 0) # Set the progress bar to use an indeterminate progress indicator
        
        # update layout
        rtTopLayout.addWidget(self.contentView)
        rtBottomLayout.addWidget(self.userInput)
        rtBottomLayout.addWidget(self.userInputMultiline)
        rtBottomLayout.addWidget(self.sendButton)
        rtBottomLayout.addWidget(self.progressBar)
        self.progressBar.hide()

        # Connections
        self.userInput.returnPressed.connect(self.addTool)

    def getAllTools(self):
        query = "@"
        endpoint = f"{config.toolmate_api_client_host}:{config.toolmate_api_client_port}/api/tools"

        url = f"""{endpoint}?query={query}"""
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": config.toolmate_api_client_key,
        }
        try:
            response = requests.post(url, headers=headers)
            results = json.loads(response.json())["results"]
            return list(results.keys())
        except Exception as e:
            #response = f"Error: {e}"
            pass
        return []

    def setFontSize(self, index=None):
        if index is not None:
            config.desktopAssistantFontSize = index + 1
        # content view
        font = self.contentView.font()
        font.setPointSize(config.desktopAssistantFontSize)
        self.contentView.setFont(font)
        config.saveConfig()

    def addTool(self):
        toolText = self.userInput.text().strip()
        if toolText:
            self.userInputMultiline.insertPlainText(f" {toolText} ")
            self.userInput.setText("")

    def submit(self):
        toolText = self.userInput.text().strip()
        execute = (toolText in ("tm -exec", "tmc -exec"))
        if execute:
            request = toolText
        else:
            requestText = self.userInputMultiline.toPlainText().strip()
            request = f"{toolText} {requestText}".strip()
        if request:
            self.userInput.setDisabled(True)
            self.addContent(request)

            if request in ("tm -exec", "tmc -exec"):
                request = "@command" if "```command" in self.lastResponse else "@execute_python_code"

            self.sendButton.hide()
            self.progressBar.show()
            QtApiResponseStreamer(self).workOnRequest(request, chat=False if self.newSession else True)
            self.newSession = False

            if not execute:
                self.userInputMultiline.setPlainText("")

    def processResponse(self):
        self.userInput.setText("")
        self.userInput.setEnabled(True)
        self.progressBar.hide()
        self.sendButton.show()
        self.userInputMultiline.setFocus()
        # handle user confirmation
        if "Run `tm -exec` or `tmc -exec` to confirm!" in self.lastResponse and self.confirmCodeExecution():
            self.userInput.setText("tm -exec")
            self.submit()

    def confirmCodeExecution(self):
        msgBox = QMessageBox(QMessageBox.Warning,
                             "User confirmation required!",
                             "Do you want to execute the task?",
                             QMessageBox.NoButton, self)
        msgBox.addButton("No", QMessageBox.RejectRole)
        msgBox.addButton("Yes", QMessageBox.AcceptRole)
        answer = msgBox.exec_()
        if answer and not answer == 2:
            return True
        else:
            # Continue
            return False

    def streamResponse(self, apiResponse):
        # in case of group discussion; getting the last message only is not enough
        conversation = json.loads(apiResponse)
        messages = []
        for i in conversation:
            role = i.get("role", "")
            content = i.get("content", "")
            if role in ("user", "assistant"):
                if role == "assistant":
                    content = convertOutputText(content.rstrip())
                    messages.append(f"[{self.assistant}] {content}")
                    self.lastResponse = content
                else:
                    messages.append(f"[{self.user}] {content}")
        self.contentView.setPlainText("\n\n".join(messages))
        self.contentScrollBar.setValue(self.contentScrollBar.maximum())

        #if config.ttsOutput:
        #    TTSUtil.play("")

    def addContent(self, newContent, user=True) -> None:
        content = self.contentView.toPlainText()
        if content:
            self.contentView.insertPlainText("\n\n")
        if user:
            self.contentView.insertPlainText(f"[{self.user}] {newContent}\n\n[{self.assistant}] ")
        else:
            self.contentView.insertPlainText(newContent)

class DesktopAssistant(QMainWindow):
    def __init__(self, standalone=False) -> None:
        super().__init__()
        # check if running standalone
        self.standalone = standalone
        # set title
        self.setWindowTitle(config.toolMateAIName)
        # gui
        self.initUI()
        # shortcuts
        self.processResponse = self.centralWidget.processResponse
        self.streamResponse = self.centralWidget.streamResponse
        self.setFontSize = self.centralWidget.setFontSize

    def closeEvent(self, event):
        if self.standalone:
            event.accept()
        else:
            # hiding it, instead of closing it, to save from reloading time
            event.ignore()
            self.hide()

    def initUI(self):
        config.conversationStarted = False
        self.centralWidget = CentralWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.resize(config.desktopAssistantWidth, config.desktopAssistantHeight)
        #
        self.createMenubar()

    def resizeEvent(self, event):
        size = event.size()
        config.desktopAssistantWidth = size.width()
        config.desktopAssistantHeight = size.height()
        config.saveConfig()
    
    def printTextOutput(self, output):
        self.centralWidget.addContent(output, False)

    def showFontSizeComboBox(self):
        self.fontSizeComboBox = QComboBox()
        self.fontSizeComboBox.setWindowTitle("Select Font Size")
        self.fontSizeComboBox.setFixedWidth(400)
        self.fontSizeComboBox.addItems([str(i) for i in range(1, 51)])
        self.fontSizeComboBox.setCurrentIndex((config.desktopAssistantFontSize - 1))
        self.fontSizeComboBox.currentIndexChanged.connect(self.setFontSize)
        self.fontSizeComboBox.show()

    def toggleAutoPaste(self):
        config.pasteTextOnWindowActivation = not config.pasteTextOnWindowActivation
        config.saveConfig()

    def createMenubar(self):
        # Create a menu bar
        menubar = self.menuBar()

        # Create a File menu and add it to the menu bar
        file_menu = menubar.addMenu("ToolMate AI")

        new_action = QAction("New Session", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.newConversation)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        new_action = QAction("Send", self)
        new_action.setShortcut("Ctrl+S")
        new_action.triggered.connect(self.centralWidget.submit)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        new_action = QAction("Change Font Size", self)
        new_action.triggered.connect(self.showFontSizeComboBox)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        new_action = QAction("Toggle Auto Paste", self)
        new_action.triggered.connect(self.toggleAutoPaste)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        new_action = QAction("Close", self)
        new_action.triggered.connect(self.hide)
        file_menu.addAction(new_action)

        """new_action = QAction("Open", self)
        new_action.setShortcut("Ctrl+O")
        new_action.triggered.connect(self.openConversation)
        file_menu.addAction(new_action)

        new_action = QAction("Save", self)
        new_action.setShortcut("Ctrl+S")
        new_action.triggered.connect(self.saveConversation)
        file_menu.addAction(new_action)

        new_action = QAction("Save As...", self)
        new_action.triggered.connect(self.saveAsConversation)
        file_menu.addAction(new_action)

        new_action = QAction("Export", self)
        new_action.triggered.connect(self.exportConversation)
        file_menu.addAction(new_action)

        file_menu.addSeparator()"""

    def newConversation(self):
        self.centralWidget.contentView.setPlainText("")
        self.centralWidget.newSession = True