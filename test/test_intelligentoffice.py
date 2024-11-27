import unittest
from datetime import datetime
from unittest.mock import patch, Mock, PropertyMock
import mock.GPIO as GPIO
from mock.SDL_DS3231 import SDL_DS3231
from mock.adafruit_veml7700 import VEML7700
from src.intelligentoffice import IntelligentOffice, IntelligentOfficeError


class TestIntelligentOffice(unittest.TestCase):

    @patch.object(GPIO, "input")
    def test_check_quadrant_occupancy(self, infrared_sensor_quadrant_1: Mock):
        infrared_sensor_quadrant_1.return_value = True
        intelligent_office = IntelligentOffice()

        is_occupied = intelligent_office.check_quadrant_occupancy(intelligent_office.INFRARED_PIN1)
        infrared_sensor_quadrant_1.assert_called_once_with(intelligent_office.INFRARED_PIN1)
        self.assertTrue(is_occupied)