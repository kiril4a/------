import unittest
from unittest.mock import patch, MagicMock
from models.car import Car
from models.parking_spot import ParkingSpot

class TestCar(unittest.TestCase):

    @patch("models.car.add_car_to_db")
    @patch("models.car.car_exists", return_value=False)
    def test_park_car_success(self, mock_exists, mock_add):
        spot = ParkingSpot(spot_id=1, x=0, y=0, status="вільно")
        car = Car("AA1234BB")
        
        with patch.object(spot, "is_free", return_value=True), \
             patch.object(spot, "occupy") as mock_occupy:
            car.park(spot)
            self.assertEqual(car.parking_spot, spot)
            self.assertIsNotNone(car.arrival_time)
            self.assertIsNotNone(car.departure_time)
            mock_add.assert_called_once()

    @patch("models.car.remove_car_from_db")
    @patch("models.car.get_parking_spot_by_id")
    def test_leave_car_success(self, mock_get_spot, mock_remove):
        spot = ParkingSpot(1, 0, 0, "зайнято")
        car = Car("AA1234BB", parking_spot=spot)
        mock_get_spot.return_value = spot
        
        with patch.object(spot, "release") as mock_release:
            car.leave()
            self.assertIsNone(car.parking_spot)
            mock_release.assert_called_once()
            mock_remove.assert_called_once_with("AA1234BB")

if __name__ == '__main__':
    unittest.main()
