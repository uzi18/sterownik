#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] == 3:
  from urllib.request import urlopen
else:
  from urllib2 import urlopen

import time 
import string

try:
  import konfiguracja
except ImportError:
  raise ImportError('brak pliku konfiguracji polaczenia ze sterownikiem: konfiguracja.py')

lucek = "http://"+konfiguracja.ip_lucjan+"/t.json"
domoticz = "http://"+konfiguracja.ip_domoticz+":"+str(konfiguracja.port_domoticz)+"/json.htm?type=command&param=udevice&idx="
value = "&nvalue=0&svalue="

while 1:
  try:
    response = urlopen(lucek)
    data = response.read()
    data = string.replace(data, '},{"t": ', ',')
    data = string.replace(data, '{"thermos":[{"t": ', '')
    sep = "}],"
    data = data.split(sep, 1)[0]
    data = data.split(",")
    
    print(data)
    
    idx = konfiguracja.idx_start
    for x in range(16):
      t = data[x]
      response = urlopen(domoticz + str(idx+x) + value + t)

  except:
    pass

  time.sleep(60)
