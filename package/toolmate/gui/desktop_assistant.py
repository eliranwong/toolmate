from toolmate import config
from toolmate.utils.call_llm import CallLLM
from toolmate.utils.tool_plugins import Plugins
from toolmate.gui.worker import Worker
import json, getpass

from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtCore import Qt, QThread, QRegularExpression, QRunnable, Slot, Signal, QObject, QThreadPool
from PySide6.QtGui import QStandardItemModel, QStandardItem, QGuiApplication, QAction, QIcon, QFontMetrics, QTextDocument
from PySide6.QtWidgets import QCompleter, QMenu, QSystemTrayIcon, QApplication, QMainWindow, QWidget, QDialog, QFileDialog, QDialogButtonBox, QFormLayout, QLabel, QMessageBox, QCheckBox, QPlainTextEdit, QProgressBar, QPushButton, QListView, QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QComboBox

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

    def setupUI(self):
        # a layout with left and right columns and a splitter placed between them
        layout000 = QHBoxLayout()
        self.setLayout(layout000)
        
        widgetLt = QWidget()
        layout000Lt = QVBoxLayout()
        widgetLt.setLayout(layout000Lt)
        widgetRt = QWidget()
        layout000Rt = QVBoxLayout()
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
        completer = QCompleter(config.inputSuggestions)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setFilterMode(Qt.MatchContains)
        self.userInput.setCompleter(completer)
        self.userInput.setPlaceholderText("Enter your request here ...")
        self.userInput.mousePressEvent = lambda _ : self.userInput.selectAll()
        self.userInput.setClearButtonEnabled(True)
        # content view
        self.contentView = QPlainTextEdit()
        self.contentView.setReadOnly(True)
        # progress bar
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 0) # Set the progress bar to use an indeterminate progress indicator
        
        # update layout
        layout000Rt.addWidget(self.userInput)
        layout000Rt.addWidget(self.contentView)
        layout000Rt.addWidget(self.progressBar)
        self.progressBar.hide()

        # Connections
        self.userInput.returnPressed.connect(self.submit)

    def submit(self):
        if request := self.userInput.text().strip():
            self.userInput.setDisabled(True)
            self.addContent(request)

        self.progressBar.show()
        config.toolmate.runMultipleActions(request, True)

    def processResponse(self):
        self.userInput.setText("")
        self.userInput.setEnabled(True)
        self.progressBar.hide()
        self.userInput.setFocus()

    def streamResponse(self, content):
        self.contentView.insertPlainText(content)
        self.contentScrollBar.setValue(self.contentScrollBar.maximum())

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
        # set variables
        #self.setupVariables()
        # run plugins
        Plugins.runPlugins()
        # gui
        self.initUI()
        # shortcuts
        self.processResponse = self.centralWidget.processResponse
        self.streamResponse = self.centralWidget.streamResponse

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

    def createMenubar(self):
        # Create a menu bar
        menubar = self.menuBar()

        # Create a File menu and add it to the menu bar
        file_menu = menubar.addMenu("Chat")

        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.newConversation)
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
        config.toolmate.saveChat(config.currentMessages)
        config.currentMessages = CallLLM.resetMessages()
        self.centralWidget.contentView.setPlainText("")

    def openConversation(self):
        ...