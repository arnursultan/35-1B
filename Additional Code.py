import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QListWidget, QMessageBox
)

def connect_db():
    return sqlite3.connect("students.database")

def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            group_name INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_student(name, age, group_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, age, group_name) VALUES (?, ?, ?)",
                   (name, age, group_name)
                   )
    conn.commit()
    conn.close()

def read_students():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, group_name FROM students")
    data = cursor.fetchall()
    conn.close()
    return data

def search_students(keyword):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, group_name FROM students WHERE name LIKE ?",
                   (f"%{keyword}%", )
                   )
    data = cursor.fetchall()
    conn.close()
    return data

def update_student(student_id, name, age, group_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE students 
        SET name = ?, age = ?, group_name = ?
        WHERE id = ?
    """, (name, age, group_name, student_id))
    conn.commit()
    conn.close()

def delete_student(student_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crud Доп Код Урок 5")
        self.setGeometry(400, 200, 400, 550)
        self.init_ui()
        self.load_students()

    def init_ui(self):
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя")

        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Возраст")

        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText("Группа")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по имени")

        self.add_btn = QPushButton("Добавить")
        self.update_btn = QPushButton("Изменить")
        self.delete_btn = QPushButton("Удалить")
        self.search_btn = QPushButton("Поиск")
        self.refresh_btn = QPushButton("Обновить")

        self.add_btn.clicked.connect(self.add_student)
        self.update_btn.clicked.connect(self.update_student)
        self.delete_btn.clicked.connect(self.delete_student)
        self.search_btn.clicked.connect(self.search_student)
        self.refresh_btn.clicked.connect(self.load_students)

        self.list_widget = QListWidget()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Данные студента"))
        layout.addWidget(self.id_input)
        layout.addWidget(self.name_input)
        layout.addWidget(self.age_input)
        layout.addWidget(self.group_input)

        layout.addWidget(self.add_btn)
        layout.addWidget(self.update_btn)
        layout.addWidget(self.delete_btn)

        layout.addWidget(QLabel("Поиск"))
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_btn)
        layout.addWidget(self.refresh_btn)

        layout.addWidget(QLabel("Список студентов"))
        layout.addWidget(self.list_widget)

        self.setLayout(layout)

    def add_student(self):
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        group = self.group_input.text().strip()

        if not name or not age or not group:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        if not age.isdigit():
            QMessageBox.warning(self, "Ошибка", "Возраст должен быть числом")
            return

        create_student(name, int(age), group)
        self.clear_inputs()
        self.load_students()

    def load_students(self):
        self.list_widget.clear()
        for s in read_students():
            self.list_widget.addItem(
                f"ID: {s[0]} | {s[1]} | {s[2]} лет | {s[3]}"
            )

    def search_student(self):
        keyword = self.search_input.text().strip()
        self.list_widget.clear()

        for s in search_students(keyword):
            self.list_widget.addItem(
                f"ID: {s[0]} | {s[1]} | {s[2]} лет | {s[3]}"
            )

    def update_student(self):
        student_id = self.id_input.text().strip()
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        group = self.group_input.text().strip()

        if not student_id.isdigit():
            QMessageBox.warning(self, "Ошибка", "Введите корректный ID")
            return

        update_student(int(student_id), name, int(age), group)
        self.clear_inputs()
        self.load_students()

    def delete_student(self):
        student_id = self.id_input.text().strip()

        if not student_id.isdigit():
            QMessageBox.warning(self, "Ошибка", "Введите корректный ID")
            return

        delete_student(int(student_id))
        self.clear_inputs()
        self.load_students()

    def clear_inputs(self):
        self.id_input.clear()
        self.name_input.clear()
        self.age_input.clear()
        self.group_input.clear()

init_db()
app = QApplication(sys.argv)
window = App()
window.show()
sys.exit(app.exec())