#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] == 3:
  from urllib.request import urlopen
else:
  from urllib2 import urlopen

import time 
import string

rs = None

try:
  import konfiguracja
except ImportError:
  raise ImportError('brak pliku konfiguracji polaczenia ze sterownikiem: konfiguracja.py')

if not 'idx_start' in dir(konfiguracja):
  print("brak poprawnej konfiguracji: idx_start")
  exit()

if not 'ip_domoticz' in dir(konfiguracja):
  print("brak poprawnej konfiguracji: ip_domoticz")
  exit()

if not 'ip_lucjan' in dir(konfiguracja):
  print("brak poprawnej konfiguracji: ip_lucjan")
  exit()

if not 'port_domoticz' in dir(konfiguracja):
  konfiguracja.port_domoticz = 8080

if not 'interwal' in dir(konfiguracja):
  konfiguracja.interwal = 30
  
print(" interwal = "+str(konfiguracja.interwal)+"s.")

if konfiguracja.ip_lucjan.count('.') == 0:
  import serial
  rs=serial.Serial(konfiguracja.ip_lucjan,115200)
  time.sleep(20)
  rs.flushInput()
  rs.flushOutput()

lucek = "http://"+konfiguracja.ip_lucjan+"/t.json"
domoticz = "http://"+konfiguracja.ip_domoticz+":"+str(konfiguracja.port_domoticz)+"/json.htm?type=command&param=udevice&idx="
value = "&nvalue=0&svalue="

while 1:
  try:
    data = ''
    if rs == None:
      response = urlopen(lucek)
      data = response.read().decode("utf-8")
      data = data.replace('},{"t": ', ',')
      data = data.replace('{"thermos":[{"t": ', '')
      data = data.split("}],", 1)[0]
      data = data.split(",")
    else:
      rs.flushInput()
      rs.flushOutput()
      rs.write('t')
      while not (data.startswith("t:[") and data.endswith("\r\n")):
        data = rs.readline()

      data = data.replace('t:[', '')
      data = data.replace(']\r\n', '')
      data = data.split(",")
      data = [float(i)/10 for i in data]
      
    print(data)
    
    idx = konfiguracja.idx_start
    if len(data) == 16:
      for x in range(16):
        t = data[x]
        response = urlopen(domoticz + str(idx+x) + value + str(t))

  except:
    pass

  time.sleep(konfiguracja.interwal)
