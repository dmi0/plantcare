import logging
from unittest import TestCase
from unittest.mock import Mock

import plantcare
from plantsensor import PlantSensorException


def _mock_sensor_read_failed_recover():
    yield PlantSensorException
    yield PlantSensorException
    while True:
        yield {}


class TestCheckSensors(TestCase):
    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.CRITICAL)
        plantcare._SLEEP = 0

    def setUp(self):
        names = ["a", "b", "c"]
        self.sensors = []
        self.evaluators = {}
        for n in names:
            self.sensors.append(Mock())
            self.sensors[-1].name = n
            self.sensors[-1].read.return_value = {}
            self.evaluators[n] = Mock()

    def test_check_sensors(self):
        self.assertEqual(plantcare.check_sensors(self.sensors, 2, Mock(), self.evaluators), 3)

    def test_check_sensors_first_failed(self):
        failed_sensor_readings = self.sensors[0].read
        failed_sensor_readings.side_effect = PlantSensorException()
        self.assertEqual(plantcare.check_sensors(self.sensors, 5, Mock(), self.evaluators), 2)
        self.assertEqual(failed_sensor_readings.call_count, 5)

    def test_check_sensors_last_failed(self):
        failed_sensor_readings = self.sensors[2].read
        failed_sensor_readings.side_effect = PlantSensorException()
        self.assertEqual(plantcare.check_sensors(self.sensors, 5, Mock(), self.evaluators), 2)
        self.assertEqual(failed_sensor_readings.call_count, 5)

    def test_check_sensors_one_failed_but_recovered(self):
        failed_sensor_readings = self.sensors[1].read
        failed_sensor_readings.side_effect = _mock_sensor_read_failed_recover()
        self.assertEqual(plantcare.check_sensors(self.sensors, 5, Mock(), self.evaluators), 3)
        self.assertEqual(failed_sensor_readings.call_count, 3)


def _mock_evaluator_need_to_notify_second(param, value):
    if param == "p1" and value == 1:
        return False
    else:
        return True


class TestCheckSensor(TestCase):
    def setUp(self) -> None:
        self.sensor = Mock()
        self.sensor.name = "plant"
        self.evaluator = Mock()
        self.messenger = Mock()

    def test__check_sensor(self):
        self.sensor.read.return_value = {"p1": 1}
        self.evaluator.need_to_notify.return_value = True
        plantcare._check_sensor(self.sensor, self.evaluator, self.messenger)

        self.sensor.read.assert_called()
        self.evaluator.need_to_notify.assert_called_with("p1", 1)
        self.messenger.send.assert_called_once_with("plant", "p1", 1)

    def test__check_sensor_one_need_to_send(self):
        self.sensor.read.return_value = {"p1": 1, "p2": 2}
        self.evaluator.need_to_notify.side_effect = _mock_evaluator_need_to_notify_second
        plantcare._check_sensor(self.sensor, self.evaluator, self.messenger)

        self.sensor.read.assert_called()
        self.messenger.send.assert_called_once_with("plant", "p2", 2)
