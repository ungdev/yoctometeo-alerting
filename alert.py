from alerting import *

class Alert(object):

    def __init__(self, sensor, alert_vector=None, level=None, direction=None, trigger=None, reset=None, status="iddle", json_config=None):
        if json_config is not None:
            self.vector = json_config["alert-vector"]
            self.level = json_config["level"]
            self.direction = json_config["direction"]
            self.trigger = json_config["trigger"]
            self.reset = json_config["reset"]
        else:
            self.vector = alert_vector
            self.level = level
            self.direction = direction
            self.trigger = trigger
            self.reset = reset
        self.sensor = sensor
        self.status = status

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
                    self.reseting(value, config_mail, addressees)
            elif self.direction == "below":
                if value > self.reset:
                    self.reseting(value, config_mail, addressees)
        return self.status

    def triggering(self, value, config_mail, addressees):
        self.status = "triggered"
        sensor_type = self.sensor.type
        subject = "%s alert" % (sensor_type)
        body = "Module %s, %s sensor : %4.1f %s, expected %s %4.1f" % (
            self.sensor.module.hwid, sensor_type, value, self.sensor.get_unit(), "<" if self.direction == "over" else ">", self.trigger)
        if self.vector == "email":
            for addressee in addressees:
                send_mail(config_mail, addressee["mail"], subject, body)

    def reseting(self, value, config_mail, addressees):
        self.status = "iddle"
        sensor_type = self.sensor.type
        subject = "End of %s alert" % (sensor_type)
        body = "Module %s, %s sensor : back to normal (%4.1f %s)" % (
            self.sensor.module.hwid, sensor_type, value, self.sensor.get_unit())
        if self.vector == "email":
            for addressee in addressees:
                send_mail(config_mail, addressee["mail"], subject, body)