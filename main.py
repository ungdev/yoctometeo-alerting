#!/usr/bin/python3

import json
from module import Module
from sensor import Sensor
from alert import *
from filters import *
from yoctopuce.yocto_api import *
from os import path
import logging
import graypy

modules = []
sensors = []
alerts = []

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

with open(CONFIG_PATH) as config_file:
    config = json.load(config_file)
    if 'mail-server' not in config:
        print("Mail server config missing : e-mail alerts will be unavailable.")
        mail_config = None
    else:
        mail_config = config["mail-server"]
    if 'log-server' not in config:
        print("Log server config missing : remote logging will be unavailable.")
        log_config = None
    else:
        log_config = config["log-server"]
    sleep_time = config["sleep-time"]
    addressees = config["addressees"]

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    if log_config is not None:
        logger.addFilter(AppNameFilter(log_config["application-name"]))
        handler = graypy.GELFHandler(log_config["host"], log_config["port"])
        logger.addHandler(handler)

    for module in config["modules"]:
        obj_module = Module(json_config=module)
        obj_module.get_hw_module()
        modules.append(obj_module)
        logger.addFilter(ModuleFilter(obj_module))
        alerts.append(ModuleDisconnectedAlert("alert.module.%s" % obj_module.hwid, obj_module))
        for sensor in module["sensors"]:
            obj_sensor = Sensor(obj_module, json_config=sensor)
            obj_sensor.get_hw_sensor()
            sensors.append(obj_sensor)
            logger.addFilter(SensorFilter(obj_sensor))
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
        if alert.id in states_read:
            alert.status = states_read[alert.id]

states = dict()
while True:
    try:
        for alert in alerts:
            states[alert.id] = alert.check(mail_config, addressees, logger)
        logger.info("Program operation report")
    except DisconnectedModuleException as dme:
        print(dme)
    except Exception as e:
        print(e)
    finally:
        with open("states.json", "w") as states_file_write:
            states_file_write.write(json.dumps(states))
        YAPI.Sleep(sleep_time)