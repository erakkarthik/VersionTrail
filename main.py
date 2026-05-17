import sys
from PyQt6.QtWidgets import QApplication
from ui import MainWindow

APP_NAME = "VersionTrail"

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

#test