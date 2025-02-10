from PyQt6.QtCore import QObject, pyqtSignal
import random
import time
import threading
from database import get_all_cars, get_parking_spot_by_id, car_exists, add_car_to_db, remove_car_from_db, get_parking_spots
from models.parking_spot import ParkingSpot
GEN_SLEEP = 1
MAX_TIME_PARK = 40
class Car:
    def __init__(self, plate_number: str, parking_spot: int = None, arrival_time: int = None, departure_time: int = None):
        self.plate_number = plate_number
        self.parking_spot = parking_spot
        self.arrival_time = arrival_time
        self.departure_time = departure_time

    def park(self, spot: ParkingSpot):
        """Паркує авто на місце та зберігає в БД."""
        if not car_exists(self.plate_number):
            if spot.is_free():
                self.parking_spot = spot
                self.arrival_time = int(time.time())
                spot.occupy()
                self.departure_time = self.arrival_time + random.randint(10, MAX_TIME_PARK)
                add_car_to_db(self.plate_number, spot.spot_id, self.arrival_time, self.departure_time)

    def leave(self):
        """Виїжджає з паркувального місця та оновлює БД."""
        #self.departure_time = time.time()
        spot = get_parking_spot_by_id(self.parking_spot)
        spot.release()
        remove_car_from_db(self.plate_number)
        self.parking_spot = None
    
    def __repr__(self):
        return f"Car(plate_number='{self.plate_number}', parking_spot={self.parking_spot}, arrival_time={self.arrival_time}, departure_time={self.departure_time})"

class CarGenerator(QObject):
    car_created = pyqtSignal(str, int)  # Передаємо номер авто і паркомісце
    car_leaving = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def generate_car(self, car_id):
        """Генерує авто, паркує та надсилає сигнал для анімації."""
        plate_number = f"ABC{car_id:03d}"
        car = Car(plate_number)
        spots = get_parking_spots()

        for spot in spots:
            if spot.is_free():
                car.park(spot)
                print(f"Авто {plate_number} припарковане на місці {spot.spot_id}")
                
                # Надсилаємо сигнал для запуску анімації
                self.car_created.emit(plate_number, spot.spot_id)
                break

    def car_generator(self):
        """Цикл генерації авто."""
        car_id = 1
        while True:
            self.generate_car(car_id)
            car_id += 1
            time.sleep(GEN_SLEEP)

    def start_car_generation(self):
        """Запуск генерації авто в окремому потоці."""
        generator_thread = threading.Thread(target=self.car_generator, daemon=True)
        exit_thread = threading.Thread(target=self.process_parked_cars, daemon=True)
        
        exit_thread.start()
        generator_thread.start()

    def process_parked_cars(self):
        """Постійно перевіряє всі автомобілі в БД та виїжджає ті, у яких минув час паркування."""
        while True:
            cars = get_all_cars()
            current_time = int(time.time()) 
            for car in cars:
                if car.departure_time and current_time >= car.departure_time:
                    print(f"Авто {car.plate_number} виїжджає з місця {car.parking_spot}")
                    self.car_leaving.emit(car.plate_number)

                    # Даємо час для анімації
                    time.sleep(3)
                    car.leave()  # Видаляємо авто з БД
                    
            time.sleep(1)  # Перевіряємо кожні 5 секунд