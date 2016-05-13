from alerting import *
from exceptions import *


class Alert(object):

    def __init__(self, alert_id, alert_vector=None, level=None, status="iddle", alert_type="generic"):
        self.id = alert_id
        self.vector = alert_vector
        self.level = level
        self.status = status
        self.alert_type = alert_type

    def check(self, config_mail, addressees, logger=None):
        return self.status

    def triggering(self, config_mail, addressees, body=None, logger=None):
        self.status = "triggered"
        if (self.vector == "email") | (self.vector == "*"):
            subject = "%s alert" % self.alert_type
            for addressee in addressees:
                send_mail(config_mail, addressee["mail"], subject, body)
        send_log_alert(logger, self.level, body)

    def resetting(self, config_mail, addressees, body=None, logger=None):
        self.status = "iddle"
        if (self.vector == "email") | (self.vector == "*"):
            subject = "End of %s alert" % self.alert_type
            for addressee in addressees:
                send_mail(config_mail, addressee["mail"], subject, body)
        send_log_alert(logger, self.level, body)



class ModuleDisconnectedAlert(Alert):

    def __init__(self, alert_id, module, alert_vector="*", level="critical", status="iddle", alert_type="module"):
        Alert.__init__(self, alert_id, alert_vector, level, status, alert_type)
        self.module = module

    def check(self, config_mail, addressees, logger=None):
        try:
            self.module.get_hw_module()
        except DisconnectedModuleException as dme:
            if self.status == "iddle":
                self.triggering(config_mail, addressees, logger=logger)
        else:
            if self.status == "triggered":
                self.resetting(config_mail, addressees, logger=logger)
        return self.status

    def triggering(self, config_mail, addressees, body=None, logger=None):
        id = self.module.hwid
        body = "Module %s appears to be disconnected. Alerts related to this module will be suspended pending resolution." % id
        Alert.triggering(self, config_mail, addressees, body, logger)

    def resetting(self, config_mail, addressees, body=None, logger=None):
        id = self.module.hwid
        body = "Module %s has been reconnected. Resuming normal operation." % id
        Alert.resetting(self, config_mail, addressees, body, logger)


class SensorAlert(Alert):

    def __init__(self, sensor, alert_id=None, alert_vector=None, level=None, direction=None, trigger=None, reset=None,
                 status="iddle", json_config=None):
        if json_config is not None:
            Alert.__init__(self, json_config["alert-id"], json_config["alert-vector"], json_config["level"], status, sensor.type)
            self.direction = json_config["direction"]
            self.trigger = json_config["trigger"]
            self.reset = json_config["reset"]
        else:
            Alert.__init__(self, alert_id, alert_vector, level, status, sensor.type)
            self.direction = direction
            self.trigger = trigger
            self.reset = reset
        self.sensor = sensor

    def check(self, config_mail, addressees, logger=None):
        value = self.sensor.get_value()
        if self.status == "iddle":
            if self.direction == "over":
                if value > self.trigger:
                    self.triggering(config_mail, addressees, logger=logger)
            elif self.direction == "below":
                if value < self.trigger:
                    self.triggering(config_mail, addressees, logger=logger)
        elif self.status == "triggered":
            if self.direction == "over":
                if value < self.reset:
                    self.resetting(config_mail, addressees, logger=logger)
            elif self.direction == "below":
                if value > self.reset:
                    self.resetting(config_mail, addressees, logger=logger)
        return self.status

    def triggering(self, config_mail, addressees, body=None, logger=None):
        value = self.sensor.get_value()
        sensor_type = self.sensor.type
        body = "Module %s, %s sensor : %4.1f %s, expected %s %4.1f" % (
            self.sensor.module.hwid, sensor_type, value, self.sensor.get_unit(),
            "<" if self.direction == "over" else ">", self.trigger)
        Alert.triggering(self, config_mail, addressees, body, logger)

    def resetting(self, config_mail, addressees, body=None, logger=None):
        value = self.sensor.get_value()
        sensor_type = self.sensor.type
        body = "Module %s, %s sensor : back to normal (%4.1f %s)" % (
            self.sensor.module.hwid, sensor_type, value, self.sensor.get_unit())
        Alert.resetting(self, config_mail, addressees, body, logger)