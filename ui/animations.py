from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QPropertyAnimation, QPoint, QSequentialAnimationGroup
from PyQt6.QtGui import QPixmap

def calculate_duration(coord1, coord2, speed=0.5):
    """Розраховує час (duration) для анімації на основі відстані між координатами.
    
    coord1, coord2 — початкова і кінцева координати (X або Y).
    speed — швидкість руху (час у мс на 1 піксель). За замовчуванням 0.5 мс/піксель.
    """
    return int(abs(coord1 - coord2) * speed)
class CarAnimation(QLabel):
    def __init__(self, parent, plate_number, spot):
        super().__init__(parent)
        self.plate_number = plate_number
        self.spot = spot  

        self.setPixmap(QPixmap("image/car.png").scaled(50, 30))
        self.setScaledContents(True)

        # Початкові координати (правий край)
        self.start_x = 1200  
        self.start_y = 612
        self.setGeometry(self.start_x, self.start_y, 50, 30)

        print(f"Створено авто {plate_number} на ({self.start_x}, {self.start_y})")

        # Зберігаємо анімаційні групи
        self.entry_sequence = None
        self.exit_sequence = None

    def get_nearest_parking_line(self, y):
        """Знаходить найближчу точку парковки"""
        parking_lines = [50, 350, 650, 950]
        return min(parking_lines, key=lambda line: abs(line - y))

    def animate_entry(self):
        """Анімує в’їзд авто на паркінг"""
        print(f"Авто {self.plate_number} починає в'їзд")

        self.entry_sequence = QSequentialAnimationGroup()  # Зберігаємо в self
        
        # 0. Рух вліво до X = 1000 перед основним заїздом
        move_left = QPropertyAnimation(self, b"pos")
        move_left.setDuration(calculate_duration(self.start_x, 1000))
        move_left.setStartValue(QPoint(self.start_x, self.start_y))
        move_left.setEndValue(QPoint(1000, self.start_y))

        print(f"Авто {self.plate_number} рухається вліво до X = 1000")

        # 1. Спускаємося або піднімаємося до найближчої Y-лінії
        target_y = self.get_nearest_parking_line((self.spot.y1 + self.spot.y2)//2)
        move_y = QPropertyAnimation(self, b"pos")
        move_y.setDuration(calculate_duration(self.start_y, target_y))
        move_y.setStartValue(QPoint(1000, self.start_y))
        move_y.setEndValue(QPoint(1000, target_y))

        print(f"Авто {self.plate_number} рухається до Y = {target_y}")

        # 2. Рухаємося вліво до парковки
        move_x = QPropertyAnimation(self, b"pos")
        move_x.setDuration(calculate_duration(1000, self.spot.x1))
        move_x.setStartValue(QPoint(1000, target_y))
        move_x.setEndValue(QPoint(self.spot.x1, target_y))

        print(f"Авто {self.plate_number} рухається по X до {self.spot.x1}")

        # 3. Останній рух: заїзд вгору або вниз на місце
        move_park = QPropertyAnimation(self, b"pos")
        move_park.setDuration(calculate_duration(target_y, (self.spot.y1+self.spot.y2)//2))
        move_park.setStartValue(QPoint(self.spot.x1, target_y))
        move_park.setEndValue(QPoint(self.spot.x1, (self.spot.y1+self.spot.y2)//2))

        print(f"Авто {self.plate_number} паркується на ({self.spot.x1}, {self.spot.y1})")

        self.entry_sequence.addAnimation(move_left)
        self.entry_sequence.addAnimation(move_y)
        self.entry_sequence.addAnimation(move_x)
        self.entry_sequence.addAnimation(move_park)

        self.entry_sequence.start()  # ОБОВ'ЯЗКОВО запускаємо!
    
    def animate_exit(self):
        """Анімація виїзду авто"""
        print(f"Авто {self.plate_number} починає виїзд")

        self.exit_sequence = QSequentialAnimationGroup()  # Зберігаємо в self

        # 1. Виїзд на найближчу Y-лінію
        nearest_y = self.get_nearest_parking_line((self.spot.y1+self.spot.y2)//2)
        move_y = QPropertyAnimation(self, b"pos")
        move_y.setDuration(calculate_duration((self.spot.y1+self.spot.y2)//2, nearest_y))
        move_y.setStartValue(QPoint(self.spot.x1,(self.spot.y1+self.spot.y2)//2))
        move_y.setEndValue(QPoint(self.spot.x1, nearest_y))

        print(f"Авто {self.plate_number} рухається до Y = {nearest_y}")

        # 2. Рух ліворуч за межі екрану
        move_x = QPropertyAnimation(self, b"pos")
        move_x.setDuration(calculate_duration(self.spot.x1, -100))
        move_x.setStartValue(QPoint(self.spot.x1, nearest_y))
        move_x.setEndValue(QPoint(-100, nearest_y))

        print(f"Авто {self.plate_number} виїжджає за межі ({1300}, {nearest_y})")

        self.exit_sequence.addAnimation(move_y)
        self.exit_sequence.addAnimation(move_x)

        # Видаляємо авто після завершення виїзду
        self.exit_sequence.finished.connect(self.deleteLater)

        self.exit_sequence.start()  # ОБОВ'ЯЗКОВО запускаємо!
