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
    print data
    
    idx = konfiguracja.idx_start
    tpiec = data[0] 
    response = urlopen(domoticz + str(idx) + value + tpiec)

    idx += 1
    tpowrot = data[1]
    response = urlopen(domoticz + str(idx) + value + tpowrot)

    idx += 1
    tpodajnik = data[2]
    response = urlopen(domoticz + str(idx) + value + tpodajnik)

    idx += 1
    tzew = data[3]
    response = urlopen(domoticz + str(idx) + value + tzew)

    idx += 1
    tzew = data[4]
    response = urlopen(domoticz + str(idx) + value + tzew)

    idx += 1
    tzew = data[5]
    response = urlopen(domoticz + str(idx) + value + tzew)

    idx += 1
    tcwu = data[6]
    response = urlopen(domoticz + str(idx) + value + tcwu)

    idx += 1
    tzew = data[7]
    response = urlopen(domoticz + str(idx) + value + tzew)

    idx += 1
    tzew = data[8]
    response = urlopen(domoticz + str(idx) + value + tzew)

    idx += 1
    tzew = data[9]
    response = urlopen(domoticz + str(idx) + value + tzew)

    idx += 1
    tzew = data[10]
    response = urlopen(domoticz + str(idx) + value + tzew)


  except:
    pass

  time.sleep(60)
