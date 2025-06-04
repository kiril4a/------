# database.py
import sqlite3
import random
import time
def create_database(db_name: str = "parking.db"):
    """Створює базу даних і таблицю для паркувальних місць"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_spots (
            spot_id INTEGER PRIMARY KEY,
            x1 INTEGER,
            y1 INTEGER,
            x2 INTEGER,
            y2 INTEGER,
            status TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            plate_number TEXT PRIMARY KEY,
            spot_id INTEGER,
            arrival_time INTEGER,
            departure_time INTEGER NULL,
            FOREIGN KEY (spot_id) REFERENCES parking_spots(spot_id)
        )
    ''')
    conn.commit()
    conn.close()

def add_parking_spot(spot_id: int, x: int, y: int, status: str = "вільно", db_name: str = "parking.db"):
    from models.parking_spot import SPOT_HEIGHT,SPOT_WIDTH
    """Додає нове паркувальне місце в базу даних"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO parking_spots (x1, y1, x2, y2, status) 
        VALUES (?, ?, ?, ?, ?)
    ''', (x, y, x + SPOT_WIDTH, y + SPOT_HEIGHT, status))


    conn.commit()
    conn.close()

def get_parking_spots(db_name: str = "parking.db"):
    from models.parking_spot import ParkingSpot
    """Отримує всі паркувальні місця з бази даних"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM parking_spots")
    spots_data = cursor.fetchall()
    
    spots = []
    for spot_data in spots_data:
        spot = ParkingSpot(spot_data[0], spot_data[1], spot_data[2], spot_data[5])
        spots.append(spot)

    conn.close()
    return spots

def get_parking_spot_by_id(spot_id, db_name="parking.db"):
    from models.parking_spot import ParkingSpot
    """Отримує паркувальне місце з БД за ID."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT spot_id, x1, y1, status FROM parking_spots WHERE spot_id = ?", (spot_id,))
    data = cursor.fetchone()
    conn.close()

    if data:
        return ParkingSpot(*data)  # Повертаємо об'єкт ParkingSpot
    return None

def get_parking_spot_status_by_id(spot_id: int, db_name="parking.db") -> str:
    # Повертає статус ("вільно", "зайнято", "зарезервовано")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM parking_spots WHERE spot_id = ?", (spot_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "вільно"

def update_parking_spot_status(spot_id: int, new_status: str, db_name: str = "parking.db"):
    """Оновлює статус паркувального місця в базі даних"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE parking_spots 
        SET status = ?
        WHERE spot_id = ?
    ''', (new_status, spot_id))
    conn.commit()
    conn.close()

def add_car(plate_number: str, spot_id: int, db_name: str = "parking.db"):
    """Додає автомобіль до БД при паркуванні."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO cars (plate_number, spot_id) VALUES (?, ?)''',
        (plate_number, spot_id)
    )
    cursor.execute(
        '''UPDATE parking_spots SET status = 'зайнято' WHERE spot_id = ?''',
        (spot_id)
    )
    conn.commit()
    conn.close()

def get_all_cars(db_name: str = "parking.db"):
    from models.car import Car
    """Отримує всі автомобілі з бази даних."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT plate_number, spot_id, arrival_time, departure_time FROM cars")
    cars_data = cursor.fetchall()
    cars = []
    for car_data in cars_data:
        car = Car(car_data[0], car_data[1], car_data[2], car_data[3])
        cars.append(car)
    conn.close()
    return cars  # Список кортежів (номер авто, місце, час прибуття)

def car_exists(plate_number, db_name="parking.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cars WHERE plate_number = ?", (plate_number,))
    exists = cursor.fetchone()[0] > 0
    conn.close()
    return exists

def add_car_to_db(plate_number, spot_id, arrival_time, departure_time=None, db_name="parking.db"):
    """Додає автомобіль у базу даних при паркуванні."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    if departure_time is None:
        # Якщо departure_time не вказано, його обчислюємо тут
        departure_time = arrival_time + random.randint(30, 300)  # Розраховуємо час виїзду

    cursor.execute('''
        INSERT INTO cars (plate_number, spot_id, arrival_time, departure_time) 
        VALUES (?, ?, ?, ?)
    ''', (plate_number, spot_id, arrival_time, departure_time))

    conn.commit()
    conn.close()

def remove_car_from_db(plate_number, db_name="parking.db"):
    """Позначає автомобіль як такий, що виїхав."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM cars 
        WHERE plate_number = ?
    ''', (plate_number,))
    
    conn.commit()
    conn.close()

def car_update_by_spot(spot_id):
    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    now = int(time.time())
    print("------------------------------here")
    cursor.execute("""
        UPDATE cars
        SET departure_time = ?
        WHERE spot_id = ?
    """, (now, spot_id))

    conn.commit()
    conn.close()
