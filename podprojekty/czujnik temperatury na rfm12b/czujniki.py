#!/usr/bin/python
# -*- coding: utf-8 -*-

import time 
import serial
import sys
import sdnotify  
if sys.version_info[0] == 3:
  from urllib.request import urlopen
else:
  from urllib2 import urlopen

try:
  import konfiguracja
except ImportError:
  raise ImportError('brak pliku konfiguracji polaczenia ze sterownikiem: konfiguracja.py')

rs=serial.Serial('/dev/ttyS0',9600)
#print("zainicjowalem serial, czekam na dane")

if 'ip_domoticz' in dir(konfiguracja) and 'port_domoticz' in dir(konfiguracja):
  domoticz = "http://"+konfiguracja.ip_domoticz+":"+str(konfiguracja.port_domoticz)+"/json.htm?type=command&param=udevice&idx="
  value = "&nvalue=0&svalue="

n = sdnotify.SystemdNotifier()
n.notify("READY=1")

while 1:
  try:
    data='' 
    rs.flushInput()
    rs.flushOutput()
    while not (data.startswith("start:") and data.endswith("\r\n")):
      data = rs.readline()
    data = data.replace("\r\n", "")
    data = data.replace("start:", "")
    data = data.replace(":stop", "")
    data = data.split(":", 3)
    print(data)
    temp = data[1]
    temp = float(temp)/100
#   print(temp)
    nodeid = data[0]
    tens = data[2]
    tens = float(tens)/1000
#   print(tens)
    response = urlopen(domoticz + "17" + value + str(temp))
#   print(domoticz + "5" + value + str(data))
    n.notify("WATCHDOG=1")
  except: 
    pass 
