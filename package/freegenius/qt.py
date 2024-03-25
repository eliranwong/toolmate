import sys
from freegenius.gui.chatgui import ChatGui
from PySide6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    ChatGui(standalone=True).show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()