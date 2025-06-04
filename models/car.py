from PyQt6.QtCore import QObject, pyqtSignal
import random
import time
import threading
from database import get_all_cars, get_parking_spot_by_id, car_exists, add_car_to_db, remove_car_from_db, get_parking_spots
from models.parking_spot import ParkingSpot
from config import GEN_SLEEP
MAX_TIME_PARK = 120
class Car:
    def __init__(self, plate_number: str, parking_spot=None, arrival_time=None, departure_time=None):
        self.plate_number = plate_number
        self.parking_spot = parking_spot  # має бути об'єктом ParkingSpot
        self.arrival_time = arrival_time
        self.departure_time = departure_time

    def park(self, spot, on_created=None):
        if not car_exists(self.plate_number):
            with spot.lock:
                if spot.is_free():
                    self.parking_spot = spot
                    self.arrival_time = int(time.time())
                    spot.occupy()
                    self.departure_time = self.arrival_time + random.randint(10, MAX_TIME_PARK)
                    add_car_to_db(self.plate_number, spot.spot_id, self.arrival_time, self.departure_time)

                    if on_created:
                        on_created(self.plate_number, spot.spot_id)

    def leave(self):
        spot = get_parking_spot_by_id(self.parking_spot)
        if spot:
            with spot.lock:
                spot.release()
        remove_car_from_db(self.plate_number)
        self.parking_spot = None

    def __repr__(self):
        return f"Car({self.plate_number}, spot_id={self.parking_spot.spot_id if self.parking_spot else None}, arrival={self.arrival_time}, departure={self.departure_time})"

class CarGenerator(QObject):
    car_created = pyqtSignal(str, int)  # Передаємо номер авто і паркомісце
    car_leaving = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.gen_sleep = 50

    def generate_car(self, car_id):
        plate_number = f"ABC{car_id:03d}"
        car = Car(plate_number)
        spots = get_parking_spots()

        for spot in spots:
            with spot.lock:  # захищаємо всю перевірку + паркування
                if spot.is_free():
                    car.park(spot)
                    self.car_created.emit(plate_number, spot.spot_id)
                    break


    def car_generator(self):
        car_id = 1
        while True:
            self.generate_car(car_id)
            car_id += 1
            time.sleep(self.gen_sleep / 10)

    def start_car_generation(self):
        generator_thread = threading.Thread(target=self.car_generator, daemon=True)
        exit_thread = threading.Thread(target=self.process_parked_cars, daemon=True)
        generator_thread.start()
        exit_thread.start()

    def process_car_exit(self, car):
        self.car_leaving.emit(car.plate_number)
        #time.sleep(3)
        car.leave()

    def process_parked_cars(self):
        while True:
            cars = get_all_cars()
            current_time = int(time.time())
            for car in cars:
                if car.departure_time and current_time >= car.departure_time:
                    self.process_car_exit(car)  # ⬅ без потоку
            #time.sleep(1)


