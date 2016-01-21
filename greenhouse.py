#!/usr/bin/env python

########################################################################################
########################################################################################
########################################################################################
import serial

def pl2303_open(device="/dev/ttyUSB0"):
    return serial.Serial(device, 115200)

########################################################################################
########################################################################################
########################################################################################
import os, time, datetime, json

def trace(msg):
    print "%s: %s"%(datetime.datetime.now(), msg)

def loop():
    with os.popen("python raspi-dht11.py 2>/dev/stdout 1>/dev/null") as f:
        ret = f.read().strip()
    if len(ret) == 0:
        trace("ignore failed to fetch temperature and humidity.")
        time.sleep(3)
        return

    obj = json.loads(ret)
    temperature = obj["t"]
    humidity = obj["h"]
    trace("ok, temperature: %s *C, humidity: %s %%"%(temperature, humidity))

    target_temperature = 19
    if temperature < target_temperature:
        trace("oh, it's too cold, let's open the heater to keep %s *C"%(target_temperature));
        arduino.write('H')
    return

def read_artuino(arduino):
    try:
        for i in range(5):
            c = arduino.read(1)
            if c == 'H':
                trace("arduino open the heater: %s(%s)"%(c, len(c)))
            if c == 'C':
                trace("arduino close the heater %s(%s)"%(c, len(c)))
    except Exception:
        pass

if __name__ == "__main__":
    print "Greenhouse use RaspberryPi and Arduino\n" \
          "Copyright (c) 2015 winlin(winlin@vip.126.com)"

    arduino = pl2303_open()
    while True:
        try:
            trace("let's look into the greenhouse.")
            loop()
        except Exception,ex:
            trace("ignore except: %s"%ex)
            time.sleep(5)
        read_artuino(arduino)

