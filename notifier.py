import logging
import sys
from telegram import Bot

_LOGGER = logging.getLogger(__name__)


def _parameter_boundaries(min_value, max_value):
    if min_value == ~sys.maxsize and max_value == sys.maxsize:
        return "-"
    if min_value == ~sys.maxsize:
        return "< " + max_value
    if max_value == sys.maxsize:
        return "> " + min_value
    return '{} \- {}'.format(min_value, max_value)


class Notifier(object):
    _EMOJI = {'light': "☀️",
              'temperature': "🌡",
              'moisture': "💧",
              'conductivity': "💩",
              'battery': "🔋"}
    _TEMPLATE = '''🥀 🍂 
*Plant*: {}
*Parameter*: {}
*Well\-being boundaries*: {}
*Current value*: {}
'''

    def __init__(self, token, channel):
        self._bot = Bot(token)
        self._channel = channel

    def evaluate_n_send(self, name, parameter, min_value, max_value, values):
        value = values[parameter]
        if value < min_value or max_value < value:
            _LOGGER.info("{}'s '{}'={} is out of the boundaries [{}, {}]".format(name, parameter, value, min_value,
                                                                                 max_value))
            self._bot.send_message(
                self._channel,
                self._TEMPLATE.format(name, self._EMOJI[parameter], _parameter_boundaries(min_value, max_value), value),
                parse_mode="MarkdownV2"
            )
