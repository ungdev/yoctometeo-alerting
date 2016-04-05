import json
from module import Module
from sensor import Sensor
from alert import Alert

modules = []
sensors = []
alerts = []

with open('config.json') as config_file:
    config = json.load(config_file)
    mail_config = config["mail-server"]
    for module in config["modules"]:
        obj_module = Module(json_config=module)
        modules.append(obj_module)
        for sensor in module["sensors"]:
            obj_sensor = Sensor(obj_module, json_config=sensor)
            sensors.append(obj_sensor)
            for alert in sensor["alerts"]:
                obj_alert = Alert(obj_sensor, alert)
                alerts.append(obj_alert)

