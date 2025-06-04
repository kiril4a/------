from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QPropertyAnimation, QPoint, QSequentialAnimationGroup, Qt, QVariantAnimation, QPauseAnimation, QTimer, QAbstractAnimation
from PyQt6.QtGui import QPixmap, QTransform, QPainter
import math
radius = 45
step_rotation = 5
def calculate_duration(coord1, coord2, speed=2):
    """Розраховує час (duration) для анімації на основі відстані між координатами.
    
    coord1, coord2 — початкова і кінцева координати (X або Y).
    speed — швидкість руху (час у мс на 1 піксель). За замовчуванням 0.5 мс/піксель.
    """
    return int(abs(coord1 - coord2) * speed)

def rotate_point(center, point, angle):
    """
    Повертає координати точки після повороту навколо центру на заданий кут.
    
    :param center: (x0, y0) - координати центру кола
    :param point: (x, y) - координати початкової точки
    :param angle: float - кут повороту в градусах (за годинниковою стрілкою)
    :return: (x', y') - нові координати точки після повороту
    """
    # Перетворення градусів у радіани
    radians = math.radians(angle)
    
    # Отримання координат
    x0, y0 = center
    x, y = point
    
    # Формули повороту
    x_new = x0 + (x - x0) * math.cos(radians) - (y - y0) * math.sin(radians)
    y_new = y0 + (x - x0) * math.sin(radians) + (y - y0) * math.cos(radians)
    
    return x_new, y_new

def distance(point1, point2):
    """
    Визначає відстань між двома точками.
    
    :param point1: (x1, y1) - координати першої точки
    :param point2: (x2, y2) - координати другої точки
    :return: float - відстань між точками
    """
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
class CarAnimation(QLabel):
    def __init__(self, parent, plate_number, spot):
        super().__init__(parent)
        self.plate_number = plate_number
        self.spot = spot  
        self.current_angle = 0
        self.original_pixmap = QPixmap("image/car.png").scaled(80, 45)
        self.setPixmap(self.original_pixmap)
        self.setScaledContents(True)

        # Початкові координати (правий край)
        self.start_x = 1300  
        self.start_y = 490
        self.setGeometry(self.start_x, self.start_y, 80, 45)

        #print(f"Створено авто {plate_number} на ({self.start_x}, {self.start_y})")

        # Зберігаємо анімаційні групи
        self.entry_sequence = None
        self.exit_sequence = None

    def get_nearest_parking_line(self, y):
        """Знаходить найближчу точку парковки"""
        parking_lines = [70, 370, 670, 970]
        return min(parking_lines, key=lambda line: abs(line - y))
    
    def move(self, x, y):
        ##print(f"Перед переміщенням: x = {self.x()}, y = {self.y()}")
        super().move(x, y)
        ##print(f"Після переміщення: x = {self.x()}, y = {self.y()}")
    # Викликаємо move() від QLabel без рекурсії


    def rotate(self, target_angle, callback=None):
        """
        Плавно повертає автомобіль навколо заданого радіусу.
        
        :param target_angle: Кут, на який треба повернути (+90 або -90 градусів).
        :param radius: Радіус повороту.
        :param callback: Функція, яка викличеться після завершення повороту.
        """
        angle_direction = 1 if target_angle > self.current_angle else -1
        
        # 1. Обчислюємо центр обертання
        center_x = self.x() + self.width() // 2
        center_y = self.y() - radius if angle_direction == 1 else self.y() + radius + self.height()
        center = (center_x, center_y)

        
        ##print(f"Центр обертання: {center}")
        ##print(self.x(), self.width())
        rotate_point((self.x(),self.y()),center,-90)
        def step():
            nonlocal center

            if abs(self.current_angle - target_angle) < step_rotation:
                self.current_angle = target_angle
            else:
                self.current_angle += step_rotation * angle_direction

            # 2. Обчислюємо нові координати центру автомобіля
            figure_center_x = self.x() + self.width() // 2
            figure_center_y = self.y() + self.height() // 2
            figure_center = (figure_center_x, figure_center_y)
            ##print(figure_center, "figure")
            new_figure_center = rotate_point(center, figure_center, step_rotation * angle_direction)

            # 3. Повертаємо зображення без зміни його розміру
            transform = QTransform()
            transform.rotate(self.current_angle)
            rotated_pixmap = self.original_pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)

            # Отримуємо нові розміри рамки (bounding box)
            new_rect = rotated_pixmap.rect()
            new_width = new_rect.width()
            new_height = new_rect.height()

            # 4. Обчислюємо новий верхній лівий кут
            new_x = new_figure_center[0] - new_width // 2
            new_y = new_figure_center[1] - new_height // 2
            ##print(new_x, new_y)

            # 5. Оновлюємо рамку та переміщуємо авто
            self.setPixmap(rotated_pixmap)
            self.setGeometry(int(new_x), int(new_y), new_width, new_height)

            # Перевіряємо, чи завершився поворот
            if self.current_angle == target_angle:
                if callback:
                    callback()
                return

            QTimer.singleShot(calculate_duration(0, distance(new_figure_center, figure_center)), step)

        step()

    def rotate2(self, target_angle, callback=None):
        angle_direction = 1 if target_angle > self.current_angle else -1

        if angle_direction == 1:  # рух вниз
            center_x = self.x() - radius
            center_y = self.y() + self.height() // 2
        else:  # рух вгору
            center_x = self.x() - radius
            center_y = self.y() + self.height() // 2

        center = (center_x, center_y)

        def step():
            nonlocal center

            if abs(self.current_angle - target_angle) < step_rotation:
                self.current_angle = target_angle
            else:
                self.current_angle += step_rotation * angle_direction

            figure_center_x = self.x() + self.width() // 2
            figure_center_y = self.y() + self.height() // 2
            figure_center = (figure_center_x, figure_center_y)
            new_figure_center = rotate_point(center, figure_center, step_rotation * angle_direction)

            transform = QTransform()
            transform.rotate(self.current_angle)
            rotated_pixmap = self.original_pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)

            new_rect = rotated_pixmap.rect()
            new_width = new_rect.width()
            new_height = new_rect.height()

            new_x = new_figure_center[0] - new_width // 2
            new_y = new_figure_center[1] - new_height // 2

            self.setPixmap(rotated_pixmap)
            self.setGeometry(int(new_x), int(new_y), new_width, new_height)

            if self.current_angle == target_angle:
                if callback:
                    callback()
                return

            QTimer.singleShot(calculate_duration(0, distance(new_figure_center, figure_center)), step)

        step()





    def animate_entry(self):
        """Анімує в’їзд авто на паркінг"""
        #print(f"Авто {self.plate_number} починає в'їзд")

        self.entry_sequence = QSequentialAnimationGroup()  # Зберігаємо в self

        # 0. Рух вліво до X = 1000 перед основним заїздом
        move_left = QPropertyAnimation(self, b"pos")
        move_left.setDuration(calculate_duration(self.start_x, 1000))
        move_left.setStartValue(QPoint(self.start_x, self.start_y))
        move_left.setEndValue(QPoint(1000, self.start_y))

        # Пауза перед першим поворотом
        #pause_before_rotate1 = QPauseAnimation(100)
        
        # Перший поворот (правильний варіант)
        rotate_animation = QPauseAnimation(1)
        #rotate_animation.setDuration(calculate_duration(0, 90)+1000)
        rotate_angle = 90 if self.get_nearest_parking_line((self.spot.y1 + self.spot.y2) // 2) < self.start_y else -90
        rotate_animation.finished.connect(lambda: self.rotate(rotate_angle))

        pause_before_rotate1 = QPauseAnimation(calculate_duration(0,2*3.14*radius//4)*2)
        # 1. Спускаємося або піднімаємося до найближчої Y-лінії
        target_y = self.get_nearest_parking_line((self.spot.y1 + self.spot.y2)//2)
        move_y = QPropertyAnimation(self, b"pos")
        X=950
        if target_y > self.y():
            move_y.setDuration(calculate_duration(self.start_y - self.width() - self.height(), target_y - self.height() - self.width()))
            move_y.setStartValue(QPoint(935, 540))
            move_y.setEndValue(QPoint(935, target_y - self.height() - self.width()))
            X = 935
        else:
            move_y.setDuration(calculate_duration(self.start_y - radius - self.height(), target_y))
            move_y.setStartValue(QPoint(950, 395))
            move_y.setEndValue(QPoint(950, target_y))
            X = 950
        
        #print(f"Авто {self.plate_number} рухається до Y = {target_y}")

        # Другий поворот
        rotate_animation_second = QPauseAnimation(1)
        rotate_angle_2 = 1 if self.get_nearest_parking_line((self.spot.y1 + self.spot.y2)//2) < (self.start_y) else -1
        rotate_animation_second.finished.connect(lambda: self.rotate2(rotate_angle_2))

        pause_before_rotate2 = QPauseAnimation(calculate_duration(0,2*3.14*radius//4)*2)

        # 2. Рухаємося вліво до парковки
        move_x = QPropertyAnimation(self, b"pos")
        move_x.setDuration(calculate_duration(850, self.spot.x1))
        #if rotate_angle_2 == 1:
        move_x.setStartValue(QPoint(850, target_y - self.height()))
        move_x.setEndValue(QPoint(self.spot.x1 + self.width()//2 + 20, target_y - self.height()))

        #print(f"Авто {self.plate_number} рухається по X до {self.spot.x1}")

        # Третій поворот (використовує rotate)
        rotate_animation_vertical = QPauseAnimation(1)
        # Якщо парковка вище поточної позиції — повертаємо вгору (-90), інакше — вниз (90)
        final_rotation_angle = 90 if (self.spot.y1 + self.spot.y2) // 2 < target_y else -90
        rotate_animation_vertical.finished.connect(lambda: self.rotate(final_rotation_angle))

        # Пауза перед третім поворотом
        pause_before_rotate3 = QPauseAnimation(calculate_duration(0, 2 * math.pi * radius // 4) * 2)

        # 3. Останній рух: заїзд вгору або вниз на місце
        move_park = QPropertyAnimation(self, b"pos")
        
        if (self.spot.y1 + self.spot.y2) // 2 < target_y:
            move_park.setDuration(calculate_duration(target_y, (self.spot.y1 + self.spot.y2) // 2 - self.height() // 2))
            move_park.setStartValue(QPoint(self.spot.x1, target_y - self.height()*3))
            move_park.setEndValue(QPoint(self.spot.x1, (self.spot.y1 + self.spot.y2) // 2 - self.height() // 2))
        else:
            move_park.setDuration(calculate_duration(target_y + self.height() , (self.spot.y1 + self.spot.y2) // 2 - self.height() // 2 - 30))
            move_park.setStartValue(QPoint(self.spot.x1, target_y + self.height() - 20))
            move_park.setEndValue(QPoint(self.spot.x1, (self.spot.y1 + self.spot.y2) // 2 - self.height() // 2 - 30))

        #print(f"Авто {self.plate_number} паркується на ({self.spot.x1}, {self.spot.y1})")

        # Додаємо всі анімації по порядку
        self.entry_sequence.addAnimation(move_left)
        self.entry_sequence.addAnimation(rotate_animation)
        self.entry_sequence.addAnimation(pause_before_rotate1)
        self.entry_sequence.addAnimation(move_y)
        self.entry_sequence.addAnimation(rotate_animation_second)
        self.entry_sequence.addAnimation(pause_before_rotate2)
        self.entry_sequence.addAnimation(move_x)
        self.entry_sequence.addAnimation(rotate_animation_vertical)
        self.entry_sequence.addAnimation(pause_before_rotate3)
        self.entry_sequence.addAnimation(move_park)

        self.entry_sequence.start()  # ОБОВ'ЯЗКОВО запускаємо!

    
    def animate_exit(self):
        """Анімація виїзду авто"""
        #print(f"Авто {self.plate_number} починає виїзд")

        self.exit_sequence = QSequentialAnimationGroup()  # Зберігаємо в self

        # 0. Поворот перед виїздом (обернений до логіки в’їзду)
        rotate_animation_second = QPauseAnimation(1)
        current_y = (self.spot.y1 + self.spot.y2) // 2
        nearest_y = self.get_nearest_parking_line(current_y)

        # Якщо середина знаходиться ближче до верхньої межі — повертаємо ліворуч (-1), інакше — праворуч (+1)
        rotate_angle_2 = self.current_angle - 90 if nearest_y < current_y else self.current_angle + 90
        rotate_animation_second.finished.connect(lambda: self.rotate2(rotate_angle_2))

        pause_before_rotate2 = QPauseAnimation(calculate_duration(0, 2 * math.pi * radius // 4) * 2)


        # 2. Рух ліворуч за межі екрану
        move_x = QPropertyAnimation(self, b"pos")
        rotate_angle_3 = 1 if nearest_y < current_y else -1
        if rotate_angle_3 == 1:
            move_x.setDuration(calculate_duration(self.spot.x1 - self.width() - 40, -100))
            move_x.setStartValue(QPoint(self.spot.x1 - self.width() - 40, self.spot.y1 - self.width() - 10))
            move_x.setEndValue(QPoint(-100, self.spot.y1 - self.width() - 10))
        else:
            move_x.setDuration(calculate_duration(self.spot.x1 - self.width() - 40, -100))
            move_x.setStartValue(QPoint(self.spot.x1 - self.width() - 40, self.spot.y1 + self.width() + self.height() - 30))
            move_x.setEndValue(QPoint(-100, self.spot.y1 + self.width() + self.height() - 30))


        #print(f"Авто {self.plate_number} виїжджає за межі ({-100}, {nearest_y})")

        self.exit_sequence.addAnimation(rotate_animation_second)
        self.exit_sequence.addAnimation(pause_before_rotate2)
        self.exit_sequence.addAnimation(move_x)

        self.exit_sequence.finished.connect(self.deleteLater)
        self.exit_sequence.start()

