#!/usr/bin/env python3
import logging
from time import sleep

import config
from messenger import Messenger, AlertMessageRender, RangeCheckerEvaluator
from plantsensor import PlantSensor, PlantSensorException

_LOGGER = logging.getLogger(__name__)
_SLEEP = 5


def main():
    try:
        max_attempts = config.get_max_attempts()
        adapter = config.get_adapter()
        telegram_token = config.get_telegram_token()
        telegram_channel = config.get_telegram_channel()
        sensors = config.get_sensors()
        message_parser_mode = config.get_message_parse_mode()
        message_templates = config.get_message_templates()
    except ValueError as e:
        _LOGGER.exception("Reading configuration failed", exc_info=e)
        exit(1)
    else:
        _LOGGER.info("Configured sensors: {}".format(sensors))
        message_render = AlertMessageRender(sensors, message_templates)
        messenger = Messenger(telegram_token, telegram_channel, message_parser_mode, message_render)
        evaluators = {name: RangeCheckerEvaluator(sensor) for name, sensor in sensors.items()}
        queue = [PlantSensor(adapter, name, sensor["mac"]) for name, sensor in sensors.items()]
        success = check_sensors(queue, max_attempts, messenger, evaluators)
        _LOGGER.info("Done. {}/{} are successfully processed".format(success, len(sensors)))


def check_sensors(queue, max_attempts, messenger, evaluators):
    lap = 1
    total_size = len(queue)
    to_retry = len(queue)
    while len(queue) > 0 and lap <= max_attempts:
        sensor = queue.pop(0)
        to_retry -= 1
        try:
            _check_sensor(sensor, evaluators[sensor.name], messenger)
        except PlantSensorException as e:
            queue.append(sensor)
            if lap < max_attempts:
                _LOGGER.info(
                    "{} sensor reading failed, {}/{} attempt{} left ".format(
                        sensor.name, max_attempts - lap, max_attempts, "s" if max_attempts - lap > 1 else "")
                )
            else:
                _LOGGER.error("{} sensor reading failed".format(sensor.name), exc_info=e)
        if to_retry == 0:
            to_retry = len(queue)
            lap += 1
            sleep(_SLEEP)
    return total_size - len(queue)


def _check_sensor(sensor, evaluator, messenger):
    readings = sensor.read()
    _LOGGER.info("{} sensor readings: {}".format(sensor.name, readings))
    for param, value in readings.items():
        if evaluator.need_to_notify(param, value):
            _LOGGER.info("{}'s '{}'={} is out of the boundaries".format(sensor.name, param, value))
            messenger.send(sensor.name, param, value)


def evaluate(name, parameter, min_value, max_value, values):
    value = values[parameter]
    if value < min_value or max_value < value:
        _LOGGER.info(
            "{}'s '{}'={} is out of the boundaries [{}, {}]".format(name, parameter, value, min_value, max_value)
        )


if __name__ == '__main__':
    loglevel = config.get_loglevel()
    logging.basicConfig(level=loglevel, format='%(asctime)s [%(name)-24s] %(levelname)-8s %(message)s')
    _LOGGER.debug("Effective config: {}".format(config.get_all()))
    main()
