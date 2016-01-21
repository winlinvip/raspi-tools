#!/usr/bin/env python

import serial

def pl2303_open(device="/dev/ttyUSB0"):
    return serial.Serial(device, 115200)

if __name__ == "__main__":
    print 'RaspberryPi communicate with Aruduino over PL2303(USB2SerialTTL)'
    print "Copyright (c) 2015 winlin(winlin@vip.126.com)"
    print "Please read http://blog.csdn.net/win_lin/article/details/50545678"

    pl2303 = pl2303_open()

    while True:
        v = "Hello, Arduino, this is RaspberryPi 2.0~"
        pl2303.write(v)
        print 'PI: %s'%(v)

        r = ''
        for i in v:
            r += pl2303.read()
            print '.',
        print ''
        print 'Arduino: %s'%(r)
