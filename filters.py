import logging
from exceptions import *

class AppNameFilter(logging.Filter):
    def __init__(self, appName):
        super().__init__()
        self.appName = appName

    def filter(self, record):
        record.application_name = self.appName
        return True

class ModuleFilter(logging.Filter):
    def __init__(self, module):
        super().__init__()
        self.module = module

    def filter(self, record):
        try:
            record.module = self.module.hwid
        except DisconnectedModuleException as dme:
            return True
        except Exception as e:
            record.exception = e.__repr__()
            return True

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
        except Exception as e:
            record.exception = e.__repr__()
            return True

        try:
            value = self.sensor.get_value()
        except DisconnectedModuleException as dme:
            return True
        except Exception as e:
            record.exception = e.__repr__()
            return True

        if self.sensor.type == "temperature":
            record.temperature = value
        elif self.sensor.type == "humidity":
            record.humidity = value
        elif self.sensor.type == "pressure":
            record.pressure = value
        else:
            return True

        return True
