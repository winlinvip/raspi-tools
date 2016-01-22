#!/usr/bin/env python

# depends on rpi.gpio, which can be install by:
#      sudo apt-get install python-rpi.gpio
import RPi.GPIO as GPIO
import time

def bits2byte(x):
    v = 0
    for i in range(8):
        v += x[i] << (7-i)
    return v

def dht11_init():
    GPIO.setmode(GPIO.BCM)

def dht11_sample(channel):
    # notify DHT11 to start: 
    #       1. PULL LOW 20ms.
    #       2. PULL HIGH 20-40us.
    #       3. SET TO INPUT.
    GPIO.setup(channel, GPIO.OUT)
    # PULL LOW 20ms.
    GPIO.output(channel, GPIO.LOW)
    time.sleep(0.02)
    # PULL HIGH 20-40us.
    GPIO.output(channel, GPIO.HIGH)
    # SET TO INPUT.
    GPIO.setup(channel, GPIO.IN)
    
    # DHT11 starting:
    #       1. PULL LOW 80us
    #       2. PULL HIGH 80us
    while GPIO.input(channel) == GPIO.LOW:
        continue
    while GPIO.input(channel) == GPIO.HIGH:
        continue
    
    # DHT11 data transmite:
    #       1. 1bit start, PULL LOW 50us
    #       2. PULL HIGH 26-28us, bit(0)
    #       3. PULL HIGH 70us, bit(1)
    data = []
    # how many directives to spent about 20us.
    DHT11_DIRECTIVE_20US=8
    for i in range(0, 40, 1):
        while GPIO.input(channel) == GPIO.LOW:
            continue
        for k in range(0, 100, 1):
            if GPIO.input(channel) != GPIO.HIGH:
                break
        #print 'got bit i=%s k=%s'%(i, k)
        if k < DHT11_DIRECTIVE_20US:
            data.append(0)
        else:
            data.append(1)
    # DHT11 EOF:
    #       1. PULL LOW 50us.
    while GPIO.input(channel) == GPIO.LOW:
        continue
    return data

def dht11_cleanup():
    GPIO.cleanup()

def dht11_parse(data):
    humidity = bits2byte(data[0:8])
    humidity_point = bits2byte(data[8:16])
    temperature = bits2byte(data[16:24])
    temperature_point = bits2byte(data[24:32])
    check = bits2byte(data[32:40])
    expect = humidity + humidity_point + temperature + temperature_point
    return (humidity, humidity_point, temperature, temperature_point, check, expect)