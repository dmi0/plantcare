import logging

from bluepy.btle import BTLEException
from btlewrap import BluepyBackend, BluetoothBackendException
from miflora.miflora_poller import MiFloraPoller, MI_BATTERY, MI_CONDUCTIVITY, MI_LIGHT, MI_MOISTURE, MI_TEMPERATURE

_param_map = {
    "light": MI_LIGHT, "temperature": MI_TEMPERATURE, "moisture": MI_MOISTURE,
    "conductivity": MI_CONDUCTIVITY, "battery": MI_BATTERY
}
PARAMETERS = _param_map.keys()
_LOGGER = logging.getLogger(__name__)


class PlantSensorException(Exception):
    pass


class PlantSensor(object):
    _CACHE_TIMEOUT = 5

    def __init__(self, adapter, name, mac):
        self.name = name
        self._mac = mac
        self._adapter = adapter
        self._poller = None

    def _get_poller(self):
        if self._poller is None:
            self._poller = MiFloraPoller(
                mac=self._mac, backend=BluepyBackend, cache_timeout=self._CACHE_TIMEOUT, adapter=self._adapter
            )
            try:
                firmware = self._poller.firmware_version()
                if firmware is None or int(firmware.replace(".", "")) < 319:
                    self._fail("Sensor firmware version must not be before 3.1.9, however {} detected".format(firmware))
            except (IOError, BluetoothBackendException, BTLEException, RuntimeError, BrokenPipeError) as e:
                self._fail("Connection to {} failed".format(self.name), e)
            else:
                _LOGGER.info("Connected to {}".format(self.name))
                _LOGGER.debug(
                    "Device info: name={}, mac={}, firmware_version={})".format(self._poller.name(), self._mac,
                                                                                firmware)
                )
        return self._poller

    def _read(self, param):
        try:
            return self._get_poller().parameter_value(param)
        except (IOError, BluetoothBackendException, BTLEException, RuntimeError, BrokenPipeError) as e:
            self._fail("Failed reading '{}' parameter from {}".format(param, self.name), e)

    def read(self):
        return {param_name: self._read(param_key) for (param_name, param_key) in _param_map.items()}

    def _fail(self, msg, e=None):
        self._poller = None
        if e is None:
            raise PlantSensorException(msg)
        else:
            raise PlantSensorException(msg) from e
