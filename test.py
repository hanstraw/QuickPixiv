from PyQt6.QtWidgets import QApplication
from qfluentwidgets import FluentWindow
import sys

class MyWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("none")
        self.resize(800, 600)

if __name__ == "__main__":
    app = QApplication(sys.argv)  #
    window = MyWindow()          
    window.show()
    sys.exit(app.exec())
