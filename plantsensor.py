import logging

from bluepy.btle import BTLEException
from btlewrap import BluepyBackend, BluetoothBackendException
from miflora.miflora_poller import MiFloraPoller, MI_BATTERY, MI_CONDUCTIVITY, MI_LIGHT, MI_MOISTURE, MI_TEMPERATURE

_LOGGER = logging.getLogger(__name__)


class PlantSensorException(Exception):
    pass


class PlantSensor(object):
    _CACHE_TIMEOUT = 5

    def __init__(self, name, mac, adapter="hci0"):
        self._name = name
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
                    raise PlantSensorException(
                        "Sensor firmware version must not be before 3.1.9, however {} detected".format(firmware)
                    )
            except (IOError, BluetoothBackendException, BTLEException, RuntimeError, BrokenPipeError) as e:
                raise PlantSensorException("Connection to {} failed".format(self._name)) from e
            _LOGGER.info("Connected to {}".format(self._name))
            _LOGGER.debug(
                "Device info: name={}, mac={}, firmware_version={})".format(self._poller.name(), self._mac, firmware)
            )
        return self._poller

    def _read(self, param):
        try:
            return self._get_poller().parameter_value(param)
        except (IOError, BluetoothBackendException, BTLEException, RuntimeError, BrokenPipeError) as e:
            raise PlantSensorException("Failed reading '{}' parameter from {}".format(param, self._name)) from e

    def status(self):
        return {
            'light': self._read(MI_LIGHT),
            'temperature': self._read(MI_TEMPERATURE),
            'moisture': self._read(MI_MOISTURE),
            'conductivity': self._read(MI_CONDUCTIVITY),
            'battery': self._read(MI_BATTERY),
        }
