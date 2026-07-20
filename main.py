import sys

from PySide6 import QtWidgets

from widgets import MainWindow


def main():
    """
    Application entry point.
    """

    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
