#!/usr/bin/env python

import serial

print 'RaspberryPi PL2303(USB2SerialTTL) communicate.'
print "Copyright (c) 2015 winlin(winlin@vip.126.com)"

f = serial.Serial('/dev/ttyUSB0', 115200)

while True:
    v = "Hello, Arduino, this is RaspberryPi 2.0~"
    f.write(v)
    print 'PI: %s'%(v)

    r = ''
    for i in v:
        r += f.read()
        print '.',
    print ''
    print 'Arduino: %s'%(r)
