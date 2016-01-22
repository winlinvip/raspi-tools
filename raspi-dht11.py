#!/usr/bin/env python

import raspi_core, time, sys

if __name__ == "__main__":
    print "RaspberryPi DH11(temperature+humidity) application\n" \
        "Copyright (c) 2015 winlin(winlin@vip.126.com)"
    print "sample at GPIO18 for PI2"
    try:
        raspi_core.dht11_init()
        while True:
            data=raspi_core.dht11_sample(18) # GPIO18
            (humidity, humidity_point, temperature, temperature_point, check, expect) = raspi_core.dht11_parse(data)
            if check == expect:
                print "ok, temperature: %s *C, humidity: %s %%"%(temperature, humidity)
            else:
                print "fail, temperature: %s *C, humidity: %s %%, check: %s != %s"%(temperature, humidity, check, expect)
            time.sleep(2)
    finally:
        raspi_core.dht11_cleanup()
