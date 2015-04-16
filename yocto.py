import json, yocto_api, yocto_humidity, yocto_temperature, yocto_pressure, logging, sys

modules =[]
captor_types = []

def die(msg):
    sys.exit(msg+' (check USB cable)')

class Mesure(object):
    """A class for mesures"""
    def __init__(self, unit, captor="not found yet", threshold=None, value=None,Captor=None, Module = None):
        self.captor = captor
        self.unit = unit
        self.value = value
        self.threshold = threshold
        self.Captor = Captor
        self.Module = Module
        #creating loggers for the mesure using logging
        s = self.captor + " " + self.unit
        self.logger = logging.getLogger(s)
        self.logger.setLevel(logging.DEBUG)
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)

    def get_module(self):
        self.Module = yocto_api.YModule.get_module(self.Captor)

    """attribute module to mesure object"""
    def get_captor(self):
        #determine which type of captor (=> API) to use and associate the module
        if self.unit == "%rh":
            errmsg =  yocto_api.YRefParam()
            if yocto_api.YAPI.RegisterHub("127.0.0.1",errmsg)  != yocto_api.YAPI.SUCCESS:
                 sys.exit("init error"+errmsg.value)

            self.Captor = yocto_humidity.YHumidity.FindHumidity(self.captor)

        elif self.unit == "mbar":
            errmsg =  yocto_api.YRefParam()
            if yocto_api.YAPI.RegisterHub("127.0.0.1",errmsg)  != yocto_api.YAPI.SUCCESS:
                 sys.exit("init error"+errmsg.value)

            self.Captor = yocto_pressure.YPressure.FindPressure(self.captor)

        elif self.unit == "C":
            errmsg =  yocto_api.YRefParam()
            if yocto_api.YAPI.RegisterHub("127.0.0.1",errmsg)  != yocto_api.YAPI.SUCCESS:
                 sys.exit("init error"+errmsg.value)

            self.Captor = yocto_temperature.YTemperature.FindTemperature(self.captor)

        else :
            self.logger.critical("units!!!!!")

    def get_value(self):
        if self.unit == "%rh":
            self.value = self.Captor.get_currentValue()
        elif self.unit == "mbar":
            self.value = self.Captor.get_currentValue()
        elif self.unit == "C":
            self.value = self.Captor.get_currentValue()
        else:
            self.logger.critical("units!!!!!")





    """sends mail to people"""
  #  def send_mail(self, user):

#class User(object):
#    def __init__(self, name, mail, number):
#        self.name = name
#        self.mail = mail
#        self.number = number

#real code now
#loading json config
with open('config.json') as data_file:
    data = json.load(data_file)
    for element in data["configuration"]["mesures"]:
        captor_types.append(Mesure(element["unit"], element["captor"], element["threshold"]))

for mesure in captor_types:
    mesure.get_captor()
    mesure.get_module()
    mesure.get_value()

while True:
    for mesure in captor_types:
        mesure.get_value()
        mesure.logger.debug(str(mesure.value))
        if not mesure.Module.isOnline():
            mesure.logger.critical("je suis déconnecté, faites quelque chose!!")
            mesure.alert_mail("déconnexion")
            mesure.alert_sms("déconnexion")
        if mesure.value >= mesure.threshold["mail"][1]:
            # appeler la bonne méthode
            #    mesure.alert_+trigger()
            mesure.logger.warning("attention")
        if mesure.value >= mesure.threshold["sms"][1]:
            mesure.logger.critical("Wowowowowow")
    yocto_api.YAPI.Sleep(60000)