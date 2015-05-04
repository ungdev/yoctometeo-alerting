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


modules = []
captor_types = []
users_list = []
moduletest = "METEOMK1-3804F"

def die(msg):
    sys.exit(msg + '(check USB cable)')


class Mesure(object):
    """A class for mesures"""

    def __init__(self, unit, module_serial, threshold=None, host=None, logical_name=None, smtp=None,
                 mail=None):
        self.unit = unit
        self.value = None
        self.threshold = threshold
        self.physical_captor = None
        self.module_serial = module_serial
        self.physical_module = None
        self.host = host
        self.logical_name = logical_name
        self.smtp = smtp
        self.mail = mail
        self.type = ""
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
        errmsg = yocto_api.YRefParam()
        if yocto_api.YAPI.RegisterHub(self.host, errmsg) != yocto_api.YAPI.SUCCESS:
            sys.exit("init error" + errmsg.value)
        self.physical_module = yocto_api.YModule.FindModule(self.module_serial)


    """attribute module to mesure object"""

    def get_captor(self):
        # determine which type of captor (=> API) to use and associate the module
        errmsg = yocto_api.YRefParam()

        if self.unit == "%rh":
            if yocto_api.YAPI.RegisterHub(self.host, errmsg) != yocto_api.YAPI.SUCCESS:
                sys.exit("init error" + errmsg.value)
            yocto_api.YAPI.RegisterHub(self.host, errmsg)
            self.physical_captor = yocto_humidity.YHumidity.FindHumidity(self.module_serial + ".humidity")
            self.type = "humidity"

        elif self.unit == "mbar":
            if yocto_api.YAPI.RegisterHub(self.host, errmsg) != yocto_api.YAPI.SUCCESS:
                sys.exit("init error" + errmsg.value)

            self.physical_captor = yocto_pressure.YPressure.FindPressure(self.module_serial + ".pressure")
            self.type = "pressure"

        elif self.unit == "C":
            if yocto_api.YAPI.RegisterHub(self.host, errmsg) != yocto_api.YAPI.SUCCESS:
                sys.exit("init error" + errmsg.value)

            self.physical_captor = yocto_temperature.YTemperature.FindTemperature(self.module_serial + ".temperature")
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

    def __str__(self):
        test = str(self.host) + " " + str(self.physical_module) + " " + str(self.physical_captor) + " " + str(self.module_serial)
        return test

class User(object):
    def __init__(self, name, mail, free_url):
        self.name = name
        self.mail = mail
        self.free_url = free_url

    def send_mail(self, smtp, sender, subject, text):
        msg = MIMEText(text)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = self.mail
        s = smtplib.SMTP(smtp)
        s.sendmail(sender, self.mail, msg.as_string())
        s.quit()

    def send_sms(self, text, smtp=None, sender=None):
        if self.free_url != "":
            urllib.request.urlopen(self.free_url + text)
        else:
            self.send_mail(smtp, sender, "sms alert", text)

# real code now
#loading json config
with open('config.json') as data_file:
    data = json.load(data_file)
    sleep_time = data["configuration"]["general"]["sleep time"]
    for module in data["configuration"]["module"]:
        for element in module["mesures"]:
            captor_types.append(
                Mesure(element["unit"], module["name"], threshold=element["threshold"], host=module["host"],
                       logical_name=module["logical"], mail=module["mail"], smtp=module["smtp"]))
    for guy in data["configuration"]["users"]:
        users_list.append(User(guy["user"], guy["mail"], guy["free_url"]))


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
                user.send_mail(mesure.smtp, mesure.mail, "YoctoMeteo alert", "%s %s is at %s %s"
                               % (mesure.logical_name, mesure.type, str(mesure.value), mesure.unit))

        if mesure.value >= mesure.threshold["sms"]["value"]:
            mesure.log_sms()
            for user in users_list:
                user.send_sms("%s %s is at %s %s" % (mesure.logical_name, mesure.type, str(mesure.value), mesure.unit),
                              smtp=mesure.smtp, mail=mesure.mail)

    yocto_api.YAPI.Sleep(sleep_time)