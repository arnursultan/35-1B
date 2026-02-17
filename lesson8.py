import sys
import psycopg2
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QListWidget,
    QComboBox, QLabel
)

conn = psycopg2.connect(
    host="localhost",
    database="db35_1b",
    port="5433",
    user="postgres",
    password="Nursultan04"
)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    title TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name TEXT,
    group_id INTEGER REFERENCES groups(id)
)
""")
conn.commit()


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Students & Groups")

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя студента")

        self.group_box = QComboBox()

        self.add_group_btn = QPushButton("Добавить группу")
        self.add_student_btn = QPushButton("Добавить студента")

        self.list = QListWidget()

        layout.addWidget(QLabel("Имя:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Группа:"))
        layout.addWidget(self.group_box)
        layout.addWidget(self.add_group_btn)
        layout.addWidget(self.add_student_btn)
        layout.addWidget(self.list)

        self.setLayout(layout)

        self.add_group_btn.clicked.connect(self.add_group)
        self.add_student_btn.clicked.connect(self.add_student)

        self.load_groups()
        self.load_students()

    def load_groups(self):
        self.group_box.clear()
        cur.execute("SELECT id, title FROM groups ORDER BY id")
        for gid, title in cur.fetchall():
            self.group_box.addItem(title, gid)

    def load_students(self):
        self.list.clear()
        cur.execute("""
        SELECT students.id, students.name, groups.title
        FROM students
        JOIN groups ON students.group_id = groups.id
        ORDER BY students.id
        """)
        for sid, name, group in cur.fetchall():
            self.list.addItem(f"{sid}: {name} ({group})")

    def add_group(self):
        title = self.name_input.text()
        if title:
            cur.execute("INSERT INTO groups(title) VALUES(%s)", (title,))
            conn.commit()
            self.name_input.clear()
            self.load_groups()

    def add_student(self):
        name = self.name_input.text()
        group_id = self.group_box.currentData()

        if name and group_id:
            cur.execute(
                "INSERT INTO students(name, group_id) VALUES(%s, %s)",
                (name, group_id)
            )
            conn.commit()
            self.name_input.clear()
            self.load_students()


app = QApplication(sys.argv)
window = App()
window.show()
sys.exit(app.exec())
