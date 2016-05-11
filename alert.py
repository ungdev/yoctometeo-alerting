from alerting import *
from exceptions import *
from main import addressees, mail_config


class Alert(object):

    def __init__(self, alert_vector=None, level=None, status="iddle", alert_type="generic"):
        self.vector = alert_vector
        self.level = level
        self.status = status
        self.alert_type = alert_type

    def check(self):
        return self.status

    def triggering(self, body=None):
        self.status = "triggered"
        if (self.vector == "email") | (self.vector == "*"):
            subject = "%s alert" % self.alert_type
            for addressee in addressees:
                send_mail(mail_config, addressee["mail"], subject, body)

    def resetting(self, body=None):
        self.status = "iddle"
        if (self.vector == "email") | (self.vector == "*"):
            subject = "End of %s alert" % self.alert_type
            for addressee in addressees:
                send_mail(mail_config, addressee["mail"], subject, body)


class ModuleDisconnectedAlert(Alert):

    def __init__(self, module, alert_vector="*", level="critical", status="iddle", alert_type="module"):
        Alert.__init__(self, alert_vector, level, status, alert_type)
        self.module = module

    def check(self):
        try:
            self.module.get_hw_module()
        except DisconnectedModuleException as dme:
            if self.status == "iddle":
                self.triggering()
        else:
            if self.status == "triggered":
                self.resetting()
        return self.status

    def triggering(self, body=None):
        id = self.module.hwid
        body = "Module %s appears to be disconnected. Alerts related to this module will be suspended pending resolution." % id
        Alert.triggering(self, body)

    def resetting(self, body=None):
        id = self.module.hwid
        body = "Module %s has been reconnected. Resuming normal operation." % id
        Alert.resetting(self, body)


class SensorAlert(Alert):

    def __init__(self, sensor, alert_vector=None, level=None, direction=None, trigger=None, reset=None,
                 status="iddle", json_config=None):
        if json_config is not None:
            Alert.__init__(self, json_config["alert-vector"], json_config["level"], status, sensor.type)
            self.direction = json_config["direction"]
            self.trigger = json_config["trigger"]
            self.reset = json_config["reset"]
        else:
            Alert.__init__(self, alert_vector, level, status, sensor.type)
            self.direction = direction
            self.trigger = trigger
            self.reset = reset
        self.sensor = sensor

    def check(self):
        value = self.sensor.get_value()
        if self.status == "iddle":
            if self.direction == "over":
                if value > self.trigger:
                    self.triggering()
            elif self.direction == "below":
                if value < self.trigger:
                    self.triggering()
        elif self.status == "triggered":
            if self.direction == "over":
                if value < self.reset:
                    self.resetting()
            elif self.direction == "below":
                if value > self.reset:
                    self.resetting()
        return self.status

    def triggering(self, body=None):
        value = self.sensor.get_value()
        sensor_type = self.sensor.type
        body = "Module %s, %s sensor : %4.1f %s, expected %s %4.1f" % (
            self.sensor.module.hwid, sensor_type, value, self.sensor.get_unit(),
            "<" if self.direction == "over" else ">", self.trigger)
        Alert.triggering(self, body)

    def resetting(self, body=None):
        value = self.sensor.get_value()
        sensor_type = self.sensor.type
        body = "Module %s, %s sensor : back to normal (%4.1f %s)" % (
            self.sensor.module.hwid, sensor_type, value, self.sensor.get_unit())
        Alert.resetting(self, body)