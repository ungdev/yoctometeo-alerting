import json
import time
from module import Module
from sensor import Sensor
from alert import Alert
from yoctopuce.yocto_api import *

modules = []
sensors = []
alerts = []

with open('config.json') as config_file:
    config = json.load(config_file)
    mail_config = config["mail-server"]
    #sleep_time = config["sleep-time"]
    sleep_time = 5
    addressees = config["addressees"]
    for module in config["modules"]:
        obj_module = Module(json_config=module)
        obj_module.get_hw_module()
        modules.append(obj_module)
        for sensor in module["sensors"]:
            obj_sensor = Sensor(obj_module, json_config=sensor)
            obj_sensor.get_hw_sensor()
            sensors.append(obj_sensor)
            for alert in sensor["alerts"]:
                obj_alert = Alert(obj_sensor, json_config=alert)
                alerts.append(obj_alert)

while True:
    print("---- %s ----" % time.asctime(time.localtime(time.time())))
    for sensor in sensors:
        print("Module %s, %s sensor : %4.1f %s" % (sensor.module.hwid, sensor.type, sensor.get_value(), sensor.get_unit()))
    for alert in alerts:
        alert.check(mail_config, addressees)
    YAPI.Sleep(1000)