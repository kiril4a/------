from ui.display import main_visual, get_parking_layout
from models.car import start_car_generation
from models.parking_spot import create_parking_layout
from database import create_database
import sqlite3 

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


if __name__ == "__main__":
    setup_parking()
    create_parking_layout()
    start_car_generation()
    #park_car()
    main_visual()