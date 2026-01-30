from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout
)


class MainUI(QWidget):
    def __init__(self):
        super().__init__()

        self.title_label = QLabel("Введите имя:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ваше имя")

        self.hello_button = QPushButton("Поздороваться")
        self.clear_button = QPushButton("Очистить")

        self.result_label = QLabel("")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.hello_button)
        button_layout.addWidget(self.clear_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.name_input)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.result_label)

        self.setLayout(main_layout)
