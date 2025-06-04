import sys
from PyQt6.QtWidgets import QApplication, QMenu, QWidget, QVBoxLayout, QLabel, QDialog, QLineEdit, QSpinBox, QPushButton, QHBoxLayout
from PyQt6.QtCore import QPoint, QRect, QTimer, Qt
from PyQt6.QtGui import QColor, QPainter, QPen, QFont, QBrush, QAction, QPixmap
from PyQt6.QtWidgets import QSlider, QGroupBox
import os
from database import get_parking_spots, get_parking_spot_by_id, get_all_cars
from models.car import Car, CarGenerator
from ui.animations import CarAnimation
from models.parking_spot import ParkingSpot
import time
spots_across = 17
spots_down = 5
FPS = 60
frame_rate = 1000 // FPS
# Колір для різних статусів
COLOR_FREE = QColor(0, 255, 0)  # Зелений (вільно)
COLOR_OCCUPIED = QColor(255, 0, 0)  # Червоний (зайнято)
COLOR_RESERVED = QColor(255, 255, 0)  # Жовтий (зарезервовано)
COLOR_BACKGROUND = QColor(100, 100, 100)  # Сірий (фон)
COLOR_BORDER = QColor(255,255,255)

def get_forecast_text(gen_sleep: float) -> str:
    """Повертає текст прогнозу завантаження паркінгу через певний динамічний час."""
    now = int(time.time())

    spots = get_parking_spots()
    total_spots = len(spots)

    # Поточна кількість зайнятих місць (через статус)
    occupied_now = len([spot for spot in spots if spot.status == "зайнято"])

    # Прогнозований часовий горизонт (10 хв)
    time_window = 60

    # Отримуємо всі авто для визначення
    cars = get_all_cars()

    # Кількість авто, які поїдуть протягом прогнозного вікна
    leaving_soon = len([
        car for car in cars
        if car.departure_time and now < car.departure_time <= now + time_window
    ])

    # Прогнозована генерація нових авто
    gen_sleep /= 10
    if gen_sleep <= 0:
        gen_sleep = 0.1
    estimated_new_cars = int(time_window / gen_sleep)

    # Прогнозована кількість вільних місць
    available_spots_future = total_spots - occupied_now + leaving_soon

    # Реальна кількість нових авто, які зможуть заїхати
    incoming_cars = min(estimated_new_cars, available_spots_future)

    # Прогнозована кількість зайнятих місць
    predicted_occupied = occupied_now - leaving_soon + incoming_cars
    predicted_occupied = max(0, min(predicted_occupied, total_spots))

    percentage = int((predicted_occupied / total_spots) * 100)
    return f"Прогноз (через {time_window // 60} хв): {percentage}% ({predicted_occupied}/{total_spots})"


def get_parking_layout():
    return spots_down, spots_across

def get_clicked_spot(x, y, spots):
    """Перевіряє, на яке паркувальне місце натиснули, і повертає відповідний об'єкт ParkingSpot."""
    for spot in spots:
        if spot.contains(x, y):
            return spot
    return None  # Якщо не потрапили в жодне місце

class ParkingWidget(QWidget):
    def __init__(self, car_generator):
        super().__init__()
        self.setWindowTitle("Паркінг")
        self.setGeometry(100, 100, 1280, 1024)
        self.spots = get_parking_spots()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_parking_status)
        self.timer.start(frame_rate)
        self.popup = None
        self.clicked_spot = None
        self.main_layout = QHBoxLayout(self)

        # Додаємо паркувальну зону (лівий блок)
        self.parking_area = QWidget(self)
        self.main_layout.addWidget(self.parking_area)

        # Завантажуємо зображення воріт
        self.gate_label = QLabel(self)
        gate_path = os.path.join("image", "gate.png")  # Шлях до файлу
        pixmap = QPixmap(gate_path)
        self.gate_label.setFixedSize(200, 200)
        if pixmap.isNull():
            print("Помилка: не вдалося завантажити gate.png")
        else:
            self.gate_label.setPixmap(pixmap)
            self.gate_label.setScaledContents(True)  # Масштабувати під розмір QLabel
         # Додаємо зображення воріт у праву частину екрану
        self.main_layout.addWidget(self.gate_label)

        # **Отримуємо генератор машин із main.py**
        self.car_generator = car_generator
        self.car_generator.car_created.connect(self.start_car_animation)  # Підключаємо сигнали
        self.car_generator.car_leaving.connect(self.start_exit_animation)

        # Створюємо праву панель керування
        self.control_panel = QVBoxLayout()
        self.main_layout.addLayout(self.control_panel)

        # Група для контролю генерації
        self.generator_group = QGroupBox("Керування генерацією авто")
        self.generator_layout = QVBoxLayout()

        # 1. Створюємо панель керування як окремий віджет
        self.control_widget = QWidget(self)
        self.control_widget.setGeometry(1050, 50, 220, 180)  # x, y, width, height
        self.control_widget.setStyleSheet("""
            background-color: #001f3f;  /* темно-синій */
            border-radius: 15px;
        """)

        # 2. Додаємо вертикальний layout для елементів всередині цього віджету
        self.control_panel = QVBoxLayout(self.control_widget)
        self.control_panel.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 3. Створюємо групу керування генерацією
        self.generator_group = QGroupBox("Керування генерацією авто")
        self.generator_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                border: none;
            }
            QLabel {
                color: white;
                font-weight: bold;
                margin-top: 40px;
            }
        """)

        self.generator_layout = QVBoxLayout()

        self.gen_slider = QSlider(Qt.Orientation.Horizontal)
        self.gen_slider.setMinimum(10)
        self.gen_slider.setMaximum(50)
        self.gen_slider.setValue(50)
        self.gen_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.gen_slider.setTickInterval(1)
        self.gen_slider.valueChanged.connect(self.update_gen_speed)

        self.generator_layout.addWidget(QLabel("Частота генерації авто (сек):"))
        self.generator_layout.addWidget(self.gen_slider)

        self.generator_group.setLayout(self.generator_layout)
        self.control_panel.addWidget(self.generator_group)

        # 4. Додаємо прогноз завантаження
        self.forecast_label = QLabel("Прогноз завантаження: Розрахунок…")
        self.forecast_label.setStyleSheet("color: white; font-weight: bold;")
        self.control_panel.addWidget(self.forecast_label)
        self.forecast_timer = QTimer()
        self.forecast_timer.timeout.connect(self.update_forecast)
        self.forecast_timer.start(5000)

    def update_forecast(self):
        forecast_text = get_forecast_text(self.car_generator.gen_sleep)
        self.forecast_label.setText(forecast_text)


    def update_gen_speed(self, value):
        self.car_generator.gen_sleep = value
        self.update_forecast()

    def start_car_animation(self, plate_number, spot_id):
        spot = get_parking_spot_by_id(spot_id)
        car_animation = CarAnimation(self, plate_number, spot)
        car_animation.show()
        car_animation.animate_entry()

    def start_exit_animation(self, plate_number):
        for child in self.findChildren(CarAnimation):
            if child.plate_number == plate_number:
                child.animate_exit()

    def update_parking_status(self):
        # Перезавантажуємо дані з БД (або іншим способом)
        self.spots = get_parking_spots()  # Оновлення паркувальних місць з БД
        self.update()  # Оновлюємо екран (викликає paintEvent)

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Малюємо фон
        painter.setBrush(COLOR_BACKGROUND)
        painter.drawRect(self.rect())

        # Малюємо паркувальні місця
        for spot in self.spots:
            self.draw_parking_spot(painter, spot)

    def draw_parking_spot(self, painter, spot):
        # Вибір кольору в залежності від статусу
        if spot.status == "вільно":
            color = COLOR_FREE
        elif spot.status == "зайнято":
            color = COLOR_OCCUPIED
        else:
            color = COLOR_RESERVED

        # Малюємо паркувальні місця
        if (spot.y1 / 100) % 3 == 1:
            center_x = (spot.x2 + spot.x1) // 2  # Центр кола по X
            center_y = spot.y2 - (spot.y2 - spot.y1) // 10  # Центр кола по Y
            radius = (spot.x2 - spot.x1) // 8  # Радіус кола (половина ширини)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(center_x - radius, center_y - radius, 2 * radius, 2 * radius)
            painter.setPen(QPen(COLOR_BORDER, 2))
            painter.drawEllipse(center_x - radius, center_y - radius, 2 * radius, 2 * radius)
            painter.drawLine(spot.x1, spot.y1, spot.x1, spot.y2)
            painter.drawLine(spot.x2, spot.y1, spot.x2, spot.y2)
            painter.drawLine(spot.x2, spot.y2, spot.x1, spot.y2)
        else:
            center_x = (spot.x2 + spot.x1) // 2
            center_y = spot.y1 + (spot.y2 - spot.y1) // 10
            radius = (spot.x2 - spot.x1) // 8
            painter.setBrush(QBrush(color))
            painter.drawEllipse(center_x - radius, center_y - radius, 2 * radius, 2 * radius)
            painter.setPen(QPen(COLOR_BORDER, 2))
            painter.drawEllipse(center_x - radius, center_y - radius, 2 * radius, 2 * radius)
            painter.drawLine(spot.x1, spot.y1, spot.x1, spot.y2)
            painter.drawLine(spot.x2, spot.y1, spot.x2, spot.y2)
            painter.drawLine(spot.x1, spot.y1, spot.x2, spot.y1)

        # Малюємо текст
        font = QFont("Arial", 12, QFont.Weight.Bold)  # Шрифт Arial, розмір 12, жирний
        painter.setFont(font)
        painter.setPen(QPen(QColor(255, 255, 255)))  # Білий колір для тексту
        # Отримуємо розміри тексту
        text_rect = painter.boundingRect(QRect((spot.x1 + spot.x2) // 2, (spot.y1 + spot.y2) // 2, 0, 0), 0, str(spot.spot_id))


        # Вираховуємо координати для відцентровки
        text_x = (spot.x1 + spot.x2) // 2 - text_rect.width() // 2
        text_y = (spot.y1 + spot.y2) // 2 - text_rect.height() // 2

        # Малюємо текст в обчислених координатах
        painter.drawText(QPoint(text_x, text_y), str(spot.spot_id))

    def mousePressEvent(self, event):
        # Отримуємо координати кліка через pos()
        x = event.position().x()
        y = event.position().y()
        print(x,y)
        # Перевіряємо, яке паркувальне місце було натиснуте
        clicked_spot = get_clicked_spot(x, y, self.spots)
        self.clicked_spot = clicked_spot
        if clicked_spot:
            self.show_popup(clicked_spot, event.globalPosition())

    def show_popup(self, spot, pos):
        # Якщо попап вже відкритий, закриваємо його
        if self.popup:
            self.popup.close()
        
        # Створюємо діалогове вікно для вводу
        self.popup = QDialog(self)
        self.popup.setWindowTitle(f"Інформація про паркувальне місце {spot.spot_id}")
        
        # Створюємо поля для вводу
        layout = QVBoxLayout()

        # Ввід номеру авто
        self.plate_number_input = QLineEdit(self.popup)
        self.plate_number_input.setPlaceholderText("Номер авто")
        layout.addWidget(QLabel("Номер авто:"))
        layout.addWidget(self.plate_number_input)

        # Ввід запланованого часу парковки
        self.parking_time_input = QSpinBox(self.popup)
        self.parking_time_input.setRange(1, 1440)  # Запланований час парковки від 1 до 1440 хвилин (24 години)
        layout.addWidget(QLabel("Запланований час парковки (хвилини):"))
        layout.addWidget(self.parking_time_input)

        # Кнопка для підтвердження
        self.submit_button = QPushButton("Зберегти", self.popup)
        self.submit_button.clicked.connect(self.save_car_info)
        layout.addWidget(self.submit_button)

        # Кнопка для виїзду авто
        self.remove_button = QPushButton("Виїзд", self.popup)
        self.remove_button.clicked.connect(self.remove_car_info)
        layout.addWidget(self.remove_button)

        
        self.popup.setLayout(layout)
        
        # Перетворюємо позицію в QPoint
        point = QPoint(int(pos.x()), int(pos.y()))
        
        # Показуємо попап
        self.popup.exec()

    def save_car_info(self):
        plate_number = self.plate_number_input.text()
        parking_time = self.parking_time_input.value()

        new_car = Car(
            plate_number,
            parking_spot=self.clicked_spot.spot_id,
            arrival_time=int(time.time()),
            departure_time=int(time.time()) + parking_time * 60
        )

        # Запускаємо паркування з анімацією
        new_car.park(
            self.clicked_spot,
            on_created=self.car_generator.car_created.emit  # <- додаємо виклик сигналу
        )
        self.popup.accept()  # Закриваємо попап після збереження

    def remove_car_info(self):

        spot_id = self.clicked_spot.spot_id

        from database import car_update_by_spot
        car_update_by_spot(spot_id)

        self.popup.accept()


    def close_popup(self):
        if self.popup:
            self.popup.close()
            self.popup = None

def main_visual():
    app = QApplication(sys.argv)
    window = ParkingWidget()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main_visual()
