import json
import os
import sys

DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_ADAPTER = "hci0"


def read_sensors_config():
    sensors_env = _read_required_config("SENSORS")

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


def read_telegram_token_config():
    return _read_required_config("TELEGRAM_TOKEN")


def read_telegram_channel_config():
    return _read_required_config("TELEGRAM_CHANNEL")


def _read_required_config(var):
    result = os.environ.get(var)
    if result is None:
        raise ValueError("Environment variable {} is not defined".format(var))
    return result
