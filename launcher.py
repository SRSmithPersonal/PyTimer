import sys
from PyQt6.QtWidgets import QApplication
from PythonScripts.gui import MyWidget


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()