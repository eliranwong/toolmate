from freegenius import config
from freegenius.utils.shared_utils import SharedUtil
from PySide6.QtWidgets import QApplication, QInputDialog
import json, sys


class QuickTask:

    def __init__(self) -> None:
        SharedUtil.setAPIkey() # create a gui for it later
        SharedUtil.runPlugins()
        def stopSpinning():
            ...
        config.stopSpinning = stopSpinning

    def run(self, default="", standalone=True) -> None:
        if standalone:
            QApplication(sys.argv)
        gui_title = "LetMeDoIt AI"
        about = "Enter your request:"
        def runGui(thisDefault) -> bool:
            dialog = QInputDialog()

            dialog.setInputMode(QInputDialog.TextInput)
            dialog.setWindowTitle(gui_title)
            dialog.setLabelText(about)
            dialog.setTextValue(thisDefault)

            # Set size of dialog here
            dialog.resize(500, 100)  # You can adjust the values according to your requirement

            if dialog.exec():
                request = dialog.textValue()
                self.resolve(request)
                return True
            else:
                return False
        if config.isTermux:
            if not default:
                print(gui_title)
                print(about)
                default = input(">>> ")
            self.resolve(default)
        else:
            while runGui(default):
                default = ""

    def resolve(self, request) -> str:
        messages=SharedUtil.resetMessages(prompt=request)
        completion = config.oai_client.chat.completions.create(
            model=config.chatGPTApiModel,
            messages=messages,
            n=1,
            temperature=config.llmTemperature,
            max_tokens=SharedUtil.getDynamicTokens(messages, config.chatGPTApiFunctionSignatures.values()),
            tools=SharedUtil.convertFunctionSignaturesIntoTools(config.chatGPTApiFunctionSignatures.values()),
            tool_choice="auto",
            #stream=True,
        )
        output = completion.choices[0].message
        if output.content:
            response = output.content
        elif output.tool_calls:
            for tool_call in output.tool_calls:
                tool = tool_call.function
                name, arguments = tool.name, tool.arguments
                response = config.chatGPTApiAvailableFunctions[name](json.loads(arguments))
        else:
            response = ""
        # ignore response for now
        return response
