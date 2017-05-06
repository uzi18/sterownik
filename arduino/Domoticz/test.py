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

if not 'ip_lucjan' in dir(konfiguracja):
  print("brak poprawnej konfiguracji: ip_lucjan")
  exit()

if not 'esp_link' in dir(konfiguracja):
  konfiguracja.esp_link = 0

if konfiguracja.esp_link and not 'ip_esp' in dir(konfiguracja):
  print("brak poprawnej konfiguracji: ip_esp")
  exit()

if not 'port_domoticz' in dir(konfiguracja):
  konfiguracja.port_domoticz = 8080

if not 'interwal' in dir(konfiguracja):
  konfiguracja.interwal = 30

if not 'interwal_domoticz' in dir(konfiguracja):
  konfiguracja.interwal_domoticz = konfiguracja.interwal

if not 'interwal_nettemp' in dir(konfiguracja):
  konfiguracja.interwal_nettemp = konfiguracja.interwal
  
print(" interwal = "+str(konfiguracja.interwal)+"s.")
print(" interwal domoticz = "+str(konfiguracja.interwal_domoticz)+"s.")
print(" interwal nettemp = "+str(konfiguracja.interwal_nettemp)+"s.")

licznik_dm = 0
licznik_nt = 0

if konfiguracja.ip_lucjan.count('.') == 0:
  import serial
  rs=serial.Serial(konfiguracja.ip_lucjan,115200)
  time.sleep(20)
  rs.flushInput()
  rs.flushOutput()

if konfiguracja.esp_link:
  import telnetlib

lucek = "http://"+konfiguracja.ip_lucjan+"/t.json"

if 'ip_domoticz' in dir(konfiguracja) and 'port_domoticz' in dir(konfiguracja):
  domoticz = "http://"+konfiguracja.ip_domoticz+":"+str(konfiguracja.port_domoticz)+"/json.htm?type=command&param=udevice&idx="
  value = "&nvalue=0&svalue="

while 1:
  try:
    data = ''
    if rs == None and not konfiguracja.esp_link:
      response = urlopen(lucek)
      data = response.read().decode("utf-8")
      data = data.replace('},{"t": ', ',')
      data = data.replace('{"thermos":[{"t": ', '')
      data = data.split("}],", 1)[0]
      data = data.split(",")
    elif rs == None and konfiguracja.esp_link:
      tn = telnetlib.Telnet(konfiguracja.ip_esp,23)
      tn.write('t')
      tn.read_until('t:[')
      while data.count(']') == 0:
        data += tn.read_some()
      tn.close()
      data = data.split("]")[0]
      data = data.split(",")
      data = [float(i)/10 for i in data]
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
    print(len(data))
    
    if len(data) == 16:
      if licznik_nt == 0 and 'ip_nettemp' in dir(konfiguracja) and 'key_nettemp' in dir(konfiguracja):
        print("Send NT:")
        d=";".join(str(x) for x in data)
        response = urlopen("http://"+konfiguracja.ip_nettemp+"/receiver.php?key="+konfiguracja.key_nettemp+"&device=ip&ip=localhost&name=Lucjan_&id=1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16&type=temp;temp;temp;temp;temp;temp;temp;temp;temp;temp;temp;temp;temp;temp;temp;temp&value="+d)
        print(response.msg)
        print(response.readlines())
        
      if licznik_nt == 0:
        licznik_nt = konfiguracja.interwal_nettemp
      
      if licznik_dm == 0 and 'ip_domoticz' in dir(konfiguracja) and 'port_domoticz' in dir(konfiguracja):
        print("Send DM:")
        idx = konfiguracja.idx_start
        for x in range(16):
          t = data[x]
          response = urlopen(domoticz + str(idx+x) + value + str(t))
        #drukujemy tylko ostatni komunikat
        print(response.msg)
        print(response.readlines())

      if licznik_dm == 0:
        licznik_dm = konfiguracja.interwal_domoticz

    while licznik_nt != 0 and licznik_dm != 0:
      time.sleep(1)
      licznik_nt -=1
      licznik_dm -=1

  except:
    pass

  
  
