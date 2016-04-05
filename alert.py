

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

