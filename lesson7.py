import sys
import psycopg2
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QListWidget
)
conn = psycopg2.connect(
    host="localhost",
    database="db35b",
    port="5433",
    user="postgres",
    password="Nursultan04"
)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name TEXT
)
""")
conn.commit()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CRUD")

        layout = QVBoxLayout()

        self.input = QLineEdit()
        self.list = QListWidget()

        self.add_btn = QPushButton("Добавить")
        self.del_btn = QPushButton("Удалить")
        self.refresh_btn = QPushButton("Обновить")

        layout.addWidget(self.input)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.del_btn)
        layout.addWidget(self.refresh_btn)
        layout.addWidget(self.list)

        self.setLayout(layout)

        self.add_btn.clicked.connect(self.add)
        self.del_btn.clicked.connect(self.delete)
        self.refresh_btn.clicked.connect(self.load)

        self.load()

    def load(self):
        self.list.clear()
        cur.execute("SELECT id, name FROM students ORDER BY id")
        for row in cur.fetchall():
            self.list.addItem(f"{row[0]}: {row[1]}")

    def add(self):
        name = self.input.text()
        cur.execute("INSERT INTO students(name) VALUES(%s)", (name,))
        conn.commit()
        self.load()

    def delete(self):
        item = self.list.currentItem()
        if item:
            student_id = item.text().split(":")[0]
            cur.execute("DELETE FROM students WHERE id=%s", (student_id,))
            conn.commit()
            self.load()

app = QApplication(sys.argv)
window = App()
window.show()
sys.exit(app.exec())