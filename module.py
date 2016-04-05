import sys
import yoctopuce.yocto_api as yapi


class Module(object):

    def __init__(self, hardware_id=None, host=None, json_config=None):
        if json_config is not None:
            self.host = json_config["host"]
            self.hwid = json_config["hardware-id"]
        else:
            self.host = host
            self.hwid = hardware_id
        self.hw_module = None

    def get_hw_module(self):
        if self.hw_module is None:
            errmsg = yapi.YRefParam()
            if yapi.YAPI.RegisterHub(self.host, errmsg) != yapi.YAPI.SUCCESS:
                sys.exit("init error" + errmsg.value)
            self.hw_module = yapi.YModule.FindModule(self.hwid)
        return self.hw_module
