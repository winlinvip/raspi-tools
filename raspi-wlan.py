#!/usr/bin/env python

import os,sys,time

print "RaspberryPi wlan auto connecter\n" \
    "Copyright (c) 2015 winlin(winlin@vip.126.com)"

if len(sys.argv) <= 2:
    print "Usage: %s <ssid0> <passwd0> [<ssidN> <passwdN>]\n" \
          "     ssid        the ssid of AP or other wireless device.\n" \
          "     passwd      the psk for AP which use WPA-PSK or WPA2-PSk.\n" \
          "For example:\n" \
          "     %s MyApSsid PlainPasswd\n" \
          "     %s MyApSsid0 PlainPasswd0 MyApSsidN PlainPasswdN\n" \
          "     %s 'My AP SSID' 'Plain Passwd'"%(
              sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0]
          )
    sys.exit(-1)

if (len(sys.argv) % 2) == 0:
    print "Error: please specifies the passwd for ssid %s."%(sys.argv[len(sys.argv) - 1])
    sys.exit(-1)

class ApConfig:
    def __init__(self, ssid, psk):
        self.ssid = str(ssid).strip('"')
        self.psk = psk

class DeviceConfig:
    def __init__(self, ifname):
        self.ifname = ifname
        self.ip = None

aps = []
for i in range(1, len(sys.argv), 2):
    ap = ApConfig(sys.argv[i], sys.argv[i + 1])
    print "Add ap(%s, %s)"%(ap.ssid, ap.psk)
    aps.append(ap)
if len(aps) == 0:
    print "No ap specified."
    sys.exit(-1)

def iwlist_scan(wlan, aps):
    with os.popen("iwlist %s scan 2>/dev/null|grep ESSID|awk -F ':' '{print $2}'"%(wlan.ifname)) as f:
        all_ap = f.read()
    for ap in aps:
        ssid = '"%s"'%(ap.ssid)
        if ssid in all_ap:
            return ap
    return None

def ifconfig_scan(wlans):
    for wlan in wlans:
        wlan.ip = None

    for wlan in wlans:
        with os.popen("ifconfig %s 2>/dev/null|grep 'inet addr'|awk -F ':' '{print $2}'|awk '{print $1}'"%(wlan.ifname)) as f:
            ip = f.read().strip()
            if len(ip) > 0:
                wlan.ip = ip
                return wlan
    return None

while True:
    # detect the device, maybe changed.
    wlans = []
    while True:
        with os.popen("cat /proc/net/wireless 2>/dev/null|awk '{print $1}'|awk -F ':' '{print $1}'|grep 'wlan'") as f:
            for wlan in f.read().splitlines():
                device = DeviceConfig(wlan)
                print "Add device(%s) to config"%(device.ifname)
                wlans.append(device)

        if len(wlans) == 0:
            print "No wlan found."
            time.sleep(1)
            continue
        break

    # retrieve ip for all wlans.
    wlan = ifconfig_scan(wlans)
    if wlan is not None:
        print "Wlan %s is ok, ip is %s"%(wlan.ifname, wlan.ip)
        time.sleep(30)
        continue

    # got the ap to connect.
    ap = None
    for wlan in wlans:
        ap = iwlist_scan(wlan, aps)
        if ap is not None:
            break

    # no ap found.
    if ap is None:
        print "No ap found."
        time.sleep(10)
        continue

    print "Config wlan for ap(%s) and retrieve ip."%(ap.ssid)
    for wlan in wlans:
        try:
            nid = None
            with os.popen("sudo wpa_cli -i%s list_networks 2>/dev/null |grep '	%s	'| awk '{print $1}'"%(wlan.ifname, ap.ssid)) as f:
                nid = f.read().strip()
                if len(nid) > 0:
                    print "Use network %s for %s"%(nid, wlan.ifname)
                else:
                    print "Create network for %s"%(wlan.ifname)
            if nid is None or len(nid) == 0:
                with os.popen("sudo wpa_cli -i%s add_network 2>/dev/null"%(wlan.ifname)) as f:
                    nid = f.read().strip()
                if len(nid) == 0:
                    print "Add network for %s failed."%(wlan.ifname)
                    continue
                print "Add network %s for %s ok."%(nid, wlan.ifname)
            with os.popen("""sudo wpa_cli -i%s set_network %s ssid '"%s"' 2>/dev/null"""%(wlan.ifname, nid, ap.ssid)) as f:
                ret = f.read().strip()
                if ret != "OK":
                    print "Set network %s ssid to %s for %s failed."%(nid, ap.ssid, wlan.ifname)
                    continue
                print "Set network %s ssid %s for %s ok."%(nid, ap.ssid, wlan.ifname)
            with os.popen("""sudo wpa_cli -i%s set_network %s psk '"%s"' 2>/dev/null"""%(wlan.ifname, nid, ap.psk)) as f:
                ret = f.read().strip()
                if ret != "OK":
                    print "Set network %s psk to %s for %s failed."%(nid, ap.psk, wlan.ifname)
                    continue
                print "Add network %s psk %s for %s ok."%(nid, ap.psk, wlan.ifname)
            with os.popen("sudo wpa_cli -i%s enable_network %s 2>/dev/null"%(wlan.ifname, nid)) as f:
                ret = f.read().strip()
                if ret != "OK":
                    print "Enable network %s for %s failed."%(nid, wlan.ifname)
                    continue
                print "Enable network %s for %s ok."%(nid, wlan.ifname)
            ok = False
            for i in range(0, 10, 1):
                with os.popen("sudo wpa_cli -i%s status 2>/dev/null|grep 'wpa_state'|awk -F'=' '{print $2}'"%(wlan.ifname)) as f:
                    ret = f.read().strip()
                    print "Status %s is %s"%(wlan.ifname, ret)
                    if ret == "COMPLETED":
                        ok = True
                        break
                    time.sleep(3)
            if ok:
                ok = False
                for i in range(0, 20, 1):
                    twlan = ifconfig_scan(wlans)
                    if twlan is not None:
                        ok = True
                        break
                    print "Wait %s to dispatch ip."%(wlan.ifname)
                    time.sleep(3)
            if ok:
                # ok, set to None to keep it.
                print "Config network %s for %s ok, ip is %s."%(nid, wlan.ifname, wlan.ip)
                nid = None
            else:
                print "Config network %s ap(%s,%s) for %s failed."%(nid, ap.ssid, ap.psk, wlan.ifname)
        finally:
            if nid is not None and len(nid) > 0:
                with os.popen("sudo wpa_cli -i%s remove_network %s 2>/dev/null"%(wlan.ifname, nid)) as f:
                    ret = f.read().strip()
                    if ret != "OK":
                        print "Remove network %s for %s failed."%(nid, wlan.ifname)
                    else:
                        print "Remove netowrk %s for %s ok"%(nid, wlan.ifname)

    print "Refresh state of wlan for RaspberryPi."
