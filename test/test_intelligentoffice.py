import unittest
from datetime import datetime
from unittest.mock import patch, Mock, PropertyMock
import mock.GPIO as GPIO
from mock.SDL_DS3231 import SDL_DS3231
from mock.adafruit_veml7700 import VEML7700
from src.intelligentoffice import IntelligentOffice, IntelligentOfficeError


class TestIntelligentOffice(unittest.TestCase):

    @patch.object(GPIO, "input")
    def test_check_quadrant_occupancy_occupied(self, infrared_sensor_mock: Mock):
        infrared_sensor_mock.return_value = True
        intelligent_office = IntelligentOffice()

        infrared_pins = [intelligent_office.INFRARED_PIN1 ,intelligent_office.INFRARED_PIN2 ,intelligent_office.INFRARED_PIN3, intelligent_office.INFRARED_PIN4]
        for infrared_pin in infrared_pins:
            is_occupied = intelligent_office.check_quadrant_occupancy(infrared_pin)
            infrared_sensor_mock.assert_called_with(infrared_pin)
            self.assertTrue(is_occupied)

    @patch.object(GPIO, "input")
    def test_check_quadrant_occupancy_free(self, infrared_sensor_mock: Mock):
        infrared_sensor_mock.return_value = False
        intelligent_office = IntelligentOffice()

        infrared_pins = [intelligent_office.INFRARED_PIN1,
                         intelligent_office.INFRARED_PIN2,
                         intelligent_office.INFRARED_PIN3,
                         intelligent_office.INFRARED_PIN4]
        for infrared_pin in infrared_pins:
            is_occupied = intelligent_office.check_quadrant_occupancy(infrared_pin)
            infrared_sensor_mock.assert_called_with(infrared_pin)
            self.assertFalse(is_occupied)

    @patch.object(GPIO, "input")
    def test_check_quadrant_occupancy_not_valid_pin(self, infrared_sensor_mock: Mock):
        infrared_sensor_mock.return_value = True
        intelligent_office = IntelligentOffice()
        not_valid_infrared_pin = intelligent_office.LED_PIN

        self.assertRaises(IntelligentOfficeError, intelligent_office.check_quadrant_occupancy, not_valid_infrared_pin)

