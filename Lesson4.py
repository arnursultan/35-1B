import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QListWidget
)

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    group_name TEXT
)
""")
conn.commit()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Урок 4 CRUD Students")
        self.setGeometry(300, 200, 300, 400)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя")

        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Возраст")

        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText("Группа")

        self.add_btn = QPushButton("Добавить студента")
        self.add_btn.clicked.connect(self.add_student)

        self.list_widget = QListWidget()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Добавление студента"))
        layout.addWidget(self.name_input)
        layout.addWidget(self.age_input)
        layout.addWidget(self.group_input)
        layout.addWidget(self.add_btn)
        layout.addWidget(QLabel("Список студентов"))
        layout.addWidget(self.list_widget)

        self.setLayout(layout)
        self.load_students()

    def add_student(self):
        name = self.name_input.text()
        age = self.age_input.text()
        group = self.group_input.text()

        if name and age and group:
            cursor.execute(
                "INSERT INTO students (name, age, group_name) VALUES (?, ?, ?)",
                (name, age, group)
            )
            conn.commit()
            self.load_students()

            self.name_input.clear()
            self.age_input.clear()
            self.group_input.clear()

    def load_students(self):
        self.list_widget.clear()
        cursor.execute("SELECT name, age, group_name FROM students")
        students = cursor.fetchall()

        for s in students:
            self.list_widget.addItem(f"{s[0]} | {s[1]} | {s[2]}")


app = QApplication(sys.argv)
window = App()
window.show()
sys.exit(app.exec())