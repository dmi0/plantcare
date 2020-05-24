#!/usr/bin/env python3
import os

from btlewrap import BluepyBackend
from miflora.miflora_poller import MiFloraPoller, MI_BATTERY, MI_CONDUCTIVITY, MI_LIGHT, MI_MOISTURE, MI_TEMPERATURE

if __name__ == '__main__':
    sensors_env = os.environ.get("SENSORS")
    if sensors_env is None:
        print("Environment variable SENSORS is not defined")
        exit(1)
    sensors = {}
    try:
        for s in sensors_env.strip(" ;").split(";"):
            (key, val) = s.strip(" =").split("=")
            sensors[key.strip()] = val.strip()
    except ValueError:
        print((
                  "Environment variable SENSORS is expected in format: "
                  "sensor1_name=sensor1_mac;sensor2_name=sensor2_mac, but '{}' is given"
              ).format(sensors_env))
        exit(1)
    print(sensors)

    flores = {}
    parameters = [MI_LIGHT, MI_TEMPERATURE, MI_MOISTURE, MI_CONDUCTIVITY, MI_BATTERY]
    for name, mac in sensors.items():
        poller = MiFloraPoller(mac=mac, backend=BluepyBackend, cache_timeout=60, retries=3, adapter="hci0")

        data = {}
        for param in parameters:
            print(param)
            data[param] = poller.parameter_value(param)
        print(data)
