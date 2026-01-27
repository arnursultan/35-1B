#1 Базовое окно
# import sys
# 
# from PyQt6.QtWidgets import QApplication, QWidget
# 
# app = QApplication(sys.argv)
# 
# window = QWidget()
# window.setWindowTitle("Наше первое окно")
# window.resize(400, 400)
# window.show()
# 
# sys.exit(app.exec())

#2 С Декомпозицией
# import sys
# from PyQt6.QtWidgets import QWidget, QApplication
#
# class MainWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.init_ui()
#
#     def init_ui(self):
#         self.setWindowTitle("PyQt6 + Декомпозиция")
#         self.resize(500, 350)
#
# app = QApplication(sys.argv)
# window = MainWindow()
# window.show()
# sys.exit(app.exec())

#3 Окно с кнопками
import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLineEdit,
    QLabel,
    QVBoxLayout
)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PyQt6: Widgets")
        self.resize(400, 300)

        self.label = QLabel("Введите имя:")
        self.input_name = QLineEdit()
        self.button = QPushButton("Нажми меня")

        self.button.clicked.connect(self.on_click)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input_name)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def on_click(self):
        name = self.input_name.text()
        self.label.setText(f"Привет, {name}!")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())








