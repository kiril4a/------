from database import update_parking_spot_status
SPOT_WIDTH = 50
SPOT_HEIGHT = 100
class ParkingSpot:
    def __init__(self, spot_id: int, x: int, y: int, status: str = "вільно"):
        """
        Ініціалізація паркувального місця.
        :param spot_id: Унікальний ідентифікатор місця.
        :param x1: Координата X для верхньої лівої точки.
        :param y1: Координата Y для верхньої лівої точки.
        :param status: Статус місця ("вільно", "зайнято", "зарезервовано").
        """
        self.spot_id = spot_id
        self.x1 = x  # Координата X верхньої лівої точки
        self.y1 = y  # Координата Y верхньої лівої точки
        self.x2 = x + SPOT_WIDTH  # Координата X нижньої правої точки (одиниця для простоти)
        self.y2 = y + SPOT_HEIGHT  # Координата Y нижньої правої точки (одиниця для простоти)
        self.status = status

    def contains(self, x, y):
        """Перевіряє, чи точка (x, y) знаходиться всередині паркувального місця."""
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2
    
    def is_free(self) -> bool:
        """Перевіряє, чи місце вільне."""
        return self.status == "вільно"

    def occupy(self):
        """Займає місце (паркує машину)."""
        if self.is_free():
            update_parking_spot_status(self.spot_id,"зайнято")
            self.status = "зайнято"

    def release(self):
        """Звільняє місце."""
        if self.status == "зайнято":
            update_parking_spot_status(self.spot_id,"вільно")
            self.status = "вільно"

    def reserve(self):
        """Резервує місце."""
        update_parking_spot_status(self.spot_id,"зарезервовано")
        self.status = "зарезервовано"

    def __repr__(self):
        return f"ParkingSpot({self.spot_id}, ({self.x1}, {self.y1}), ({self.x2}, {self.y2}), {self.status})"

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
                spot = ParkingSpot(spot_id, x, y)
                spots.append(spot)
                add_parking_spot(spot_id,x,y)
                spot_id += 1
    return spots
