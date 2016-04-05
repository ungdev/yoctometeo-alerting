import sys
import yoctopuce.yocto_api as yapi
import yoctopuce.yocto_humidity as yhum
import yoctopuce.yocto_temperature as ytemp
import yoctopuce.yocto_pressure as ypres


class Sensor(object):

    def __init__(self, type=None, module=None, json_config=None):
        if json_config is not None:
            self.type = json_config["type"]
            self.module = module
            self.hw_sensor = None
        else:
            self.type = type
            self.module = module
            self.hw_sensor = None

    def get_hw_sensor(self):
        if self.hw_sensor is None:
            errmsg = yapi.YRefParam()
            if self.type == 'humidity':
                self.hw_sensor = yhum.YHumidity.FindHumidity(self.module.hwid + ".humidity")
            elif self.type == 'temperature':
                self.hw_sensor = ytemp.YTemperature.FindTemperature(self.module.hwid + ".temperature")
            elif self.type == 'pressure':
                self.hw_sensor = ypres.YPressure.FindPressure(self.module.hwid + ".pressure")
            else:
                sys.exit("Sensor type '%s' undefined (module '%s')" % (self.type, self.module.hwid))
        return self.hw_sensor