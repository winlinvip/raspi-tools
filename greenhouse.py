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
import raspi_core
import os, time, datetime, json

def trace(msg):
    print "%s: %s"%(datetime.datetime.now(), msg)

def loop(channel, target, gate):
    data=raspi_core.dht11_sample(channel)
    (humidity, humidity_point, temperature, temperature_point, check, expect) = raspi_core.dht11_parse(data)
    if check != expect:
        raise Exception("invalid temperature.")
    trace("ok, temperature: %s *C, humidity: %s %%"%(temperature, humidity))
    
    diff = target - temperature
    if diff > gate:
        trace("oh, it's too cold, let's open the heater to keep %s *C"%(target));
        arduino.write('H')
        return True
    return False

def read_artuino(arduino, words):
    try:
        for i in range(words):
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
    try:
        raspi_core.dht11_init()
        gate = 2
        while True:
            try:
                trace("let's look into the greenhouse.")
                if loop(18, 21, gate): # GPIO18
                    gate = 0 # set trigger to 0, to ensure the temperature reach target.
                else:
                    gate = 2 # when reach target, trigger only when diff is large.
            except Exception,ex:
                trace("ignore except: %s"%ex)
            finally:
                sleep_seconds=2
                # the arduino will atleast print a char per second.
                read_artuino(arduino, sleep_seconds)
                time.sleep(sleep_seconds)
    finally:
        raspi_core.dht11_cleanup()

