import unittest
from models.gate import Gate
from models.parking_spot import ParkingSpot

class TestGate(unittest.TestCase):

    def test_admit_car_success(self):
        gate = Gate(0, 0)
        spot = ParkingSpot(1, 0, 0, "вільно")
        spot.is_free = lambda: True  # "заморозка" статусу
        spot.occupy = lambda: None   # глушимо зміну статусу

        car = gate.admit_car("AA9999BB", [spot])
        self.assertIsNotNone(car)
        self.assertEqual(car.parking_spot, spot)
        self.assertEqual(car.plate_number, "AA9999BB")

    def test_admit_car_no_free_spots(self):
        gate = Gate(0, 0)
        spot = ParkingSpot(1, 0, 0, "зайнято")
        spot.is_free = lambda: False

        car = gate.admit_car("BB8888CC", [spot])
        self.assertIsNone(car)

if __name__ == '__main__':
    unittest.main()
