import sys
import random
import requests

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QFileDialog,
    QComboBox, QMessageBox
)
from PyQt6.QtGui import (
    QPixmap, QPainter, QFont,
    QColor, QPen, QIcon
)
from PyQt6.QtCore import Qt, QRect, QPoint, QTimer


class DraggableText:
    def __init__(self, text="", pos=None):
        self.text = text
        self.pos = pos or QPoint(0, 0)
        self.bounding_rect = QRect()
        self.selected = False
        self.opacity = 1.0


class MemeCanvas(QWidget):
    def __init__(self):
        super().__init__()


        self.pixmap = None
        self.font_family = "Impact"
        self.text_color = QColor("white")
        self.stroke_color = QColor("black")
        self.stroke_width = 4
        self.font_scale = 1.0
        self.caps_enabled = False

        self.top_text = DraggableText("", QPoint(400, 120))
        self.bottom_text = DraggableText("", QPoint(400, 650))
        self.dragging_object = None

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_text)

    def set_pixmap(self, pixmap):
        self.pixmap = pixmap
        self.auto_position()
        self.update()

    def auto_position(self):
        w, h = self.width(), self.height()
        self.top_text.pos = QPoint(w // 2, int(h * 0.1))
        self.bottom_text.pos = QPoint(w // 2, int(h * 0.9))

    def resizeEvent(self, event):
        self.auto_position()

    def start_animation(self):
        self.top_text.opacity = 0
        self.bottom_text.opacity = 0
        self.animation_timer.start(30)

    def animate_text(self):
        done = True
        for obj in (self.top_text, self.bottom_text):
            if obj.opacity < 1:
                obj.opacity = min(1, obj.opacity + 0.05)
                done = False

        if done:
            self.animation_timer.stop()

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.pixmap:
            scaled = self.pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

        self.draw_text(painter, self.top_text)
        self.draw_text(painter, self.bottom_text)

    def auto_fit_font(self, painter, text, max_width, max_height):
        size = int(120 * self.font_scale)

        while size > 10:
            font = QFont(self.font_family, size)
            font.setBold(True)
            painter.setFont(font)

            rect = painter.boundingRect(
                QRect(0, 0, max_width, max_height),
                Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
                text
            )

            if rect.width() <= max_width and rect.height() <= max_height:
                return font, rect

            size -= 2

        return QFont(self.font_family, 20), QRect()

    def draw_text(self, painter, obj):
        if not obj.text:
            return

        text = obj.text.upper() if self.caps_enabled else obj.text
        max_width = int(self.width() * 0.9)
        max_height = int(self.height() * 0.4)

        font, rect = self.auto_fit_font(painter, text, max_width, max_height)
        rect.moveCenter(obj.pos)
        obj.bounding_rect = rect

        painter.setFont(font)
        painter.setOpacity(obj.opacity)

        pen = QPen(self.stroke_color)
        pen.setWidth(self.stroke_width)
        painter.setPen(pen)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, text)

        painter.setPen(self.text_color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, text)

        painter.setOpacity(1.0)

        if obj.selected:
            painter.setPen(QPen(QColor("yellow"), 2, Qt.PenStyle.DashLine))
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        pos = event.position().toPoint()

        for obj in (self.top_text, self.bottom_text):
            obj.selected = obj.bounding_rect.contains(pos)
            if obj.selected:
                self.dragging_object = obj

        self.update()

    def mouseMoveEvent(self, event):
        if self.dragging_object:
            self.dragging_object.pos = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging_object = None

    def wheelEvent(self, event):
        if self.top_text.selected or self.bottom_text.selected:
            delta = event.angleDelta().y()
            self.font_scale += 0.05 if delta > 0 else -0.05
            self.font_scale = max(0.3, min(2.5, self.font_scale))
            self.update()

class MemeGenerator(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("🔥 Meme Generator ")
        self.setGeometry(200, 100, 1200, 900)
        self.setWindowIcon(QIcon("icon.ico"))

        self.memes = []
        self.cache = {}

        self.init_ui()
        self.fetch_memes()

    def init_ui(self):
        layout = QVBoxLayout()
        controls = QHBoxLayout()

        self.canvas = MemeCanvas()

        self.top_input = QLineEdit()
        self.bottom_input = QLineEdit()

        self.font_combo = QComboBox()
        self.font_combo.addItems(["Impact", "Arial Black", "Comic Sans MS"])
        self.font_combo.currentTextChanged.connect(
            lambda f: setattr(self.canvas, "font_family", f)
        )

        self.generate_btn = QPushButton("🎲 Новый мем")
        self.save_btn = QPushButton("💾 Сохранить")

        self.generate_btn.clicked.connect(self.load_meme)
        self.save_btn.clicked.connect(self.save_meme)

        self.top_input.textChanged.connect(self.update_text)
        self.bottom_input.textChanged.connect(self.update_text)

        controls.addWidget(self.generate_btn)
        controls.addWidget(self.save_btn)
        controls.addWidget(self.font_combo)

        layout.addWidget(self.top_input)
        layout.addWidget(self.bottom_input)
        layout.addWidget(self.canvas)
        layout.addLayout(controls)

        self.setLayout(layout)

    def fetch_memes(self):
        try:
            r = requests.get("https://api.imgflip.com/get_memes", timeout=5)
            data = r.json()

            if data.get("success"):
                self.memes = data["data"]["memes"]
                self.load_meme()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки мемов:\n{e}")

    def load_meme(self):
        if not self.memes:
            return

        meme = random.choice(self.memes)
        url = meme["url"]

        try:
            if url not in self.cache:
                self.cache[url] = requests.get(url, timeout=5).content

            pixmap = QPixmap()
            pixmap.loadFromData(self.cache[url])
            self.canvas.set_pixmap(pixmap)

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить мем:\n{e}")

    def update_text(self):
        self.canvas.top_text.text = self.top_input.text()
        self.canvas.bottom_text.text = self.bottom_input.text()
        self.canvas.update()

    def save_meme(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить", "meme.png", "Images (*.png *.jpg)"
        )

        if file_path:
            self.canvas.grab().save(file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemeGenerator()
    window.show()
    sys.exit(app.exec())