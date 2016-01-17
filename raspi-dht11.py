#!/usr/bin/env python

import RPi.GPIO as GPIO, time, sys

def sample(channel):
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(channel, GPIO.OUT)
  GPIO.output(channel, GPIO.LOW)
  time.sleep(0.02)
  GPIO.output(channel, GPIO.HIGH)
  GPIO.setup(channel, GPIO.IN)

  while GPIO.input(channel) == GPIO.LOW:
    continue
  while GPIO.input(channel) == GPIO.HIGH:
    continue

  data = []
  for i in range(40):
    while GPIO.input(channel) == GPIO.LOW:
      continue
    for j in range(100):
      if GPIO.input(channel) != GPIO.HIGH:
          break
    if j < 8:
      data.append(0)
    else:
      data.append(1)

  return data

def fn(x):
  v = 0
  for i in range(8):
    v += x[i] << (7-i)
  return v

print "RaspberryPi DH11(temperature+humidity) application\n" \
    "Copyright (c) 2015 winlin(winlin@vip.126.com)"

try:
  print "sample at GPIO18 for PI2"
  data=sample(18) # GPIO18
finally:
  GPIO.cleanup()

humidity = fn(data[0:8])
humidity_point = fn(data[8:16])
temperature = fn(data[16:24])
temperature_point = fn(data[24:32])
check = fn(data[32:40])
expect = humidity + humidity_point + temperature + temperature_point

#print "got data: %s"%(data)
if check == expect:
  print "ok, temperature: %s *C, humidity: %s %%"%(temperature, humidity) 
  sys.exit(0)
else:
  print "fail, temperature: %s *C, humidity: %s %%, check: %s != %s"%(temperature, humidity, check, expect)
  sys.exit(-1)
