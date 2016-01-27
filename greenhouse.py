#!/usr/bin/env python

# @see https://github.com/winlinvip/SimpleSerial/blob/master/examples/CommandDefault/CommandDefault.ino
# @see https://github.com/winlinvip/SimpleSerial/blob/master/SimpleSerial.py
import SimpleSerial as sserial, os, time, datetime, json, sys

def trace(msg):
    print "%s: %s"%(datetime.datetime.now(), msg)

def startup_ping(ss, cmd):
    if cmd is None:
        trace("Ping Arduino")
        ss.write(sserial.ping())
        return
    
    if cmd.is_ping() == True:
        trace("Arduino reply: %s"%(cmd.str()))
        return
    trace("Arduino ignore %s"%(cmd.str()))
    
def startup_xtest(ss, cmd):
    if cmd is None:
        trace("X test Arduino")
        ss.write(sserial.notSupported(ord('X')))
        return
        
    if cmd.is_not_supported() == True:
        trace("Arduino reply: %s"%(cmd.str()))
        return
    trace("Arduino ignore %s"%(cmd.str()))
    
def detect(ss, cmd, temperature, humidity):
    if cmd is None:
        ss.write(sserial.queryTH())
        return (0, 0)
        
    if cmd.is_resp_th() == True:
        t,h = cmd.arg1()
        if t != temperature or h != humidity:
            trace("Arduino Detect: (%d*C %d%%) => (%d*C %d%%)"%(temperature, humidity, t, h))
        return (t, h)
    trace("Arduino ignore %s"%(cmd.str()))
    return (0, 0)
'''
State Diagram
init => detect => heat => detect
'''
def serve(ss, cmd, target, expire, trigger, ostate, state, temperature, humidity):
    if state == 'init':
        startup_ping(ss, cmd)
        return (state, 'xtest', 0, 0)
    
    if state == 'xtest':
        startup_xtest(ss, cmd)
        return (state, 'detect', 0, 0)
        
    if state == 'detect':
        (t, h) = detect(ss, cmd, temperature, humidity)
        if t == 0 and h == 0:
            return (state, 'detect', temperature, humidity)
        if t < target - trigger:
            return (state, 'heat', t, h)
        return (state, 'detect', t, h)
        
    if state == 'heat':
        if cmd is not None:
            if cmd.is_heater_closed() == True:
                trace("Arduino close the heater for warm enough.")
                return (state, 'detect', t, h)
            if cmd.is_heater_opened() == True:
                if ostate != state:
                    trace("Arduino open heater ok, %d*C %d%%, target is %d*C"%(t, h, target))
                return (state, 'heat', t, h)
        (t, h) = detect(ss, cmd, temperature, humidity)
        if t == 0 and h == 0:
            return (state, 'heat', temperature, humidity)
        if t < target:
            if ostate != state:
                trace("Notify Arduino to open heater.")
            ss.write(sserial.openHeater(target, expire))
            return (state, 'heat', t, h)
        trace("Warn enough, no need to heat, %d*C %d%%"%(t, h))
        return (state, 'detect', t, h)
        
    return (state, 'init', 0, 0)

if __name__ == "__main__":
    print "Greenhouse use RaspberryPi and Arduino\n" \
          "Copyright (c) 2015 winlin(winlin@vip.126.com)"
          
    # start heater when <=(target-trigger)
    # stop heater when overflow, texpire in seconds.
    (target, expire, trigger, ostate, state, temperature, humidity) = (21, 30, 2, 'init', 'init', 0, 0)
    
    ss = sserial.open("/dev/ttyUSB0", 115200)
    while True:
        try:
            cmd = None
            if state != 'init' and ss.available(3) == True:
                cmd = ss.read()
                
            if cmd is not None:
                if cmd.is_not_supported() == True:
                    trace("Ignore command %s"%(cmd.str()))
                elif cmd.is_unknown() == True:
                    trace("Ignore command %s"%(cmd.str()))
                    
            # input and output the states.
            (ostate, state, temperature, humidity) = serve(ss, cmd, target, expire, trigger, ostate, state, temperature, humidity)
        except int, ex:
            trace("Ignore error: %s"%(ex))
        time.sleep(3)
    sys.exit(0)
