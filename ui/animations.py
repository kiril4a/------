from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, QPointF
from PyQt6.QtGui import QPixmap

class CarAnimation(QLabel):
    def __init__(self, parent, car, gate_x, gate_y, parking_x, parking_y):
        super().__init__(parent)
        self.car = car
        self.setPixmap(QPixmap("images/car.png").scaled(50, 30))  # Масштабуємо авто
        self.setScaledContents(True)
        
        self.gate_x, self.gate_y = gate_x, gate_y  # Координати воріт
        self.parking_x, self.parking_y = parking_x, parking_y  # Координати місця
        
        self.x, self.y = -100, gate_y  # Початкова позиція за межами екрану
        self.setGeometry(self.x, self.y, 50, 30)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_car)
        self.timer.start(30)  # Частота оновлення анімації
    
    def move_car(self):
        if self.x < self.gate_x:  # Рух до воріт
            self.x += 5
        elif self.y != self.parking_y:  # Поворот вгору/вниз до ряду
            self.y += 5 if self.parking_y > self.gate_y else -5
        elif self.x != self.parking_x:  # Рух до місця
            self.x += 5 if self.parking_x > self.gate_x else -5
        else:  # Запаркувались
            self.timer.stop()
            return
        
        self.move(self.x, self.y)
