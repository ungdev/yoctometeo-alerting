class DisconnectedModuleException(Exception):

    def __init__(self, module, sensor=None):

        self.module = module
        self.sensor = sensor



    def __str__(self):

        str_module = "Error : module %s disconnected" % self.module.hwid
        if self.sensor is not None:
            str_sensor = " while trying to access %s sensor" % self.sensor.type
            return str_module + str_sensor
        else:
            return str_module