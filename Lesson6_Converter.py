import sys, json, urllib.request, ssl, time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QDoubleSpinBox, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

ssl._create_default_https_context = ssl._create_unverified_context

CURRENCIES = ["USD", "EUR", "KGS", "KZT", "UZB", "CNY", "RUB"]

API_MAIN = "https://api.exchangerate.host/convert"
API_BACKUP = "https://open.er-api.com/v6/latest/"

class CurrencyAPI:
    def __init__(self):
        self.cache = {}
        self.cache_time = 60

    def fetch_json(self, url):
        with urllib.request.urlopen(url, timeout=8) as r:
            return json.loads(r.read().decode("utf-8"))

    def get_rate(self, src, dst, amount):
        key = f"{src}_{dst}"

        if key in self.cache:
            rate, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_time:
                return rate * amount

        try:
            url = f"{API_MAIN}?amount={amount}&from={src}&to={dst}"
            data = self.fetch_json(url)
            result = data["rates"][dst]

            rate = result / amount
            self.cache[key] = (rate, time.time())
            return result
        except:
            pass

        try:
            data2 = self.fetch_json(API_BACKUP + src)
            rate = data2["rates"].get(dst)

            if rate:
                self.result = rate * amount
                self.cache[key] = (rate, time.time())
                return rate * amount
        except:
            pass

        raise ValueError("Курс не найден.")

class Converter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Конвертер валют")
        self.resize(420, 220)

        self.api = CurrencyAPI()

        self.amount = QDoubleSpinBox()
        self.amount.setRange(0.0, 1e9)
        self.amount.setDecimals(2)
        self.amount.setValue(100.0)

        self.from_cb = QComboBox()
        self.to_cb = QComboBox()

        self.from_cb.addItems(CURRENCIES)
        self.to_cb.addItems(CURRENCIES)

        self.from_cb.setCurrentText("USD")
        self.to_cb.setCurrentText("KGS")

        self.result = QLabel("-")
        self.result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result.setStyleSheet(
            "font-size:18px; font-weight:bold; margin-top:10px;"
        )

        convert_btn = QPushButton("Конвертировать")
        convert_btn.clicked.connect(self.convert)

        swap_btn = QPushButton("Поменять")
        swap_btn.clicked.connect(self.swap_currencies)

        self.amount.returnPressed.connect(self.convert)

        layout = QVBoxLayout(self)

        for text, widget in [
            ("Сумма:", self.amount),
            ("Из:", self.from_cb),
            ("В:", self.to_cb),
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(text))
            row.addWidget(widget)
            layout.addLayout(row)

        btn_row = QHBoxLayout()
        btn_row.addWidget(convert_btn)
        btn_row.addWidget(swap_btn)

        layout.addLayout(btn_row)
        layout.addWidget(self.result)

    def swap_currencies(self):
        src = self.from_cb.currentText()
        dst = self.to_cb.currentText()
        self.from_cb.setCurrentText(dst)
        self.to_cb.setCurrentText(src)

    def convert(self):
        amount = self.amount.value()
        src = self.from_cb.currentText()
        dst = self.to_cb.currentText()

        if src == dst:
            self.result.setText(f"{amount:.2f} {dst}")
            self.result.setStyleSheet("font-size:18px; color:green;")
            return
        try:
            result = self.api.get_rate(src, dst, amount)
            self.result.setText(f"{amount:.2f} {src} = {result:.2f} {dst}")
            self.result.setStyleSheet("font-size:18px; color:green;")

        except Exception as e:
            self.result.setText("Ошибка получения курса")
            self.result.setStyleSheet("font-size:18px; color:red;")
            QMessageBox.critical(self, "Ошибка", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Converter()
    window.show()
    sys.exit(app.exec())