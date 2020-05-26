#!/usr/bin/env python3
import logging
import os
from time import sleep

from config import read_loglevel_config, read_max_attempts_config, read_adapter_config, read_sensors_config, \
    read_telegram_token_config, read_telegram_channel_config
from notifier import Notifier
from plantsensor import PlantSensor, PlantSensorException

_LOGGER = logging.getLogger(__name__)


def main():
    max_attempts = read_max_attempts_config()
    adapter = read_adapter_config()
    telegram_token = read_telegram_token_config()
    telegram_channel = read_telegram_channel_config()
    sensors = None
    try:
        sensors = read_sensors_config()
    except ValueError as e:
        _LOGGER.exception("Failed to parse SENSORS configuration", exc_info=e)
        exit(1)
    _LOGGER.info("Configured sensors: {}".format(sensors))

    notifier = Notifier(telegram_token, telegram_channel)
    success = check_sensors(notifier, adapter, sensors, max_attempts)
    _LOGGER.info("Done. {}/{} are successfully processed".format(success, len(sensors)))


def check_sensors(notifier, adapter, sensors, max_attempts):
    sensors_to_process = dict((name, max_attempts) for name in sensors)
    success = 0
    while True:
        sensors_to_repeat = {}
        for name, attempts in sensors_to_process.items():
            sensor = sensors[name]
            try:
                ps = PlantSensor(name, sensor["mac"], adapter)
                readings = ps.status()
                _LOGGER.info("{} sensor readings: {}".format(name, readings))
                notifier.evaluate_n_send(name, sensor["parameter"], sensor["min"], sensor["max"], readings)
                success += 1
            except PlantSensorException as e:
                if attempts > 1:
                    attempts -= 1
                    _LOGGER.info(
                        "{} sensor reading failed, {}/{} attempt{} left ".format(
                            name, attempts, max_attempts,
                            "s" if attempts > 1 else "")
                    )
                    sensors_to_repeat[name] = attempts
                else:
                    _LOGGER.error("{} sensor reading failed".format(name), exc_info=e)
        if len(sensors_to_repeat) > 0:
            sleep(5)
            sensors_to_process = sensors_to_repeat
        else:
            break
    return success


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

    main()
