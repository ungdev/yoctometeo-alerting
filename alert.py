

class Alert(object):

    def __init__(self, sensor, alert_vector=None, level=None, trigger=None, reset=None, json_config=None):
        if json_config is not None:
            self.vector = json_config["alert-vector"]
            self.level = json_config["level"]
            self.trigger = json_config["trigger"]
            self.reset = json_config["reset"]
            self.sensor = sensor
        else:
            self.vector = alert_vector
            self.level = level
            self.trigger = trigger
            self.reset = reset
            self.sensor = sensor