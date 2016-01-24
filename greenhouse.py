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
    trace("Arduino reply: %s"%(SimpleSerial.str(command)))
    
    trace("X test Arduino")
    ss.write0('X')
    while ss.available() == False:
        time.sleep(0.1)
    (command, data) = ss.read()
    trace("Arduino reply: %s"%(SimpleSerial.str(command)))
    
def detect(ss, temperature, humidity):
    while True:
        ss.write0(SimpleSerial.SSC_QUERY_TH)
        for i in range(10):
            if ss.available() == False:
                time.sleep(0.1)
            else:
                break
                
        (command, t, h) = ss.read2()
        if command == SimpleSerial.SSC_HEATER_CLOSED:
            trace("Arduino close the heater for warm enough.")
            continue
        if command != SimpleSerial.SSC_RESP_TH:
            raise Exception("Invalid QueryTH response: %s"%(SimpleSerial.str(command)))
        if t != temperature or h != humidity:
            trace("Arduino Detect: (%d*C %d%%) => (%d*C %d%%)"%(temperature, humidity, t, h))
        break
    return (t, h)
    
'''
State Diagram
init => detect => heat => detect
'''
def serve(ss, target, expire, trigger, ostate, state, temperature, humidity):
    if state == 'init':
        startup(ss)
        return (state, 'detect', 0, 0)
        
    if state == 'detect':
        (t, h) = detect(ss, temperature, humidity)
        if t < target - trigger:
            return (state, 'heat', t, h)
        return (state, 'detect', t, h)
        
    if state == 'heat':
        (t, h) = detect(ss, temperature, humidity)
        if t < target:
            if ostate != state:
                trace("Notify Arduino to open heater.")
                
            ss.write2(SimpleSerial.SSC_OPEN_HEATER, target, expire)
            for i in range(10):
                if ss.available() == False:
                    time.sleep(0.1)
                else:
                    break
            command = ss.read0()
            
            if command == SimpleSerial.SSC_HEATER_CLOSED:
                trace("Arduino close the heater for warm enough.")
                return (state, 'detect', t, h)
            if command != SimpleSerial.SSC_HEATER_OPENED:
                raise Exception("Invalid OpenHeater response: %s."%(SimpleSerial.str(command)))
                
            if ostate != state:
                trace("Arduino open heater ok, %d*C %d%%, target is %d*C"%(t, h, target))
            return (state, 'heat', t, h)
        else:
            trace("Warn enough, no need to heat, %d*C %d%%"%(t, h));
            return (state, 'detect', t, h)
        
    return (state, 'init', 0, 0)

if __name__ == "__main__":
    print "Greenhouse use RaspberryPi and Arduino\n" \
          "Copyright (c) 2015 winlin(winlin@vip.126.com)"
          
    # start heater when <=(target-trigger)
    # stop heater when overflow, texpire in seconds.
    (target, expire, trigger, ostate, state, temperature, humidity) = (21, 30, 2, 'init', 'init', 0, 0)
    
    ss = SimpleSerial.open("/dev/ttyUSB0", 115200)
    while True:
        try:
            # input and output the states.
            (ostate, state, temperature, humidity) = serve(ss, target, expire, trigger, ostate, state, temperature, humidity)
        except Exception, ex:
            trace("Ignore error: %s"%(ex))
        time.sleep(3)
    sys.exit(0)
