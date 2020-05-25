#!/usr/bin/env python3
import logging
import os
from time import sleep

from plantsensor import PlantSensor, PlantSensorException


def read_sensors_config():
    sensors_env = os.environ.get("SENSORS")
    if sensors_env is None:
        raise ValueError("Environment variable SENSORS is not defined")

    result = {}
    try:
        for s in sensors_env.strip(" ;").split(";"):
            (name, mac) = s.strip(" =").split("=")
            result[name.strip()] = mac.strip()
    except ValueError:
        raise ValueError(("Environment variable SENSORS is expected in format: "
                          "sensor1_name=sensor1_mac;sensor2_name=sensor2_mac, but '{}' is given"
                          ).format(sensors_env))
    return result


if __name__ == '__main__':
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"),
                        format='%(asctime)s [%(name)-24s] %(levelname)-8s %(message)s')
    _LOGGER = logging.getLogger(__name__)

    sensors = {}
    try:
        sensors = read_sensors_config()
    except ValueError as e:
        _LOGGER.error(e)
        exit(1)
    _LOGGER.info("Configured sensors: {}".format(sensors))

    sensors_to_process = dict((name, {"mac": mac, "attempts": 3}) for name, mac in sensors.items())
    while True:
        sensors_to_repeat = {}
        for s_name, s_item in sensors_to_process.items():
            try:
                ps = PlantSensor(s_name, s_item["mac"])
                readings = ps.status()
                _LOGGER.info("{} sensor readings: {}".format(s_name, readings))
            except PlantSensorException as e:
                attempts = sensors_to_process[s_name]["attempts"]
                if attempts > 1:
                    attempts -= 1
                    _LOGGER.info(
                        "{} sensor reading failed, {}/{} attempt{} left ".format(
                            s_name, attempts, 5,
                            "s" if attempts > 1 else "")
                    )
                    sensors_to_repeat[s_name] = {"mac": s_item["mac"], "attempts": attempts}
                else:
                    _LOGGER.error("{} sensor reading failed".format(s_name), exc_info=e)
        if len(sensors_to_repeat) > 0:
            sleep(2)
            sensors_to_process = sensors_to_repeat
        else:
            break
