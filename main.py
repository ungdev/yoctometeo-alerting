import json
import time
from module import Module
from sensor import Sensor
from alert import *
from exceptions import *
from yoctopuce.yocto_api import *
import logging
import graypy

modules = []
sensors = []
alerts = []

with open('config.json') as config_file:
    config = json.load(config_file)
    mail_config = config["mail-server"]
    log_config = config["log-server"]
    sleep_time = config["sleep-time"]
    addressees = config["addressees"]
    for module in config["modules"]:
        obj_module = Module(json_config=module)
        obj_module.get_hw_module()
        modules.append(obj_module)
        alerts.append(ModuleDisconnectedAlert("alert.module.%s" % obj_module.hwid, obj_module))
        for sensor in module["sensors"]:
            obj_sensor = Sensor(obj_module, json_config=sensor)
            obj_sensor.get_hw_sensor()
            sensors.append(obj_sensor)
            for alert in sensor["alerts"]:
                obj_alert = SensorAlert(obj_sensor, json_config=alert)
                alerts.append(obj_alert)

logger = logging.getLogger('yoctometeo-alerting')
logger.setLevel(logging.DEBUG)
handler = graypy.GELFHandler(log_config["host"], log_config["port"])
logger.addHandler(handler)

try:
    states_file_read = open('states.json', 'r')
except FileNotFoundError:
    print("States persistence file not found. Initializing with default states.")
else:
    states_read = json.load(states_file_read)
    states_file_read.close()
    for alert in alerts:
        if alert.id in states_read:
            alert.status = states_read[alert.id]

states = dict()
while True:
    print("---- %s ----" % time.asctime(time.localtime(time.time())))
    try:
        for alert in alerts:
            states[alert.id] = alert.check(mail_config, addressees, logger)
        for sensor in sensors:
            print("Module %s, %s sensor : %4.1f %s" % (sensor.module.hwid, sensor.type, sensor.get_value(), sensor.get_unit()))
    except DisconnectedModuleException as dme:
        print(dme)
        #logger.critical("Module disconnected", exc_info=1)
    finally:
        with open("states.json", "w") as states_file_write:
            states_file_write.write(json.dumps(states))
        YAPI.Sleep(1000)