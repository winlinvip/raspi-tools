# raspi-tools

Some tools for RaspberryPi

## RaspiWlan

The tool raspi-wlan.py used to connect to multiple Wifi automatically.
```
Usage: raspi-wlan.py <ssid0> <passwd0> [<ssidN> <passwdN>]
     ssid        the ssid of AP or other wireless device.
     passwd      the psk for AP which use WPA-PSK or WPA2-PSk.
For example:
     raspi-wlan.py MyApSsid PlainPasswd
     raspi-wlan.py MyApSsid0 PlainPasswd0 MyApSsidN PlainPasswdN
     raspi-wlan.py 'My AP SSID' 'Plain Passwd'
```

## RaspiDH11

The tool raspi-dh11.py used to read data from DH11, the temperature and humidity sensor.
```
sudo python raspi-dh11.py
```

## RaspiPL2302

The tool raspi-pl2302.py used to communicate with Arduino over PL2303(USB2SerialTTL).
```
sudo python raspi-pl2303.py
```

Please read [RaspberryPi+Arduino](http://blog.csdn.net/win_lin/article/details/50545678).

## Greenhouse

The tool greenhouse.py used to control the temperature and humidity,
with an [android app](https://github.com/winlinvip/raspi-tools/tree/master/android).

Please read [Greenhouse control](http://blog.csdn.net/win_lin/article/details/50572308).

Winlin 2016
