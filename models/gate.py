from models.car import Car

class Gate:
    def __init__(self, entry_x: int, entry_y: int):
        """
        В’їзні ворота для додавання машин.
        :param entry_x: Координата X в’їзду.
        :param entry_y: Координата Y в’їзду.
        """
        self.entry_x = entry_x
        self.entry_y = entry_y

    def admit_car(self, plate_number: str, parking_spots: list):
        """Приймає машину і намагається знайти їй місце."""
        car = Car(plate_number, self.entry_x, self.entry_y)
        for spot in parking_spots:
            if spot.is_free():
                car.park(spot)
                return car
        return None  # Якщо немає місць
