from database import update_parking_spot_status, get_parking_spot_status_by_id
SPOT_WIDTH = 50
SPOT_HEIGHT = 100
from threading import RLock

class ParkingSpot:
    def __init__(self, spot_id: int, x: int, y: int, status: str):
        self.spot_id = spot_id
        self.x1 = x
        self.y1 = y
        self.x2 = x + SPOT_WIDTH
        self.y2 = y + SPOT_HEIGHT
        self.status = status
        self.lock = RLock()  # Захищаємо критичні секції

    def contains(self, x, y):
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    def get_status(self) -> str:
        return get_parking_spot_status_by_id(self.spot_id)

    def is_free(self) -> bool:
        return self.get_status() == "вільно"

    def occupy(self):
        with self.lock:
            if self.is_free():
                self.status = "зайнято"
                update_parking_spot_status(self.spot_id, "зайнято")

    def release(self):
        with self.lock:
            if self.get_status() == "зайнято":
                self.status = "вільно"
                update_parking_spot_status(self.spot_id, "вільно")

    def reserve(self):
        with self.lock:
            if self.get_status() == "вільно":
                update_parking_spot_status(self.spot_id, "зарезервовано")

    def __repr__(self):
        return f"ParkingSpot({self.spot_id}, ({self.x1}, {self.y1}), ({self.x2}, {self.y2}), status={self.get_status()})"


def create_parking_layout():
    from database import add_parking_spot
    from ui.display import get_parking_layout
    """Створює список об'єктів ParkingSpot для всіх паркувальних місць."""
    spots = []
    rows, cols = get_parking_layout()
    print(rows, cols)
    spot_id = 1
    for row in range(rows*2):
        for col in range(cols):
            if row % 3:
                x = col * SPOT_WIDTH
                y = row * SPOT_HEIGHT
                spot = ParkingSpot(spot_id, x, y, "вільно")
                spots.append(spot)
                add_parking_spot(spot_id,x,y)
                spot_id += 1
    return spots
