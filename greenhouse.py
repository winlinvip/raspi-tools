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
    
    if sserial.is_ping(cmd) == True:
        trace("Arduino reply: %s"%(cmd.str()))
        return
    trace("Arduino ignore %s"%(cmd.str()))
    
def startup_xtest(ss, cmd):
    if cmd is None:
        trace("X test Arduino")
        ss.write(sserial.notSupported(ord('X')))
        return
        
    if sserial.is_not_supported(cmd) == True:
        trace("Arduino reply: %s"%(cmd.str()))
        return
    trace("Arduino ignore %s"%(cmd.str()))
    
def detect(ss, cmd, temperature, humidity):
    if cmd is None:
        ss.write(sserial.queryTH())
        return (0, 0)
        
    if sserial.is_resp_th(cmd) == True:
        t,h = cmd.arg1()
        if t != temperature or h != humidity:
            trace("Arduino Detect: (%d*C %d%%) => (%d*C %d%%)"%(temperature, humidity, t, h))
        return (t, h)
    trace("Arduino ignore %s"%(cmd.str()))
    return (0, 0)
'''
State Diagram
init => detect => work => detect
'''
def serve(ss, cmd, tt, te, tr, ht, he, hr, os, s, ot, oh):
    if s == 'init':
        startup_ping(ss, cmd)
        return (s, 'xtest', 0, 0)
    
    if s == 'xtest':
        startup_xtest(ss, cmd)
        return (s, 'detect', 0, 0)
        
    if s == 'detect':
        (t, h) = detect(ss, cmd, ot, oh)
        if t == 0 and h == 0:
            return (s, 'detect', ot, oh)
        if t < tt - tr:
            return (s, 'heat', t, h)
        if h >= ht - hr:
            return (s, 'fan', t, h)
        return (s, 'detect', t, h)
        
    if s == 'heat':
        if cmd is not None:
            if sserial.is_heater_closed(cmd) == True:
                trace("Arduino close the heater for warm enough.")
                return (s, 'detect', ot, oh)
            if sserial.is_heater_opened(cmd) == True:
                if os != s:
                    trace("Arduino open heater ok, %d*C %d%%, target is %d*C"%(t, h, tt))
                return (s, 'heat', ot, oh)
        (t, h) = detect(ss, cmd, ot, oh)
        if t == 0 and h == 0:
            return (s, 'heat', ot, oh)
        if t < tt:
            if os != s:
                trace("Notify Arduino to open heater.")
            ss.write(sserial.openHeater(tt, te))
            return (s, 'heat', t, h)
        trace("Warm enough, no need to heat, %d*C %d%%"%(t, h))
        return (s, 'detect', t, h)
        
    if s == 'fan':
        if cmd is not None:
            if sserial.is_fan_closed(cmd) == True:
                trace("Arduino close the fan for humidity ok.")
                return (s, 'detect', t, h)
            if sserial.is_fan_opened(cmd) == True:
                if os != s:
                    trace("Arduino open fan ok, %d*C %d%%, target is %d%%"%(t, h, ht))
                return (s, 'fan', t, h)
        (t, h) = detect(ss, cmd, ot, oh)
        if t == 0 and h == 0:
            return (s, 'fan', ot, oh)
        if t < tt:
            if os != s:
                trace("Notify Arduino to open fan.")
            ss.write(sserial.openFan(ht, he))
            return (s, 'fan', t, h)
        trace("Humidity ok, no need to fan, %d*C %d%%"%(t, h))
        return (s, 'detect', t, h)
        
    return (s, 'init', 0, 0)

if __name__ == "__main__":
    print "Greenhouse use RaspberryPi and Arduino\n" \
          "Copyright (c) 2015 winlin(winlin@vip.126.com)"
          
    # start heater when <=(target-trigger)
    # stop heater when overflow, texpire in seconds.
    (tt, te, tr, ht, he, hr, os, s, t, h) = (
        21, # tt, temperature target
        30, # te, temperature expire
        2, # tr, temperature trigger
        50, # ht, humidity target
        30, # he, humidity expire
        10, # hr, humidity trigger
        'init', # os, original state
        'init', # s, state
        0, # t, temperature
        0 # h, humifity
    )
    
    ss = sserial.open("/dev/ttyUSB0", 115200)
    while True:
        try:
            cmd = None
            if s != 'init' and ss.available(3) == True:
                cmd = ss.read()
                
            if cmd is not None:
                if sserial.is_not_supported(cmd) == True:
                    trace("Ignore command %s"%(cmd.str()))
                elif sserial.is_unknown(cmd) == True:
                    trace("Ignore command %s"%(cmd.str()))
                    
            # input and output the states.
            (os, s, t, h) = serve(ss, cmd, tt, te, tr, ht, he, hr, os, s, t, h)
        except int, ex:
            trace("Ignore error: %s"%(ex))
        time.sleep(3)
    sys.exit(0)
