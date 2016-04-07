from alerting import *


class Alert(object):

    def __init__(self, alert_vector=None, level=None, status="iddle", alert_type="generic"):
        self.vector = alert_vector
        self.level = level
        self.status = status
        self.alert_type = alert_type

    def check(self, config_mail, addressees):
        return self.status

    def triggering(self, config_mail, addressees, body=None):
        self.status = "triggered"
        if self.vector == "email":
            subject = "%s alert" % self.alert_type
            for addressee in addressees:
                send_mail(config_mail, addressee["mail"], subject, body)

    def resetting(self, config_mail, addressees, body=None):
        self.status = "iddle"
        if self.vector == "email":
            subject = "End of %s alert" % self.alert_type
            for addressee in addressees:
                send_mail(config_mail, addressee["mail"], subject, body)


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

    def check(self, config_mail, addressees):
        value = self.sensor.get_value()
        if self.status == "iddle":
            if self.direction == "over":
                if value > self.trigger:
                    self.triggering(value, config_mail, addressees)
            elif self.direction == "below":
                if value < self.trigger:
                    self.triggering(value, config_mail, addressees)
        elif self.status == "triggered":
            if self.direction == "over":
                if value < self.reset:
                    self.resetting(value, config_mail, addressees)
            elif self.direction == "below":
                if value > self.reset:
                    self.resetting(value, config_mail, addressees)
        return self.status

    def triggering(self, config_mail, addressees, body=None):
        value = self.sensor.get_value()
        sensor_type = self.sensor.type
        body = "Module %s, %s sensor : %4.1f %s, expected %s %4.1f" % (
            self.sensor.module.hwid, sensor_type, value, self.sensor.get_unit(),
            "<" if self.direction == "over" else ">", self.trigger)
        Alert.triggering(self, config_mail, addressees, body)

    def resetting(self, config_mail, addressees, body=None):
        value = self.sensor.get_value()
        sensor_type = self.sensor.type
        body = "Module %s, %s sensor : back to normal (%4.1f %s)" % (
            self.sensor.module.hwid, sensor_type, value, self.sensor.get_unit())
        Alert.resetting(self, config_mail, addressees, body)