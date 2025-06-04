from ui.display import main_visual, get_parking_layout,ParkingWidget
from models.car import CarGenerator  # Імпортуємо клас, а не функцію
from models.parking_spot import create_parking_layout
from database import create_database
import sqlite3 
import sys
from PyQt6.QtWidgets import QApplication 

DATABASE = 'parking.db'

rows, cols = get_parking_layout()

def clear_parking_spots():
    """Очищає таблицю паркувальних місць в базі даних"""
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    
    cursor.execute("DELETE FROM parking_spots")
    cursor.execute("DELETE FROM cars")
    connection.commit()
    connection.close()
    print("База даних паркувальних місць очищена.")

def setup_parking():
    create_database()
    clear_parking_spots()

def generation():
    app = QApplication(sys.argv)

    # Створюємо генератор машин
    car_generator = CarGenerator()

    # Передаємо генератор у ParkingWidget
    parking_widget = ParkingWidget(car_generator)
    parking_widget.show()

    car_generator.start_car_generation()  # Запускаємо генерацію машин

    sys.exit(app.exec())
if __name__ == "__main__":
    setup_parking()
    create_parking_layout()
    generation()
    main_visual()
