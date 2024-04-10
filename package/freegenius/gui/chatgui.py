from freegenius import config
from freegenius.utils.call_llm import CallLLM
from freegenius.utils.tool_plugins import Plugins
from freegenius.gui.worker import Worker
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
        self.assistant = config.freeGeniusAIName.split(" ")[0]
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
        # Pass the function to execute
        worker = Worker(self.go_submit, request) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.processResponse)
        worker.signals.progress.connect(self.printStream)
        # Connection
        #worker.signals.finished.connect(None)
        # Execute
        self.threadpool.start(worker)

    def go_submit(self, request, progress_callback) -> None:
        if self.chat_tools(request, progress_callback):
            # extend chat conversation
            self.chat(progress_callback)

    def processResponse(self):
        self.userInput.setText("")
        self.userInput.setEnabled(True)
        self.progressBar.hide()
        self.userInput.setFocus()

    def printStream(self, content):
        self.contentView.insertPlainText(content)
        self.contentScrollBar.setValue(self.contentScrollBar.maximum())

    def addContent(self, newContent, user=True) -> None:
        content = self.contentView.toPlainText()
        if content:
            self.contentView.insertPlainText("\n\n")
        self.contentView.insertPlainText(f"[{self.user}] " if user else f"[{self.assistant}] ")
        self.contentView.insertPlainText(newContent)

    def chat(self, progress_callback) -> None:
        # run completion
        completion = config.oai_client.chat.completions.create(
            model=config.chatGPTApiModel,
            messages=config.currentMessages,
            n=1,
            temperature=config.llmTemperature,
            max_tokens=getDynamicTokens(config.currentMessages, config.toolFunctionSchemas.values()),
            stream=True,
        )
        # display response
        self.addContent("", user=False)
        response = ""
        for chunk in completion:
            if delta_content := chunk.choices[0].delta.content:
                progress_callback.emit(delta_content)
                response += delta_content
        # update message chain
        if response:
            config.currentMessages.append({"role": "assistant", "content": response})

    def chat_tools(self, request, progress_callback) -> bool:
        user_request = {"role": "user", "content": request}
        # temporary update of messages
        messages = config.currentMessages + [user_request]
        # run completion
        completion = config.oai_client.chat.completions.create(
            model=config.chatGPTApiModel,
            messages=messages,
            n=1,
            temperature=config.llmTemperature,
            max_tokens=getDynamicTokens(messages, config.toolFunctionSchemas.values()),
            tools=convertFunctionSignaturesIntoTools(config.toolFunctionSchemas.values()),
            tool_choice="auto",
            stream=True,
        )
        #output = completion.choices[0].message
        for chunk in completion:
            first_delta = chunk.choices[0].delta
            break # consume the first chunk only at this point; just for initial check if this is a tool call or not

        if first_delta.tool_calls:
            function_calls = [i for i in first_delta.tool_calls if i.type == "function"]
            function_arguments = getToolArgumentsFromStreams(completion)
            for function_call in function_calls:
                function_index = function_call.index
                function_name = function_call.function.name
                func_argument = function_arguments[function_index]
                response = config.toolFunctionMethods[function_name](json.loads(func_argument))

                function_call_message = {
                    "role": "assistant",
                    "content": "",
                    "function_call": {
                        "name": function_name,
                        "arguments": func_argument,
                    }
                }

                function_call_response = {
                    "role": "function",
                    "name": function_name,
                    "content": response if response else config.tempContent,
                }
                # empty tempContent
                config.tempContent = ""

                # handle response
                if not response:
                    # update message chain
                    config.currentMessages += [user_request, function_call_message, function_call_response]
                    # function executed without chat extension
                    extendChat = False
                elif response == "[INVALID]":
                    # update message chain
                    config.currentMessages.append(user_request)
                    # function attempted to be executed but found invalid tool applied
                    extendChat = True
                else:
                    # update message chain
                    config.currentMessages += [user_request, function_call_message, function_call_response]
                    # function executed with chat extension
                    extendChat = True
        else:
            # direct answer
            response = ""
            if first_delta_content := first_delta.content:
                response += first_delta_content
            self.addContent(response, user=False)
            # display the rest of the stream
            for chunk in completion:
                if delta_content := chunk.choices[0].delta.content:
                    progress_callback.emit(delta_content)
                    response += delta_content
            # update message chain
            config.currentMessages += [user_request, {"role": "assistant", "content": response}]
            # finish chat
            extendChat = False
        return extendChat

class ChatGui(QMainWindow):
    def __init__(self, standalone=False) -> None:
        super().__init__()
        # check if running standalone
        self.standalone = standalone
        # set title
        self.setWindowTitle(config.freeGeniusAIName)
        # set variables
        #self.setupVariables()
        # run plugins
        Plugins.runPlugins()
        # gui
        self.initUI()

    def closeEvent(self, event):
        if self.standalone:
            event.accept()
        else:
            # hiding it, instead of closing it, to save from reloading time
            event.ignore()
            self.hide()

    def initUI(self):
        self.centralWidget = CentralWidget(self)
        self.setCentralWidget(self.centralWidget)
