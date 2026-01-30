class Logic:
    def __init__(self, ui):
        self.ui = ui
        self.connect_signals()

    def connect_signals(self):
        self.ui.hello_button.clicked.connect(self.say_hello)
        self.ui.clear_button.clicked.connect(self.clear)

    def say_hello(self):
        name = self.ui.name_input.text()

        if name:
            self.ui.result_label.setText(f"Привет, {name}!")
        else:
            self.ui.result_label.setText("Введите имя")

    def clear(self):
        self.ui.name_input.clear()
        self.ui.result_label.clear()
