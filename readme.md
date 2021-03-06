# Yocto-meteo alerting

This program has been designed to alert administrators if environmental variables cross certain thresholds, using a Yocto-Meteo station device.

## Installation guide

First, install the Yoctopuce SDK for Python available in PyPi repositories :
```
pip install yoctopuce
```

Depending on your needs, you might want to install the following dependency in order to send log messages to a Graylog server :
```
pip install graypy
```

Clone the repository in a target folder, e.g. /opt, and give ownership to the user whose identity will be used to run the program.

## Running

### Direct launch
You can launch it by hand, in which case execute a Python3 interpreter targeting `main.py`.

### Systemd service
A skeleton of systemd service descriptor is provided under `yoctometeo-alerting.service`.
You might want to edit the following parameters to suit your install :
- User/Group : must match the aforementionned
- WorkingDirectory/ExecStart : depending on the program path
- StandardOutput/StandardOutput : where the outputs should be directed to, defaults to syslog


## Configuration

The configuration is stored in a JSON-syntax file `config.json`. A sample skeleton may be found in the repository : `sample-config.json`.
This section will briefly summarize the available options.

### sleep-time

The program will automatically perform a check sequence after the expiry of the delay since the last sequence completed.
To be expressed in milliseconds.

### mail-server

This section defines the parameters required to send alerts through e-mails.
```
"mail-server": {
    "host": "smtp.example.tld",
    "port": "465",
    "tls": "yes", // whether using TLS encryption
    "username": "ano.nymous", //leave blank if no authentication is required
    "password": "Azerty",
    "from-address": "yocto@example.tld" // Originating e-mail address, will appear to the recipient
}
```

### log-server

This section defines the parameters required to send alerts to a Graylog server. Optional.
```
"log-server": {
    "host": "log.example.tld",
    "port": 12201
}
```

### addressees

This section defines the people who will receive the alerts, with their contact infos.
It is an array of objects defined as follow :
```
"addressees": [
    {
      "name": "****", // Name of the addressee
      "mail": "**@***", // Email address
      "phone-number": "+336XXXXXXXXX" // Phone number
    }
]
```

### modules

This section defines the YoctoMeteo devices used by the program. Here are the different components of this section.

#### Module object

These objects define a module, as a hardware piece of equipment, with the following parameters :
- The hardware ID, which can be found using YoctoPuce SDKs or demo softwares, it is used to uniquely identify a module.
- The host identifier
    - `[hostname]:[port]` for VirtualHub intallations
    - `usb` for direct access through USB port (specific instructions to be found thereafter)
- An array of sensor objects, whose description can be found in the next section

```
{
  "hardware-id": "****",
  "host": "***",
  "sensors": []
}
```

#### Sensor object

These objects define a sensor, meaning an environmental variable (not necessarily a separate physical equipment).
One must be defined for each variable to be monitored, for each module, with the following parameters :
- The sensor type, to be chosed among the following :
    - temperature
    - humidity
    - pressure
- An array of alert objects, whose description can be found in the next section

```
{
    "type": "temperature|humidity|pressure",
    "alerts": []
}
```

#### Alert object

These objects define an alert, meaning a threshold which, if crossed, will trigger an alerting action.
Sensors can handle multiple alerts, for instance lowlevel e-mail alert for a small overheating, and a hurry SMS alert for a fire-like problem.
It must be defined with the following parameters :
- An identifier to remain unique among the program instance
- The vector used to transmit the alert (if a log server has been defined, each and every alert will be forwarded to it), currently supported :
    - E-mail
    - SMS (to be implemented depending on your platform)
- The alert level (used for the logging system), to be chosed among the following, by increasing degree of harm :
    - warning
    - error
    - critical
- The variable can pass **below** or **over** the threshold
- The trigger threshold : crossing it in the aforementioned direction will trigger the alert
- The reset threshold : crossing it in the direction opposite to the aforementioned will reset the alert

The interest of this double-threshold mechanism is to introduce a hysteresis,
thus avoiding endless alert/end-of-alert messages when the value bounces arround the threshold.

```
{
    "alert-id": 1,
    "alert-vector": "email",
    "level": "warning",
    "direction": "over",
    "trigger": 25,
    "reset": 22
}
```

## Direct USB connection

In order for USB access to work for users other than root, you should copy the file
 `51-yoctopuce_all.rules` in the `/etc/udev/rules.d` directory.