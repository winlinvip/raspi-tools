#!/usr/bin/env python

########################################################################################
########################################################################################
########################################################################################
import SimpleSerial, os, time, datetime, json, sys

def trace(msg):
    print "%s: %s"%(datetime.datetime.now(), msg)

def loop():
    trace("======================================")
    trace("Arduino Ping")
    ss.write0(SimpleSerial.SSC_PING)
    (command, data) = ss.read()
    trace("Arduino Reply: %s"%(SimpleSerial.str(command)))
    
    trace("Mesure Teperature and Humidity")
    ss.write0(SimpleSerial.SSC_QUERY_TH)
    (command, arg0, arg1) = ss.read2()
    trace("Arduino Reply: %s %d*C %d%%"%(SimpleSerial.str(command), arg0, arg1))
    return

if __name__ == "__main__":
    print "Greenhouse use RaspberryPi and Arduino\n" \
          "Copyright (c) 2015 winlin(winlin@vip.126.com)"
    ss = SimpleSerial.open("/dev/ttyUSB0", 115200)
    while True:
        try:
            loop()
        except Exception, ex:
            trace("Ignore error: %s"%(ex))
        time.sleep(1)
    sys.exit(0)
