import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt6 Lesson3 Second Code")
        self.resize(450, 320)

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        self.title_label = QLabel("Анкета пользователя")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите имя")

        self.language_box = QComboBox()
        self.language_box.addItems(["Python", "JavaScript", "Java", "C++", "GO"])

        self.is_student_checkbox = QCheckBox("Я студент")

        self.submit_button = QPushButton("Отправить")
        self.clear_button = QPushButton("Очистить")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.clear_button)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(QLabel("Имя:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Язык программирования"))
        layout.addWidget(self.language_box)
        layout.addWidget(self.is_student_checkbox)
        layout.addStretch()
        layout.addLayout(button_layout)