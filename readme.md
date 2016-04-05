# Yocto-meteo alerting

This program has been designed to alert administrators if environmental variables cross certain thresholds, using a Yocto-Meteo station device.

## Installation guide

First, install the Yoctopuce SDK for Python available in PyPi repositories :
```
pip install yoctopuce
```


## Configuration tips

Read me before changing conf file!!
Here is how to to write a good conf file for yoctometeo-alerting python script created by bijou

First get the serial name(YOCTOMETEOMK******) (or logical name) of all your modules, put it in the dict list "module" along with
their hosts (IP of corresponding virtual hub (if local: 127.0.0.1 or localhost))

Then in the "mesures" dict list specify unit !! only C(for celsius degre),mbar and %rh are handled at the moment !!
The resolution is not yet handled (coming soon)
Threshold is important only two means of communication are handled at the moment: mail and sms via free-mobile api, specify the level corresponding
to the type of alert (warning, error or critical) for logs, don't forget to specify the value of the threshold.
At the end fill the users dict list, user is just there to be used by you to find who is who in the config file. If the user doesn't have a
free-mobile account then just put a blank string "". sms won't be sent, a mail will replace it.

At the moment each time a threshold is exceeded corresping alert is sent. (working on it)