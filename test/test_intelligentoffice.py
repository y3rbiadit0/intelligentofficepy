import unittest
from datetime import datetime
from unittest.mock import patch, Mock, PropertyMock
import mock.GPIO as GPIO
from mock.SDL_DS3231 import SDL_DS3231
from mock.adafruit_veml7700 import VEML7700
from src.intelligentoffice import IntelligentOffice, IntelligentOfficeError


class TestIntelligentOffice(unittest.TestCase):
    
    def setUp(self):
        self.intelligent_office = IntelligentOffice()
        self.infrared_pins = [self.intelligent_office.INFRARED_PIN1, self.intelligent_office.INFRARED_PIN2, self.intelligent_office.INFRARED_PIN3, self.intelligent_office.INFRARED_PIN4]
    
    @patch.object(GPIO, "input")
    def test_check_quadrant_occupancy_occupied(self, infrared_sensor_mock: Mock):
        infrared_sensor_mock.return_value = True

        for infrared_pin in self.infrared_pins:
            is_occupied = self.intelligent_office.check_quadrant_occupancy(infrared_pin)
            infrared_sensor_mock.assert_called_with(infrared_pin)
            self.assertTrue(is_occupied)

    @patch.object(GPIO, "input")
    def test_check_quadrant_occupancy_free(self, infrared_sensor_mock: Mock):
        infrared_sensor_mock.return_value = False

        for infrared_pin in self.infrared_pins:
            is_occupied = self.intelligent_office.check_quadrant_occupancy(infrared_pin)
            infrared_sensor_mock.assert_called_with(infrared_pin)
            self.assertFalse(is_occupied)

    def test_check_quadrant_occupancy_not_valid_pin(self):
        
        not_valid_infrared_pin = self.intelligent_office.LED_PIN

        self.assertRaises(IntelligentOfficeError, self.intelligent_office.check_quadrant_occupancy, not_valid_infrared_pin)

    @patch.object(IntelligentOffice, "change_servo_angle")
    @patch.object(SDL_DS3231, "read_datetime")
    def test_manage_blinds_based_on_time_open(self, read_datetime_mock: Mock, change_servo_angle_mock: Mock):
        read_datetime_mock.return_value = datetime(2024, 10, 7, 8, 0, 0)
        

        self.intelligent_office.manage_blinds_based_on_time()
        change_servo_angle_mock.assert_called_once_with(12) # (180/18) + 2
        self.assertTrue(self.intelligent_office.blinds_open)

    @patch.object(IntelligentOffice, "change_servo_angle")
    @patch.object(SDL_DS3231, "read_datetime")
    def test_manage_blinds_based_on_time_closes(self, read_datetime_mock: Mock,
                                              change_servo_angle_mock: Mock):
        read_datetime_mock.return_value = datetime(2024, 10, 10, 20, 0, 0)
        
        self.intelligent_office.blinds_open = True

        self.intelligent_office.manage_blinds_based_on_time()
        change_servo_angle_mock.assert_called_once_with(2)  # (0/18) + 2
        self.assertFalse(self.intelligent_office.blinds_open)

    @patch.object(IntelligentOffice, "change_servo_angle")
    @patch.object(SDL_DS3231, "read_datetime")
    def test_manage_blinds_based_on_time_saturday_sunday(self, read_datetime_mock: Mock,
                                                change_servo_angle_mock: Mock):

        read_datetime_mock.side_effect = [datetime(2024, 10, 5, 20, 0, 0), datetime(2024, 10, 6, 20, 0, 0)]
        
        for _ in read_datetime_mock.side_effect:
            self.intelligent_office.manage_blinds_based_on_time()
            change_servo_angle_mock.assert_not_called()  # (0/18) + 2
            self.assertFalse(self.intelligent_office.blinds_open)


    @patch.object(GPIO, "input")
    @patch.object(GPIO, "output")
    def test_manage_light_level_turn_on(self, led_sensor_mock: Mock, infrared_sensor_mock: Mock):
        infrared_sensor_mock.return_value = True
        with patch("mock.adafruit_veml7700.VEML7700.lux", PropertyMock()) as mock_lux:
            mock_lux.return_value = 499.0

            self.intelligent_office.manage_light_level()

            led_sensor_mock.assert_called_once_with(self.intelligent_office.LED_PIN, True)
            self.assertTrue(self.intelligent_office.light_on)

    @patch.object(GPIO, "input")
    @patch.object(GPIO, "output")
    def test_manage_light_level_turn_off(self, led_sensor_mock: Mock, infrared_sensor_mock: Mock):
        infrared_sensor_mock.return_value = True
        with patch("mock.adafruit_veml7700.VEML7700.lux", PropertyMock()) as mock_lux:
            mock_lux.return_value = 551.0

            self.intelligent_office.manage_light_level()

            led_sensor_mock.assert_called_once_with(self.intelligent_office.LED_PIN, False)
            self.assertFalse(self.intelligent_office.light_on)

    @patch.object(GPIO, "input")
    def test_manage_light_level_turn_off_light_when_all_workers_off(self, infrared_sensor_mock: Mock, ):
        with patch("mock.adafruit_veml7700.VEML7700.lux", PropertyMock()) as mock_lux:
            mock_lux.return_value = 499.0
            infrared_sensor_mock.return_value = False
            self.intelligent_office.manage_light_level()

            for infrared_pin in self.infrared_pins:
                infrared_sensor_mock.assert_any_call(infrared_pin)

            self.assertFalse(self.intelligent_office.light_on)

    @patch.object(GPIO, "input")
    def test_manage_light_level_turn_off_light_when_all_workers_off(self, infrared_sensor_mock: Mock, ):
        with patch("mock.adafruit_veml7700.VEML7700.lux", PropertyMock()) as mock_lux:
            mock_lux.return_value = 499.0
            infrared_sensor_mock.return_value = True
            self.intelligent_office.manage_light_level()

            infrared_sensor_mock.assert_called_with(self.infrared_pins[0])

            self.assertTrue(self.intelligent_office.light_on)


