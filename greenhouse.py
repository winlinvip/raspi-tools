#!/usr/bin/env python

# @see https://github.com/winlinvip/SimpleSerial/blob/master/examples/CommandDefault/CommandDefault.ino
# @see https://github.com/winlinvip/SimpleSerial/blob/master/SimpleSerial.py
import SimpleSerial, os, time, datetime, json, sys

def trace(msg):
    print "%s: %s"%(datetime.datetime.now(), msg)

def startup(ss):
    trace("Ping Arduino")
    ss.write0(SimpleSerial.SSC_PING)
    while ss.available() == False:
        time.sleep(0.1)
    (command, data) = ss.read()
    trace("Arduino Reply: %s"%(SimpleSerial.str(command)))
    
    trace("X Test Arduino")
    ss.write0('X')
    while ss.available() == False:
        time.sleep(0.1)
    (command, data) = ss.read()
    trace("Arduino Reply: %s"%(SimpleSerial.str(command)))
    
def loop(ss, target, expire, trigger, overflow):
    trace("======================================")
    trace("Mesure Teperature and Humidity")
    ss.write0(SimpleSerial.SSC_QUERY_TH)
    (command, temperature, humidity) = ss.read2()
    if command != SimpleSerial.SSC_RESP_TH:
        raise Exception("Invalid Response.")
    trace("Arduino Reply: %s %d*C %d%%"%(SimpleSerial.str(command), temperature, humidity))
    
    if temperature < target - trigger:
        trace("Too cold, open the heater util %d*C"%(target))
        ss.write2(SimpleSerial.SSC_OPEN_HEATER, target, expire)
        command = ss.read0()
        if command != SimpleSerial.SSC_HEATER_OPENED:
            raise Exception("Invalid Response.")
        trace("Arduino Reply: %s"%(SimpleSerial.str(command)))
        trigger = 0
        
    overflow = False
    if temperature >= target:
        overflow = True
        
    return (trigger, overflow)

if __name__ == "__main__":
    print "Greenhouse use RaspberryPi and Arduino\n" \
          "Copyright (c) 2015 winlin(winlin@vip.126.com)"
          
    # start heater when <=(target-trigger)
    # stop heater when overflow
    (target, expire, trigger, overflow) = (21, 30, 2, False)
    
    ss = SimpleSerial.open("/dev/ttyUSB0", 115200)
    ok = False
    while True:
        try:
            if ok == False:
                startup(ss)
            ok = True
        
            (trigger, overflow) = loop(ss, target, expire, trigger, overflow)
            if overflow == True:
                trigger = 2
        except Exception, ex:
            trace("Ignore error: %s"%(ex))
            time.sleep(1)
            continue
        time.sleep(3)
    sys.exit(0)
