from yoctopuce.yocto_humidity import *
from yoctopuce.yocto_temperature import *
from yoctopuce.yocto_pressure import *


class Sensor(object):

    def __init__(self, module, type=None, json_config=None):
        if json_config is not None:
            self.type = json_config["type"]
            self.module = module
            self.hw_sensor = None
            self.unit = None
        else:
            self.type = type
            self.module = module
            self.hw_sensor = None
            self.unit = None

    def get_hw_sensor(self):
        if self.hw_sensor is None:
            errmsg = YRefParam()
            if self.type == 'humidity':
                self.hw_sensor = YHumidity.FindHumidity(self.module.hwid + ".humidity")
            elif self.type == 'temperature':
                self.hw_sensor = YTemperature.FindTemperature(self.module.hwid + ".temperature")
            elif self.type == 'pressure':
                self.hw_sensor = YPressure.FindPressure(self.module.hwid + ".pressure")
            else:
                sys.exit("Sensor type '%s' undefined (module '%s')" % (self.type, self.module.hwid))
        return self.hw_sensor
    
    def get_unit(self):
        if self.unit is None:
            self.unit = self.get_hw_sensor().get_unit()
        return self.unit

    def get_value(self):
        return self.get_hw_sensor().get_currentValue()