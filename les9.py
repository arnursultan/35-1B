# Импорт библиотек
import sys              # Для корректного завершения приложения
import random           # Для выбора случайного мема
import requests         # Для отправки HTTP-запроса к API


# Импорт модулей PyQt6
# Базовые элементы интерфейса
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QFileDialog,
    QComboBox, QMessageBox
)

# Инструменты для рисования
from PyQt6.QtGui import (
    QPixmap,     # Работа с изображениями
    QPainter,    # Главный объект для рисования
    QFont,       # Работа со шрифтами
    QColor,      # Цвета
    QPen,        # "Карандаш" для обводки
    QIcon        # Иконка окна
)

# Базовые классы ядра Qt
from PyQt6.QtCore import (
    Qt,          # Константы (выравнивание, режимы)
    QRect,       # Прямоугольник
    QPoint,      # Точка (x, y)
    QTimer       # Таймер для анимации
)


# Класс DraggableText
# Хранит данные одного текста (верхнего или нижнего)
class DraggableText:
    def __init__(self, text="", pos=None):

        self.text = text
        # Сам текст, который будет отображаться

        self.pos = pos or QPoint(0, 0)
        # Позиция центра текста (если не передали — ставим (0,0))

        self.bounding_rect = QRect()
        # Прямоугольная область текста
        # Нужна чтобы понимать: кликнули по тексту или нет

        self.selected = False
        # Выбран ли сейчас этот текст

        self.opacity = 1.0
        # Прозрачность (для анимации появления)

# Класс MemeCanvas
# Это полотно, на котором рисуется картинка и текст
class MemeCanvas(QWidget):

    def __init__(self):
        super().__init__()


        # Данные картинки
        self.pixmap = None
        # Здесь будет храниться изображение мема

        # Настройки текста
        self.font_family = "Impact"         # Шрифт
        self.text_color = QColor("white")  # Цвет текста
        self.stroke_color = QColor("black")# Цвет обводки
        self.stroke_width = 4              # Толщина обводки
        self.font_scale = 1.0              # Масштаб текста
        self.caps_enabled = False          # Включён ли CAPS


        # Создаём два текста
        self.top_text = DraggableText("", QPoint(400, 120))
        self.bottom_text = DraggableText("", QPoint(400, 650))

        self.dragging_object = None
        # Переменная хранит текст, который мы сейчас двигаем мышкой

        # Таймер для анимации
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_text)
        # Каждые 30мс будет вызываться animate_text()

    # Установка изображения
    def set_pixmap(self, pixmap):
        self.pixmap = pixmap
        self.auto_position()   # Автоматически расставляем текст
        self.update()          # Просим Qt перерисовать окно

    # Автоматическое расположение текста
    def auto_position(self):

        w = self.width()
        h = self.height()

        # Верхний текст — 10% сверху
        self.top_text.pos = QPoint(w // 2, int(h * 0.1))

        # Нижний текст — 90% снизу
        self.bottom_text.pos = QPoint(w // 2, int(h * 0.9))

    # При изменении размера окна
    def resizeEvent(self, event):
        self.auto_position()

    # Запуск анимации появления текста
    def start_animation(self):

        self.top_text.opacity = 0
        self.bottom_text.opacity = 0

        self.animation_timer.start(30)
        # Запускаем таймер (30 миллисекунд)

    # Плавное увеличение прозрачности
    def animate_text(self):

        done = True

        for obj in (self.top_text, self.bottom_text):

            if obj.opacity < 1:
                obj.opacity += 0.05
                done = False

        if done:
            self.animation_timer.stop()

        self.update()


    # Главный метод рисования
    def paintEvent(self, event):

        painter = QPainter(self)
        # Создаём объект для рисования

        # Рисуем изображение
        if self.pixmap:

            scaled = self.pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            # Центрируем картинку
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2

            painter.drawPixmap(x, y, scaled)

        # Рисуем тексты
        self.draw_text(painter, self.top_text)
        self.draw_text(painter, self.bottom_text)


    # Автоматический подбор размера шрифта
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

            # Если текст помещается — возвращаем шрифт
            if rect.width() <= max_width and rect.height() <= max_height:
                return font, rect

            size -= 2

        return QFont(self.font_family, 20), QRect()


    # Рисование одного текста
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

        # Обводка
        pen = QPen(self.stroke_color)
        pen.setWidth(self.stroke_width)
        painter.setPen(pen)

        painter.drawText(rect,
                         Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
                         text)

        # Основной текст
        painter.setPen(self.text_color)

        painter.drawText(rect,
                         Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
                         text)

        painter.setOpacity(1.0)

        # Если текст выбран — рисуем рамку
        if obj.selected:
            painter.setPen(QPen(QColor("yellow"), 2, Qt.PenStyle.DashLine))
            painter.drawRect(rect)

    # Работа мыши
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


    # Масштабирование колесиком мыши
    def wheelEvent(self, event):

        if self.top_text.selected or self.bottom_text.selected:

            delta = event.angleDelta().y()

            if delta > 0:
                self.font_scale += 0.05
            else:
                self.font_scale -= 0.05

            self.font_scale = max(0.3, min(2.5, self.font_scale))

            self.update()

# Класс MemeGenerator
# Это главное окно приложения
class MemeGenerator(QWidget):

    def __init__(self):
        super().__init__()

        # Настройка окна
        self.setWindowTitle("🔥 Meme Generator ")
        # Заголовок окна

        self.setGeometry(200, 100, 1200, 900)
        # Позиция окна (x=200, y=100)
        # Размер окна (ширина=1200, высота=900)

        self.setWindowIcon(QIcon("icon.ico"))
        # Устанавливаем иконку приложения
        # (если файл icon.ico есть в папке проекта)


        # Переменные для работы с мемами
        self.memes = []
        # Здесь будет храниться список мемов,
        # полученный с API imgflip

        self.cache = {}
        # Кэш изображений.
        # Ключ = URL картинки
        # Значение = байты изображения
        # Нужно, чтобы не скачивать одно и то же несколько раз

        # Создаём интерфейс
        self.init_ui()


        # Загружаем список мемов С API
        self.fetch_memes()

    # Метод создания интерфейса
    def init_ui(self):

        # Главный вертикальный layout
        layout = QVBoxLayout()

        # Горизонтальный layout для кнопок
        controls = QHBoxLayout()

        # Создаём Canvas (полотно для рисования)
        self.canvas = MemeCanvas()

        # Поля ввода текста
        self.top_input = QLineEdit()
        # Поле для ввода верхнего текста

        self.bottom_input = QLineEdit()
        # Поле для ввода нижнего текста

        # Выбор шрифта
        self.font_combo = QComboBox()

        self.font_combo.addItems([
            "Impact",
            "Arial Black",
            "Comic Sans MS"
        ])
        # Добавляем варианты шрифтов в выпадающий список

        # Когда пользователь меняет шрифт —
        # мы обновляем font_family в canvas
        self.font_combo.currentTextChanged.connect(
            lambda f: setattr(self.canvas, "font_family", f)
        )

        # Кнопки
        self.generate_btn = QPushButton("🎲 Новый мем")
        # Кнопка загрузки случайного мема

        self.save_btn = QPushButton("💾 Сохранить")
        # Кнопка сохранения мема

        # Привязка событий (Сигналы → Слоты)

        # При нажатии загружаем новый мем
        self.generate_btn.clicked.connect(self.load_meme)

        # При нажатии сохраняем изображение
        self.save_btn.clicked.connect(self.save_meme)

        # Когда пользователь печатает —
        # обновляем текст на canvas
        self.top_input.textChanged.connect(self.update_text)
        self.bottom_input.textChanged.connect(self.update_text)

        # Собираем интерфейс
        controls.addWidget(self.generate_btn)
        controls.addWidget(self.save_btn)
        controls.addWidget(self.font_combo)

        layout.addWidget(self.top_input)
        layout.addWidget(self.bottom_input)
        layout.addWidget(self.canvas)
        layout.addLayout(controls)

        self.setLayout(layout)

    # Получение списка мемов с API
    def fetch_memes(self):

        try:
            # Отправляем GET-запрос
            r = requests.get(
                "https://api.imgflip.com/get_memes",
                timeout=5
            )

            # Преобразуем ответ в JSON
            data = r.json()

            # Проверяем успешность ответа
            if data.get("success"):

                # Сохраняем список мемов
                self.memes = data["data"]["memes"]

                # Сразу загружаем первый случайный мем
                self.load_meme()

        except Exception as e:

            # Если произошла ошибка —
            # показываем окно с ошибкой
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Ошибка загрузки мемов:\n{e}"
            )

    # Загрузка случайного мема
    def load_meme(self):

        # Если список пуст — выходим
        if not self.memes:
            return

        # Выбираем случайный мем
        meme = random.choice(self.memes)

        url = meme["url"]

        try:
            # Если мем ещё не скачан —
            # загружаем и кладём в кэш
            if url not in self.cache:
                self.cache[url] = requests.get(url, timeout=5).content

            # Создаём QPixmap
            pixmap = QPixmap()

            # Загружаем картинку из байтов
            pixmap.loadFromData(self.cache[url])

            # Передаём изображение в canvas
            self.canvas.set_pixmap(pixmap)

        except Exception as e:

            QMessageBox.warning(
                self,
                "Ошибка",
                f"Не удалось загрузить мем:\n{e}"
            )

    # Обновление текста на холсте
    def update_text(self):

        # Передаём текст в объекты canvas
        self.canvas.top_text.text = self.top_input.text()
        self.canvas.bottom_text.text = self.bottom_input.text()

        # Просим перерисовать
        self.canvas.update()

    # Сохранение изображения
    def save_meme(self):

        # Открываем диалог выбора файла
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить",
            "meme.png",
            "Images (*.png *.jpg)"
        )

        # Если пользователь выбрал путь
        if file_path:

            # grab() делает снимок виджета canvas
            # и сохраняет его как изображение
            self.canvas.grab().save(file_path)

# Точка входа в программу
if __name__ == "__main__":

    app = QApplication(sys.argv)
    # Создаём главное приложение Qt
    # Оно управляет всем GUI и событиями

    window = MemeGenerator()
    # Создаём главное окно нашего приложения

    window.show()
    # Показываем окно (без show() оно не отобразится)

    sys.exit(app.exec())
    # Запускаем главный цикл обработки событий (event loop)
    # Без этого программа сразу закроется