#!/usr/bin/env python

# @see https://github.com/winlinvip/SimpleSerial/blob/master/examples/CommandDefault/CommandDefault.ino
# @see https://github.com/winlinvip/SimpleSerial/blob/master/SimpleSerial.py
import SimpleSerial as sserial, os, time, datetime, json, sys, urllib2

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
def serve(ss, cmd, tt, te, tr, ht, he, hr, s, ot, oh):
    # process the events from Arduino.
    if cmd is not None:
        if sserial.is_not_supported(cmd) == True:
            trace("Ignore command %s"%(cmd.str()))
            return (s, ot, oh)
        elif sserial.is_unknown(cmd) == True:
            trace("Ignore command %s"%(cmd.str()))
            return (s, ot, oh)
        elif sserial.is_heater_closed(cmd) == True:
            trace("Arduino close the heater for warm enough.")
            return ('detect', ot, oh)
        if sserial.is_heater_opened(cmd) == True:
            trace("Arduino open heater ok, %d*C %d%%, target is %d*C"%(ot, oh, tt))
            return (s, ot, oh)
        if sserial.is_fan_closed(cmd) == True:
            trace("Arduino close the fan for humidity ok.")
            return ('detect', ot, oh)
        if sserial.is_fan_opened(cmd) == True:
            trace("Arduino open fan ok, %d*C %d%%, target is %d%%"%(ot, oh, ht))
            return (s, ot, oh)
            
    # use state machine to drive new event.
    if s == 'init':
        startup_ping(ss, cmd)
        return ('xtest', 0, 0)
    
    if s == 'xtest':
        startup_xtest(ss, cmd)
        return ('detect', 0, 0)
        
    if s == 'detect':
        (t, h) = detect(ss, cmd, ot, oh)
        if t == 0 and h == 0:
            return ('detect', ot, oh)
        if t < tt - tr:
            return ('heat', t, h)
        if h >= ht + hr:
            return ('fan', t, h)
        return ('detect', t, h)
        
    if s == 'heat':
        (t, h) = detect(ss, cmd, ot, oh)
        if t == 0 and h == 0:
            return ('heat', ot, oh)
        if t < tt:
            #trace("Notify Arduino to open heater.")
            ss.write(sserial.openHeater(tt, te))
            return ('heat', t, h)
        trace("Warm enough, no need to heat, %d*C %d%%"%(t, h))
        return ('detect', t, h)
        
    if s == 'fan':
        (t, h) = detect(ss, cmd, ot, oh)
        if t == 0 and h == 0:
            return ('fan', ot, oh)
        if h >= ht:
            #trace("Notify Arduino to open fan.")
            ss.write(sserial.openFan(ht, he))
            return ('fan', t, h)
        trace("Humidity ok, no need to fan, %d*C %d%%"%(t, h))
        return ('detect', t, h)
        
    return ('init', 0, 0)
    
def report(id, obj):
    data = json.dumps({
        "id": id,
        "data": obj
    })
    urllib2.urlopen("http://127.0.0.1:2015/api/v1/htbt/devices", data).close()

if __name__ == "__main__":
    print "Greenhouse use RaspberryPi and Arduino\n" \
          "Copyright (c) 2015 winlin(winlin@vip.126.com)"
          
    # start heater when <=(target-trigger)
    # stop heater when overflow, texpire in seconds.
    (tt, te, tr, ht, he, hr, s, t, h) = (
        21, # tt, temperature target
        30, # te, temperature expire
        2, # tr, temperature trigger
        75, # ht, humidity target
        30, # he, humidity expire
        15, # hr, humidity trigger
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
                if sserial.is_resp_th2(cmd):
                    t2, h2 = cmd.arg1()
                    report("space",  { "temperature": t2, "humidity": h2})
                    continue
                    
            # input and output the states.
            (s, t, h) = serve(ss, cmd, tt, te, tr, ht, he, hr, s, t, h)
            
            # remote to local oryx server, which heatbeat to ossrs.
            report("greenhouse",  { "temperature": t, "humidity": h, "state": s })
        except Exception, ex:
            trace("Ignore error: %s"%(ex))
        time.sleep(3)
    sys.exit(0)
