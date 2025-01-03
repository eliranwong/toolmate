from toolmate import config, getCurrentDateTime
from toolmate.utils.call_llm import CallLLM
from toolmate.gui.worker import QtApiResponseStreamer
#from toolmate.utils.tts_utils import TTSUtil
import getpass, requests, json, os, time, re
from PIL import ImageGrab
from PySide6.QtCore import Qt, QThreadPool, QDir, QSortFilterProxyModel
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QCompleter, QMainWindow, QWidget, QMessageBox, QPlainTextEdit, QProgressBar, QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QInputDialog, QPushButton, QFileDialog, QTreeView, QFileSystemModel, QTableWidget, QTableWidgetItem, QHeaderView


class ToolSelectionWindow(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Select a Tool")

        # Set a layout
        layout = QVBoxLayout(self)

        # Create a QLineEdit for the regex input
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Enter regex to filter tools")
        layout.addWidget(self.filter_input)

        # Create a QTableWidget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Tool", "Description"])
        layout.addWidget(self.table_widget)

        # Set the resize mode for the columns
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Tool column
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Description column

        # Store and populate the table with data
        self.data = data
        self.populate_table(self.data)

        # Connect signals
        self.filter_input.textChanged.connect(self.filter_table)
        self.table_widget.cellClicked.connect(self.cell_clicked)

    def populate_table(self, data):
        self.table_widget.setRowCount(0)  # Clear existing rows
        for row, (tool, description) in enumerate(data.items()):
            self.table_widget.insertRow(row)
            self.table_widget.setItem(row, 0, QTableWidgetItem(tool))
            self.table_widget.setItem(row, 1, QTableWidgetItem(description))

    def filter_table(self):
        pattern = self.filter_input.text()
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error:
            return  # Invalid regex, do nothing

        filtered_data = {k: v for k, v in self.data.items() if regex.search(k) or regex.search(v)}
        self.populate_table(filtered_data)

    def cell_clicked(self, row, _):
        tool_item = self.table_widget.item(row, 0)
        toolEntry = "@" + tool_item.text()
        if tool_item:
            self.parent.userInputMultiline.insertPlainText(f" {toolEntry} ")


class FileFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        file_name = model.fileName(index)
        if model.isDir(index):
            return True if file_name == "chats" or re.search(r"^[0-9][0-9][0-9][0-9]-[0-9][0-9]$", file_name) else False # display only chats folder and date folders
        return True if re.search(r"^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]_[0-9][0-9]_[0-9][0-9]_[0-9][0-9]\.chat$", file_name) else False # display only chat files


class CentralWidget(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # chat history directory
        self.chatHistoryDir = os.path.join(config.localStorage, "chats")
        # set up interface
        self.setupUI()
        # set up variables
        self.setupVariables()
    
    def setupVariables(self):
        # chat file
        self.chatfile = None
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
        
        self.widgetLt = QWidget()
        layout000Lt = QVBoxLayout()
        self.widgetLt.setLayout(layout000Lt)

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
        splitter.addWidget(self.widgetLt)
        splitter.addWidget(widgetRt)
        layout000.addWidget(splitter)

        # widgets
        # user input
        self.userInput = QLineEdit()
        completer = QCompleter([f"@{i}" for i in self.getAllToolNames()]+["tm -exec", "tmc -exec"])
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setFilterMode(Qt.MatchContains)
        self.userInput.setCompleter(completer)
        self.userInput.setPlaceholderText("Find a tool here ...")
        self.userInput.mousePressEvent = lambda _ : self.userInput.selectAll()
        self.userInput.setClearButtonEnabled(True)
        self.userInput.returnPressed.connect(self.addTool)
        self.userInputMultiline = QPlainTextEdit()
        self.userInputMultiline.setPlaceholderText("Enter your request here ...")
        self.addFileButton = QPushButton("+File")
        self.addFileButton.setToolTip("Add file to request")
        self.addFileButton.clicked.connect(self.insertFilePath)
        self.addFolderButton = QPushButton("+Folder")
        self.addFolderButton.setToolTip("Add file to request")
        self.addFolderButton.clicked.connect(self.insertFolderPath)
        self.addScreenshotButton = QPushButton("+Screenshot")
        self.addScreenshotButton.setToolTip("Add screenshot to request")
        self.addScreenshotButton.clicked.connect(self.insertScreenshot)
        self.sendButton = QPushButton("Send")
        self.sendButton.clicked.connect(self.submit)
        self.addButton = QPushButton("+")
        self.addButton.setFixedWidth(45)
        self.addButton.setToolTip("Add tool to request")
        self.addButton.clicked.connect(self.addTool)
        self.toolsButton = QPushButton("...")
        self.toolsButton.setFixedWidth(45)
        self.toolsButton.setToolTip("Open tool selection window")
        self.toolsButton.clicked.connect(self.openToolSelectionWindow)
        # content view
        self.contentView = QPlainTextEdit()
        self.contentView.setReadOnly(True)
        font = self.contentView.font()
        font.setPointSize(config.desktopAssistantFontSize)
        self.contentView.setFont(font)
        # progress bar
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 0) # Set the progress bar to use an indeterminate progress indicator

        # Set up the file system model
        self.model = QFileSystemModel()
        self.model.setRootPath(self.chatHistoryDir)
        self.model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Files)

        # Set up the filter proxy model
        self.proxy_model = FileFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        # Sort the first column (Name) in descending order
        self.proxy_model.sort(0, Qt.DescendingOrder)

        # Set up the tree view
        self.tree = QTreeView()
        self.tree.setModel(self.proxy_model)
        self.tree.setRootIndex(self.proxy_model.mapFromSource(self.model.index(self.chatHistoryDir)))
        # Show only the first column `Name`
        self.tree.setHeaderHidden(True)
        self.tree.hideColumn(1) # Size
        self.tree.hideColumn(2) # Type
        self.tree.hideColumn(3) # Data Modified
        # file selection action
        self.tree.clicked.connect(self.onFileClicked)

        layout000Lt.addWidget(self.tree)

        # update layout
        addToolWdiget = QWidget()
        addToolLayout = QHBoxLayout()
        addToolLayout.addWidget(self.userInput)
        addToolLayout.addWidget(self.addButton)
        addToolLayout.addWidget(self.toolsButton)
        addToolWdiget.setLayout(addToolLayout)

        addDataWdiget = QWidget()
        addDataLayout = QHBoxLayout()
        addDataLayout.addWidget(self.addFileButton)
        addDataLayout.addWidget(self.addFolderButton)
        addDataLayout.addWidget(self.addScreenshotButton)
        addDataLayout.addWidget(self.sendButton)
        addDataWdiget.setLayout(addDataLayout)

        rtTopLayout.addWidget(self.contentView)
        rtBottomLayout.addWidget(addToolWdiget)
        rtBottomLayout.addWidget(self.userInputMultiline)
        rtBottomLayout.addWidget(addDataWdiget)
        rtBottomLayout.addWidget(self.progressBar)
        self.progressBar.hide()

    def openToolSelectionWindow(self):
        # Create a new QMainWindow to host the ToolSelectionWindow
        toolSelectionWindow = QMainWindow(self)
        toolSelectionWindow.setWindowTitle("Select a Tool")
        # Create an instance of TaskViewerWidget
        toolSelectionWidget = ToolSelectionWindow(self.getAllTools(), self)
        # Set the TaskViewerWidget as the central widget of the new window
        toolSelectionWindow.setCentralWidget(toolSelectionWidget)
        # Show the new window
        toolSelectionWindow.resize(950, 600)
        toolSelectionWindow.show()

    def onFileClicked(self, index):
        index = self.proxy_model.mapToSource(index)
        filePath = self.model.filePath(index)
        self.openChatFile(filePath)

    def openChatFile(self, filePath):
        if os.path.isfile(filePath):
            self.chatfile = filePath
            self.newSession = False
            self.userInput.setText("")
            self.userInputMultiline.setPlainText(".")
            self.submit()
        else:
            self.chatfile = None

    def insertScreenshot(self):
        self.parent.hide()
        time.sleep(1)
        screenshotPath = os.path.join(os.path.expanduser("~"), "toolmate", "images", f"screenshot_{getCurrentDateTime()}.png")
        screenshot = ImageGrab.grab()
        screenshot.save(screenshotPath)
        self.userInputMultiline.insertPlainText(f' "{screenshotPath}" ')
        self.parent.show()

    def insertFilePath(self):
        if filePath := self.getFilePath(title="Add File"):
            self.userInputMultiline.insertPlainText(f' "{filePath}" ')

    def insertFolderPath(self):
        if folderPath := self.getFolderPath():
            self.userInputMultiline.insertPlainText(f' "{folderPath}" ')

    def getFilePath(self, title="Open File"):
        options = QFileDialog.Options()
        filePath, *_ = QFileDialog.getOpenFileName(
            self,
            title,
            os.path.expanduser("~"),
            "All Files (*)",
            "",
            options,
        )
        return filePath if filePath else ""

    def getFolderPath(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(
            self,
            "Add folder",
            os.path.expanduser("~"),
            options,
        )
        return directory if directory else ""

    def getAllToolNames(self):
        allTools = self.getAllTools()
        return list(allTools.keys())

    def getAllTools(self):
        query = "@"
        endpoint = f"{config.toolmate_api_client_host}:{config.toolmate_api_client_port_desktop}/api/tools"

        url = f"""{endpoint}?query={query}"""
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": config.toolmate_api_client_key,
        }
        try:
            response = requests.post(url, headers=headers)
            results = json.loads(response.json())["results"]
            return results
        except Exception as e:
            #response = f"Error: {e}"
            pass
        return {}

    def setFontSize(self):
        integer, ok = QInputDialog.getInt(self,
                                          "Desktop Assistant", "Change font size:", config.desktopAssistantFontSize, 1,
                                          50, 1)
        if ok:
            config.desktopAssistantFontSize = integer
            # content view
            font = self.contentView.font()
            font.setPointSize(config.desktopAssistantFontSize)
            self.contentView.setFont(font)
            config.saveConfig()

    def addTool(self):
        toolText = self.userInput.text().strip()
        if toolText:
            if toolText in ("tm -exec", "tmc -exec"):
                self.submit()
            else:
                self.userInputMultiline.insertPlainText(f" {toolText} ")
                self.userInput.setText("")

    def submit(self):
        toolText = self.userInput.text().strip()
        execute = (toolText in ("tm -exec", "tmc -exec"))
        if execute:
            request = toolText
        else:
            #requestText = self.userInputMultiline.toPlainText().strip()
            #request = f"{toolText} {requestText}".strip()
            request = self.userInputMultiline.toPlainText().strip()
        if request:
            self.userInput.setDisabled(True)
            self.addContent(request)

            if request in ("tm -exec", "tmc -exec"):
                request = "@command" if "```command" in self.lastResponse else "@execute_python_code"

            self.sendButton.hide()
            self.progressBar.show()
            QtApiResponseStreamer(self).workOnRequest(request, chat=False if self.newSession else True, chatfile=self.chatfile)
            self.chatfile = None
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
            if role in ("user", "assistant") and content.strip():
                if role == "assistant":
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
            self.contentView.setPlainText(content + "\n\n")
        if user:
            self.contentView.setPlainText(content + f"\n\n[{self.user}] {newContent}\n\n[{self.assistant}] ")
        else:
            self.contentView.setPlainText(content + newContent)

    def newConversation(self):
        self.contentView.setPlainText("")
        self.newSession = True

    def openConversation(self):
        if filePath := self.getFilePath(title="Open Chat File"):
            self.openChatFile(filePath)

    def saveConversation(self):
        current_newSession = self.newSession
        current_toolText = self.userInput.text()
        current_request = self.userInputMultiline.toPlainText().strip()
        self.newSession = True
        self.userInput.setText("")
        self.userInputMultiline.setPlainText(".")
        self.submit()
        self.newSession = current_newSession
        self.userInput.setText(current_toolText)
        self.userInputMultiline.setPlainText(current_request)

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

    def toggleAutoPaste(self):
        config.pasteTextOnWindowActivation = not config.pasteTextOnWindowActivation
        config.saveConfig()

    def toolgeChatHistory(self):
        self.centralWidget.widgetLt.hide() if self.centralWidget.widgetLt.isVisible() else self.centralWidget.widgetLt.show()

    def createMenubar(self):
        # Create a menu bar
        menubar = self.menuBar()

        # Create a File menu and add it to the menu bar
        file_menu = menubar.addMenu("Chat")

        new_action = QAction("New Session", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.centralWidget.newConversation)
        file_menu.addAction(new_action)

        new_action = QAction("Open", self)
        new_action.setShortcut("Ctrl+O")
        new_action.triggered.connect(self.centralWidget.openConversation)
        file_menu.addAction(new_action)

        new_action = QAction("Save", self)
        new_action.setShortcut("Ctrl+W")
        new_action.triggered.connect(self.centralWidget.saveConversation)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        new_action = QAction("Send", self)
        new_action.setShortcut("Ctrl+S")
        new_action.triggered.connect(self.centralWidget.submit)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        new_action = QAction("Change Font Size", self)
        new_action.triggered.connect(self.centralWidget.setFontSize)
        file_menu.addAction(new_action)

        file_menu.addSeparator()
        
        new_action = QAction("Toggle Auto Paste", self)
        new_action.triggered.connect(self.toggleAutoPaste)
        file_menu.addAction(new_action)

        new_action = QAction("Toggle Chat History", self)
        new_action.triggered.connect(self.toolgeChatHistory)
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