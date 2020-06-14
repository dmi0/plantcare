import json
import logging
import os

from plantsensor import PARAMETERS

_LOGGER = logging.getLogger(__name__)
_config = {
    "_loaded": False,
    "loglevel": "INFO",
    "adapter": "hci0",
    "max_attempts": 5,
    "telegram": {
        "token": None,
        "channel": None,
        "message": {
            "parse_mode": "MarkdownV2",
            **{param: "{plant}: '" + param + "' parameter is out of boundaries '{boundaries}'" for param in PARAMETERS}
        }
    },
    "sensors": {}
}


def _update(a, b):
    for key in a:
        if key in b and key != "_loaded":
            if isinstance(a[key], dict) and isinstance(b[key], dict) and len(a[key]) > 0:
                _update(a[key], b[key])
            elif isinstance(b[key], type(a[key])) or a[key] is None:
                a[key] = b[key]
            else:
                raise ValueError(
                    "'{}' is expected to have {} type, but {} found".format(key, type(a[key]), type(b[key]))
                )


def _load_custom():
    config = os.environ.get("CONFIG")
    if config is None or config.strip() == "":
        return {}
    else:
        return json.loads(config.strip())


def _get_cfg():
    if not _config["_loaded"]:
        _update(_config, _load_custom())
        _config["_loaded"] = True
    return _config


def get_all():
    config = _get_cfg()
    return {key: config[key] for key in config if key != "_loaded"}


def get_max_attempts():
    config = _get_cfg()
    try:
        return int(config["max_attempts"])
    except ValueError as e:
        raise ValueError(
            "'max_attempts' is expected to be numerical, but '{}' is given".format(config["max_attempts"])
        ) from e


def get_loglevel():
    config = _get_cfg()
    allowed = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]
    loglevel = config["loglevel"]
    if loglevel not in allowed:
        raise ValueError("'loglevel' can accept only one of {}, but '{}' is given".format(allowed, loglevel))
    return loglevel


def get_adapter():
    return _get_non_empty("adapter")


def get_telegram_token():
    return _get_non_empty("telegram", "token")


def get_telegram_channel():
    return _get_non_empty("telegram", "channel")


def get_message_parse_mode():
    return _get_non_empty("telegram", "message", "parse_mode")


def _get_non_empty(*keys):
    value = _get_cfg()
    key = None
    for key in keys:
        value = value[key]
    if value is None or value == "":
        raise ValueError("'{}' cannot be empty".format(key))
    return value


def get_message_templates():
    return {k: v for k, v in _get_cfg()["telegram"]["message"].items() if k != "parse_mode"}


def get_sensors():
    sensors = _get_cfg()["sensors"]
    if len(sensors) == 0:
        raise ValueError("No plant sensor found")

    result = {}
    for name, item in sensors.items():
        if "mac" not in item or item["mac"] is None or item["mac"] == "":
            raise ValueError("'mac' is not defined for '{}'".format(name))
        if "wellbeing_range" not in item:
            raise ValueError("'wellbeing_range' parameter is not defined for '{}'".format(name))
        wellbeing_range = item["wellbeing_range"]
        if not isinstance(wellbeing_range, dict):
            raise ValueError(
                "'wellbeing_range' is expected to be a yaml mapping, but '{}' is given for '{}'".format(
                    item["wellbeing_range"], name
                )
            )
        val = {"mac": item["mac"].strip(), "wellbeing_range": {}}
        for p, r in wellbeing_range.items():
            if p not in PARAMETERS:
                raise ValueError("parameter {} is not in supported list {} for '{}'".format(p, PARAMETERS, name))
            try:
                p_min = int(r["min"]) if "min" in r else None
                p_max = int(r["max"]) if "max" in r else None
            except ValueError as e:
                raise ValueError(
                    "min and/or max are expected to be numerical for '{}' parameter for '{}'".format(p, name)
                ) from e
            if p_min is not None and p_max is not None:
                if p_min > p_max:
                    raise ValueError("Wrong '{}' parameter boundaries for '{}': [{},{}]".format(p, name, p_min, p_max))
            val["wellbeing_range"][p] = {"min": p_min, "max": p_max}
        result[name.strip()] = val
    return result
