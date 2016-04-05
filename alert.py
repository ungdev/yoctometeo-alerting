from alerting import *

class Alert(object):

    def __init__(self, sensor, alert_vector=None, level=None, direction=None, trigger=None, reset=None, json_config=None):
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
        self.status = "iddle"

    def check(self, config_mail, addressees):
        value = self.sensor.get_value()
        print("value : %f" % value)
        if self.status == "iddle":
            if self.direction == "over":
                if value > self.trigger:
                    self.triggering(value, config_mail, addressees)
            elif self.direction == "below":
                if value < self.trigger:
                    self.triggering(value, config_mail, addressees)
        elif self.status == "triggered":
            if self.direction == "over":
                if value < self.trigger:
                    self.reseting(value, config_mail, addressees)
            elif self.direction == "below":
                if value > self.trigger:
                    self.reseting(value, config_mail, addressees)

    def triggering(self, value, config_mail, addressees):
        self.status = "triggered"
        print("Debut alerte")
        if self.vector == "email":
            for addressee in addressees:
                send_mail(config_mail, addressee["mail"], "Alert", "Alert")

    def reseting(self, value, config_mail, addressees):
        self.status = "iddle"
        print("Fin alerte")
        if self.vector == "email":
            for addressee in addressees:
                send_mail(config_mail, addressee["mail"], "End Alert", "End Alert")