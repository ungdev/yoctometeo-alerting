import json
import yocto_api
import yocto_humidity
import yocto_temperature
import yocto_pressure
import logging
import sys
import smtplib
import urllib.request
from email.mime.text import MIMEText

me = "yoctometeo@utt.fr"
modules = []
captor_types = []
users_list = []


def die(msg):
    sys.exit(msg + '(check USB cable)')


class Mesure(object):
    """A class for mesures"""

    def __init__(self, unit, module, captor=None, threshold=None, host=None, logical_name = None):
        self.captor = captor
        self.unit = unit
        self.value = None
        self.threshold = threshold
        self.physical_captor = None
        self.module = module
        self.physical_module = None
        self.Host = host
        self.type = ""
        self.logical_name = logical_name
        # creating loggers for the mesure using logging library
        s = self.unit
        self.logger = logging.getLogger(s)
        self.logger.setLevel(logging.INFO)
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)
        #Syslog usage
        #self.sh = logging.handlers.SysLogHandler(address = ('localhost',514), facility=19)
        #self.sh.setLevel(logging.INFO)
        #self.sh.setFormatter(self.formatter)
        #self.logger.addHandler(self.sh)

    def get_module(self):
        self.physical_module = yocto_api.YModule.get_module(self.physical_captor)

    """attribute module to mesure object"""

    def get_captor(self):
        # determine which type of captor (=> API) to use and associate the module
        if self.unit == "%rh":
            errmsg = yocto_api.YRefParam()
            if yocto_api.YAPI.SUCCESS != yocto_api.YAPI.RegisterHub(self.Host, errmsg):
                sys.exit("init error" + errmsg.value)

            self.physical_captor = yocto_humidity.YHumidity.FindHumidity(self.module + ".humidity")
            self.type = "humidity"

        elif self.unit == "mbar":
            errmsg = yocto_api.YRefParam()
            if yocto_api.YAPI.SUCCESS != yocto_api.YAPI.RegisterHub(self.Host, errmsg):
                sys.exit("init error" + errmsg.value)

            self.physical_captor = yocto_pressure.YPressure.FindPressure(self.module + ".pressure")
            self.type = "pressure"

        elif self.unit == "C":
            errmsg = yocto_api.YRefParam()
            if yocto_api.YAPI.SUCCESS != yocto_api.YAPI.RegisterHub(self.Host, errmsg):
                sys.exit("init error" + errmsg.value)

            self.physical_captor = yocto_temperature.YTemperature.FindTemperature(self.module + ".temperature")
            self.type = "temperature"

        else:
            self.logger.critical("units!!!!!")

    def get_value(self):
        self.value = self.physical_captor.get_currentValue()

    def log_sms(self):
        if self.threshold["sms"]["level"] == "warning":
            self.logger.warning("")
        elif self.threshold["sms"]["level"] == "error":
            self.logger.error("")
        elif self.threshold["sms"]["level"] == "critical":
            self.logger.critical("")
        else:
            self.logger.critical("")

    def log_mail(self):
        if self.threshold["mail"]["level"] == "warning":
            self.logger.warning("")
        elif self.threshold["mail"]["level"] == "error":
            self.logger.error("")
        elif self.threshold["mail"]["level"] == "critical":
            self.logger.critical("")
        else:
            self.logger.critical("")


class User(object):
    def __init__(self, name, mail, free_url):
        self.name = name
        self.mail = mail
        self.free_url = free_url

    def send_mail(self, subject, text):
        msg = MIMEText(text)
        msg['Subject'] = subject
        msg['From'] = me
        msg['To'] = self.mail
        s = smtplib.SMTP('smtp.utt.fr')
        s.sendmail(me, self.mail, msg.as_string())
        s.quit()

    def send_sms(self, text):
        if self.free_url != "":
            urllib.request.urlopen(self.free_url + text)
        else:
            self.send_mail("sms alert",text)

# real code now
#loading json config
with open('config.json') as data_file:
    data = json.load(data_file)
    for module in data["configuration"]["module"]:
        for element in data["configuration"]["mesures"]:
            captor_types.append(
                Mesure(element["unit"], module["name"], threshold=element["threshold"], host=module["host"],
                       logical_name=module["logical"]))
    for guy in data["configuration"]["users"]:
        users_list.append(User(guy["user"], guy["mail"], guy["Free_url"]))

for mesure in captor_types:
    mesure.get_captor()
    mesure.get_module()


while True:
    for mesure in captor_types:
        mesure.get_value()
        mesure.logger.info(str(mesure.value))
        if not mesure.physical_module.isOnline():
            mesure.logger.critical("deconnected %s, do something!!" % mesure.logical_name)
            for user in users_list:
                user.send_mail("YoctoMeteo alert", "deconnected %s!!" % mesure.logical_name)
                user.send_sms("YoctoMeteo deconnected %s" % mesure.logical_name)

        if mesure.value >= mesure.threshold["mail"]["value"]:
            mesure.log_mail()
            for user in users_list:
                user.send_mail("YoctoMeteo alert", "%s %s is at %s %s"
                               % (mesure.logical_name, mesure.type, str(mesure.value), mesure.unit))

        if mesure.value >= mesure.threshold["sms"]["value"]:
            mesure.log_sms()
            for user in users_list:
                user.send_sms("%s %s is at %s %s" % (mesure.logical_name, mesure.type, str(mesure.value), mesure.unit))

    yocto_api.YAPI.Sleep(60000)