import logging
from exceptions import *


class ModuleFilter(logging.Filter):
    def __init__(self, module):
        super().__init__()
        self.module = module

    def filter(self, record):
        record.module = self.module.hwid
        return True


class SensorFilter(logging.Filter):
    def __init__(self, sensor):
        super().__init__()
        self.sensor = sensor

    def filter(self, record):
        try:
            unit = self.sensor.get_unit()
        except DisconnectedModuleException as dme:
            return True

        try:
            value = self.sensor.get_value()
            msg = "%s %s" % (value, unit)
        except DisconnectedModuleException as dme:
            msg = "N/A"

        if self.sensor.type == "temperature":
            record.temperature = msg
        elif self.sensor.type == "humidity":
            record.humidity = msg
        elif self.sensor.type == "pressure":
            record.pressure = msg
        else:
            return True

        return True
