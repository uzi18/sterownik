#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json
import os.path
import logging
from logging.handlers import RotatingFileHandler
#logging.basicConfig(level=logging.ERROR,filename=__file__ + ".log",format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
log_handler = RotatingFileHandler(__file__ + ".log", mode='a', maxBytes=10*1024*1024, backupCount=5, encoding=None, delay=0)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
logger.addHandler(log_handler)

if sys.version_info[0] == 3:
  from urllib.request import urlopen
else:
  from urllib2 import urlopen

import time 
import string

rs = None
js = {}

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

logger.error('Start')

if konfiguracja.ip_lucjan.count('.') == 0:
  import serial
  rs=serial.Serial(konfiguracja.ip_lucjan,115200,timeout=3)
  #rs.flushInput()
  #rs.flushOutput()
  #time.sleep(10)

if konfiguracja.esp_link:
  import telnetlib

lucek = "http://"+konfiguracja.ip_lucjan+"/t.json"

if 'ip_domoticz' in dir(konfiguracja) and 'port_domoticz' in dir(konfiguracja):
  domoticz = "http://"+konfiguracja.ip_domoticz+":"+str(konfiguracja.port_domoticz)+"/json.htm?type=command&param=udevice&idx="
  value = "&nvalue=0&svalue="

slij_nettemp = 'ip_nettemp' in dir(konfiguracja) and 'key_nettemp' in dir(konfiguracja);
slij_domoticz = 'ip_domoticz' in dir(konfiguracja) and 'port_domoticz' in dir(konfiguracja);

while 1:
  try:
    if os.path.exists("/var/lock/lucjan_programator"):
        print ("pauza: pracuje programator")
        time.sleep(10)
        continue
    
    data = ''
    if rs == None and not konfiguracja.esp_link:
      print ("ETH: czekam na dane")
      response = urlopen(lucek,None,3)
      j    = response.read().decode("utf-8")
      js   = json.loads(j)
      print (js)
      data2= js.get('thermos')
      data = [list(i.values())[0] for i in data2]
    elif rs == None and konfiguracja.esp_link:
      stop = False
      x,y = 0,0
      t = int(time.time())
      tn = telnetlib.Telnet(konfiguracja.ip_esp,23,3)
      tn.write(b't')
      print ("ESP: czekam na dane")
      while 1:
        a = tn.read_some()
        print(a)
        if os.path.exists("/var/lock/lucjan_debug"):
           logger.error(a)
        data += a
        x = data.find('t:[')
        y = data.find(']\r\n')
        if (y>x and x>=0 and y>=0):
          data = data[x:y]
          break
        elif x >= 0:
          data = data[x:]
        else:
          data = a
        if int(time.time())-t>5:
          t = int(time.time())
          if not os.path.exists("/var/lock/lucjan_programator"):
            tn.write(b't')
          logger.error('ESP: Timeout')
      
      tn.close()
      data = data.replace('t:[', '')
      data = data.split("]")[0]
      data = data.split(",")
      data = [float(i)/10 for i in data]
      print (data)
    else:
      #rs.flushInput()
      #rs.flushOutput()
      rs.write(b't')
      print ("SER: czekam na dane")
      t = int(time.time())
      while not (data.startswith("t:[") and data.endswith("]\r\n")):
        data = rs.readline()
        print(data)
        if os.path.exists("/var/lock/lucjan_debug"):
           logger.error(data)
        if int(time.time())-t>5:
          t = int(time.time())
          logger.error('Serial: Timeout')
          if not os.path.exists("/var/lock/lucjan_programator"):
            rs.write(b't')
      
      data = data.replace('t:[', '')
      data = data.replace(']\r\n', '')
      data = data.split(",")
      data = [float(i)/10 for i in data]
    
    print('');
    print("Lucjan RCV:")
    print(data)
    print(len(data))
    
    if len(data) == 16:
      if licznik_nt == 0 and slij_nettemp:
        print("Send NT:")
        d=";".join(str(x) for x in data)
        adr = "http://"+konfiguracja.ip_nettemp+"/receiver.php?key="+konfiguracja.key_nettemp+"&device=ip&ip=localhost&name=Lucjan_&id=1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16&type=temp;temp;temp;temp;temp;temp;temp;temp;temp;temp;temp;temp;temp;temp;temp;temp&value="+d
        print(adr)
        response = urlopen(adr)
        print(response.msg)
        print(response.readlines())

        # plus nowosci
        if 'idx_zasobnik_cm' in dir(konfiguracja) and konfiguracja.idx_zasobnik_cm > 0 and js.has_key("podcm") and js.get("pod") == 0:
            t = js.get("podcm")
            adr = "http://"+konfiguracja.ip_nettemp+"/receiver.php?key="+konfiguracja.key_nettemp+"&device=ip&ip=localhost&name=Lucjan_&id=zasobnik_cm&type=battery&value="+str(t)
            print(adr)
            response = urlopen(adr)

        if 'idx_zasobnik_procent' in dir(konfiguracja) and konfiguracja.idx_zasobnik_procent > 0 and js.has_key("podcmp") and js.get("pod") == 0:
            t = js.get("podcmp")
            adr = "http://"+konfiguracja.ip_nettemp+"/receiver.php?key="+konfiguracja.key_nettemp+"&device=ip&ip=localhost&name=Lucjan_&id=zasobnik_procent&type=battery&value="+str(t)
            print(adr)
            response = urlopen(adr)

        
      if licznik_nt == 0:
        licznik_nt = konfiguracja.interwal_nettemp
      
      if licznik_dm == 0 and slij_domoticz:
        print("Send DM:")
        idx = konfiguracja.idx_start
        for x in range(16):
          t = data[x]
          adr = domoticz + str(idx+x) + value + str(t)
          print(adr)
          response = urlopen(adr)
        #drukujemy tylko ostatni komunikat
        print(response.msg)
        print(response.readlines())
        
        # plus nowosci
        if 'idx_zasobnik_cm' in dir(konfiguracja) and konfiguracja.idx_zasobnik_cm > 0 and js.has_key("podcm") and js.get("pod") == 0:
            t = js.get("podcm")
            adr = domoticz + str(konfiguracja.idx_zasobnik_cm) + value + str(t)
            print(adr)
            response = urlopen(adr)

        if 'idx_zasobnik_procent' in dir(konfiguracja) and konfiguracja.idx_zasobnik_procent > 0 and js.has_key("podcmp") and js.get("pod") == 0:
            t = js.get("podcmp")
            adr = domoticz + str(konfiguracja.idx_zasobnik_procent) + value + str(t)
            print(adr)
            response = urlopen(adr)
        
      if licznik_dm == 0:
        licznik_dm = konfiguracja.interwal_domoticz
      
    while 1:
      print("NT: "+str(licznik_nt)+" DM: "+str(licznik_dm))
      time.sleep(1)
      if slij_nettemp and licznik_nt > 0:
         licznik_nt -=1
      if slij_domoticz and licznik_dm > 0:
         licznik_dm -=1
      if licznik_nt == 0 or licznik_dm == 0:
         break;

  except Exception, e:
    logger.error('Exception', exc_info=True)
    pass

