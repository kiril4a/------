import unittest
from unittest.mock import patch
from models.parking_spot import ParkingSpot

class TestParkingSpot(unittest.TestCase):

    def setUp(self):
        self.spot = ParkingSpot(1, 0, 0, "вільно")

    @patch("models.parking_spot.get_parking_spot_status_by_id", return_value="вільно")
    def test_is_free(self, mock_status):
        self.assertTrue(self.spot.is_free())

    @patch("models.parking_spot.get_parking_spot_status_by_id", return_value="вільно")
    @patch("models.parking_spot.update_parking_spot_status")
    def test_occupy_spot(self, mock_update, mock_status):
        self.spot.occupy()
        self.assertEqual(self.spot.status, "зайнято")
        mock_update.assert_called_once_with(1, "зайнято")

    @patch("models.parking_spot.get_parking_spot_status_by_id", return_value="зайнято")
    @patch("models.parking_spot.update_parking_spot_status")
    def test_release_spot(self, mock_update, mock_status):
        self.spot.release()
        self.assertEqual(self.spot.status, "вільно")
        mock_update.assert_called_once_with(1, "вільно")

if __name__ == '__main__':
    unittest.main()
