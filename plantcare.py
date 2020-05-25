#!/usr/bin/env python3
import json
import logging
import os
import sys
from time import sleep

from plantsensor import PlantSensor, PlantSensorException

DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_ADAPTER = "hci0"

_LOGGER = logging.getLogger(__name__)


def read_sensors_config():
    sensors_env = os.environ.get("SENSORS")
    if sensors_env is None:
        raise ValueError("Environment variable SENSORS is not defined")

    result = {}
    for name, item in json.loads(sensors_env).items():
        if "mac" not in item or "parameter" not in item:
            raise ValueError("'mac' or 'parameter' is not found in {}".format(item))
        val = {
            "mac": item["mac"].strip(),
            "parameter": item["parameter"].strip(),
            "max": int(item["max"]) if "max" in item else sys.maxsize,
            "min": int(item["min"]) if "min" in item else ~sys.maxsize,
        }
        if val["min"] > val["max"]:
            raise ValueError("Wrong parameter boundaries: {}".format(item))
        result[name.strip()] = val
    return result


def read_max_attempts_config():
    if os.environ.get("MAX_ATTEMPTS") is None:
        return DEFAULT_MAX_ATTEMPTS
    try:
        return int(os.environ.get("MAX_ATTEMPTS"))
    except ValueError:
        return DEFAULT_MAX_ATTEMPTS


def read_loglevel_config():
    if os.environ.get("LOGLEVEL") is not None:
        return os.environ.get("LOGLEVEL")
    else:
        return DEFAULT_LOG_LEVEL


def read_adapter_config():
    if os.environ.get("ADAPTER") is not None:
        return os.environ.get("ADAPTER")
    else:
        return DEFAULT_ADAPTER


def evaluate(name, parameter, min_value, max_value, values):
    value = values[parameter]
    if value < min_value or max_value < value:
        _LOGGER.info(
            "{}'s '{}'={} is out of the boundaries [{}, {}]".format(name, parameter, value, min_value, max_value)
        )


if __name__ == '__main__':
    loglevel = read_loglevel_config()
    logging.basicConfig(level=os.environ.get("LOGLEVEL", loglevel),
                        format='%(asctime)s [%(name)-24s] %(levelname)-8s %(message)s')
    max_attempts = read_max_attempts_config()
    adapter = read_adapter_config()

    sensors = None
    try:
        sensors = read_sensors_config()
    except ValueError as e:
        _LOGGER.exception("Failed to parse SENSORS configuration", exc_info=e)
        exit(1)
    _LOGGER.info("Configured sensors: {}".format(sensors))

    sensors_to_process = dict((name, max_attempts) for name in sensors)
    success = 0
    while True:
        sensors_to_repeat = {}
        for s_name, attempts in sensors_to_process.items():
            s_item = sensors[s_name]
            try:
                ps = PlantSensor(s_name, s_item["mac"], adapter)
                readings = ps.status()
                _LOGGER.info("{} sensor readings: {}".format(s_name, readings))
                evaluate(s_name, s_item["parameter"], s_item["min"], s_item["max"], readings)
                success += 1
            except PlantSensorException as e:
                if attempts > 1:
                    attempts -= 1
                    _LOGGER.info(
                        "{} sensor reading failed, {}/{} attempt{} left ".format(
                            s_name, attempts, max_attempts,
                            "s" if attempts > 1 else "")
                    )
                    sensors_to_repeat[s_name] = attempts
                else:
                    _LOGGER.error("{} sensor reading failed".format(s_name), exc_info=e)
        if len(sensors_to_repeat) > 0:
            sleep(5)
            sensors_to_process = sensors_to_repeat
        else:
            break

    _LOGGER.info("Done. {}/{} are successfully processed".format(success, len(sensors)))
