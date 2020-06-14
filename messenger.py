import sys

from telegram import Bot


class Messenger(object):
    def __init__(self, token, channel, parser_mode, render):
        self._bot = Bot(token)
        self._channel = channel
        self._parser_mode = parser_mode
        self._render = render

    def send(self, name, param, value):
        self._bot.send_message(
            self._channel,
            self._render.prepare(name, param, value),
            parse_mode=self._parser_mode
        )


def _render_boundaries(boundary):
    if boundary["min"] is not None and boundary["max"] is not None:
        return "[{}, {}]".format(boundary["min"], boundary["max"])
    elif boundary["min"] is not None:
        return "≥ {}".format(boundary["min"])
    elif boundary["max"] is not None:
        return "≤ {}".format(boundary["max"])
    return ""


class AlertMessageRender(object):
    def __init__(self, sensors_config, templates_config):
        self.templates = templates_config
        self.boundaries = {}
        for name, s in sensors_config.items():
            self.boundaries[name] = {}
            for p, b in s["wellbeing_range"].items():
                self.boundaries[name][p] = _render_boundaries(b)

    def prepare(self, name, param, value):
        return self.templates[param].format(plant=name, boundaries=self.boundaries[name][param], value=value)


class RangeCheckerEvaluator(object):
    def __init__(self, sensor_config):
        self.boundaries = {}
        for p, b in sensor_config["wellbeing_range"].items():
            self.boundaries[p] = {
                "min": b["min"] if b["min"] is not None else ~sys.maxsize,
                "max": b["max"] if b["max"] is not None else sys.maxsize
            }

    def need_to_notify(self, param, value):
        if param not in self.boundaries:
            return False
        return not self.boundaries[param]["min"] <= value <= self.boundaries[param]["max"]
