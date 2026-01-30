import sys
from PyQt6.QtWidgets import QApplication

from ui import MainUI
from logic import Logic
import config


def main():
    app = QApplication(sys.argv)

    window = MainUI()
    window.setWindowTitle(config.APP_TITLE)
    window.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

    logic = Logic(window)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()