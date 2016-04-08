import json
import time
from module import Module
from sensor import Sensor
from alert import *
from exceptions import *
from yoctopuce.yocto_api import *

modules = []
sensors = []
alerts = []

with open('config.json') as config_file:
    config = json.load(config_file)
    mail_config = config["mail-server"]
    sleep_time = config["sleep-time"]
    addressees = config["addressees"]
    for module in config["modules"]:
        obj_module = Module(json_config=module)
        obj_module.get_hw_module()
        modules.append(obj_module)
        alerts.append(ModuleDisconnectedAlert(obj_module))
        for sensor in module["sensors"]:
            obj_sensor = Sensor(obj_module, json_config=sensor)
            obj_sensor.get_hw_sensor()
            sensors.append(obj_sensor)
            for alert in sensor["alerts"]:
                obj_alert = SensorAlert(obj_sensor, json_config=alert)
                alerts.append(obj_alert)
try:
    states_file_read = open('states.json', 'r')
except FileNotFoundError:
    print("States persistence file not found. Initializing with default states.")
else:
    states_read = json.load(states_file_read)
    states_file_read.close()
    for alert in alerts:
        if id(alert) in states_read:
            alert.status = states_read[id(alert)]

states = dict()
while True:
    print("---- %s ----" % time.asctime(time.localtime(time.time())))
    try:
        for alert in alerts:
            states[id(alert)] = alert.check(mail_config, addressees)
        for sensor in sensors:
            print("Module %s, %s sensor : %4.1f %s" % (sensor.module.hwid, sensor.type, sensor.get_value(), sensor.get_unit()))
    except DisconnectedModuleException as dme:
        print(dme)
    finally:
        with open("states.json", "w") as states_file_write:
            states_file_write.write(json.dumps(states))
        YAPI.Sleep(1000)