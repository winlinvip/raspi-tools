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

Winlin 2016
