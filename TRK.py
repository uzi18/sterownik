#!/usr/bin/python
# -*- coding: utf-8 -*-

#===============================================================================
#               TRK by Stan v 0.3.64
#===============================================================================

# Import bibliotek
from sterownik import *
import threading, time
import signal, os
try:
  import konf_polaczenie
except ImportError:
  raise ImportError('brak pliku konfiguracji polaczenia ze sterownikiem: konf_polaczenie.py')

c = sterownik(konf_polaczenie.ip, konf_polaczenie.login, konf_polaczenie.haslo);

try:
  from konf_TRK import *
except ImportError:
  raise ImportError('brak pliku konfiguracji parametrow pracy TRK: konf_TRK.py')


#===========================================================================================
#                KOD PROGRAMU
#===============================================================================
global czPod
global czPrz
global czNaw
global moNaw
global tZadGora
global tZadDol
global hist
global praca
global p
global d
global ts060
global razy_jeden
global maxdelta
maxdelta = 0
global max_licznik
max_licznik = 0
global ostatni_stop
ostatni_stop = 0
global autodopalanie
autodopalanie = False
ts060 = 0
global opoznienie_licznik
opoznienie_licznik = 0
global ile_krokow
ile_krokow = len(czas_podawania);
if not len(czas_podawania) == len(czas_przerwy) == len(czas_nawiewu) == len(moc_nawiewu) == len(tryb):
   print ("Błąd: Zła ilość elementów w blokach")
   sys.exit()

razy_jeden = ile_krokow * [False];

#========= WATKI ==============================================================
class RTimer(object):
    def __init__(self, function):
        self._timer     = None
        self.interval   = None
        self.function   = function
        self.is_running = False

    def _run(self):
        self.is_running = False
        self.start()
        self.function()

    def start(self):
        if not self.is_running:
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def startInterval(self, interval):
        self.interval = interval
        if not self.is_running:
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

def spaliny():
    global maxdelta
    global max_licznik
    global deltaspalin
    global autodopalanie
    global opoznienie_licznik
    global ts060
    wspaliny.stop()
    x = c.getTempSpaliny()
    daneTSpal.pop(0)
    daneTSpal.append(x)
    tts060 = ts060 
    ts020 = daneTSpal[-1] - daneTSpal[-3]
    ts060 = daneTSpal[-1] - daneTSpal[-1 -1 * 6 * 1]
    ts061 = daneTSpal[-2] - daneTSpal[-2 -1 * 6 * 1]
    ts120 = daneTSpal[-1] - daneTSpal[-1 -1 * 6 * 2]
    ts180 = daneTSpal[-1] - daneTSpal[-1 -1 * 6 * 3]
    tts060 = ts060 - tts060
    print ("trend TSpal: " + str(ts020) + "/20s "+ str(ts060) + "/60s "+ str(ts120) + "/120s "+ str(ts180) + "/180s")
    print ("trend tts060: " + str(tts060) + "/60s  tspalin:" + str(x) + " tco:"+ str(c.getTempCO()))
    
    if autodopalanie == True and wsd.is_running == False:
       max_licznik = max_licznik + 1
       if opoznienie_licznik != opoznienie:
          opoznienie_licznik = opoznienie_licznik + 1
          wspaliny.start()
          return
       
       opoznienie_licznik = 0
       
       if ts060 < 0 and ts060 < maxdelta:
          maxdelta = abs(ts060)
       
       if max_licznik > 6 * 15:
          print ("*** MAX CZAS DOPALANIA OSIAGNIETO delta:"+str(maxdelta))
          deltaspalin = int(abs(maxdelta)*0.9)
          autodopalanie = False
          wspaliny.start()
          return
       
       if c.getTempPodajnik() > max_temp_podajnika:
          print ("*** MAX TEMP PODAJNIKA OSIAGNIETA")
          autodopalanie = False
          wspaliny.start()
          return

       #if x - 20 <= tempZadanaDol:
       #   print("a")
       #   autodopalanie = False
       #   wspaliny.start()
       #   return

       if ts060 <= -deltaspalin and x < tspalin:
          print("b")
          autodopalanie = False
          wspaliny.start()
          return
      
       elif ts060 < -deltaspalin and tts060 < 0:
          print("c")
          autodopalanie = False
          wspaliny.start()
          return

       elif ts060 > 0 and ts061 < 0:
          print("d")
          autodopalanie = False
          wspaliny.start()
          return
      
       delta = tspalin - x
       if delta < 0:
          delta = delta / 2
       moc = c.getDmuchawaMoc()
       if ts060 != 0:
          nowamoc = int(moc + delta/abs(ts060))
       else:
          nowamoc = moc
       
       if nowamoc > max_obr_dmuchawy:
          nowamoc = max_obr_dmuchawy

       if nowamoc < min_obr_dmuchawy:
          nowamoc = min_obr_dmuchawy
        
       print ("autodopalanie TSpal: " + str(x) + " delta: "+ str(delta) +" moc: "+ str(moc) + " nowamoc: "+ str(nowamoc))
       c.setDmuchawaMoc(nowamoc)
    else:
      max_licznik = 0
    wspaliny.start()

def status():
    wstatus.stop()
    c.getStatus()
    wstatus.start()

def regulatorCWU():
    wcwu.stop()
    print ("Watek regulator CWU...")
    if (c.getTrybAuto() != True):
        if (c.getTempCO() >= T_dolna_CWU):
            if (c.getTempCWU() < T_dolna_CWU):
                if (c.getPompaCWU() == False):
                    c.setPompaCWU(True);
        elif (c.getTempCWU() >= T_dolna_CWU):
            if (c.getPompaCWU() == True):
             c.setPompaCWU(False);
    wcwu.start()

def uruchomBloki():
    wbl.stop()
    pracaBloki()

def podtrzymanie():
    wpod.stop()
    print ("Podtrzymanie ...")
    pracaPieca(podtrzymanie_podajnik,podtrzymanie_przerwa + podtrzymanie_podajnik,podtrzymanie_przerwa,podtrzymanie_nadmuch,False)
    #if tlo > 0:
    #    c.setDmuchawa(True);
    #    c.setDmuchawaMoc(tlo);
    wpod.startInterval(podtrzymanie_postoj*60)

def stopPodajnik():
    global p
    wsp.stop()
    c.setPodajnik(False);
    p = 0

def stopDmuchawa():
    global d
    global autodopalanie
    wsd.stop()
    while autodopalanie == True:
      time.sleep(0.01)
    
    c.setDmuchawa(False);
    d = 0

c.getStatus()    
daneTSpal = []
x = c.getTempSpaliny()
# 60 * 10s.
for y in range(60):
    daneTSpal.append(x) 

wstatus = RTimer(status)
wstatus.startInterval(2)
wspaliny = RTimer(spaliny)
wspaliny.startInterval(10) # co 10s.
wcwu = RTimer(regulatorCWU)
wcwu.startInterval(10)
wbl = RTimer(uruchomBloki)
wsp = RTimer(stopPodajnik)
wsd = RTimer(stopDmuchawa)
wpod = RTimer(podtrzymanie)

#========= FUNKCJA PRACA PIECA ==============================================================

def pracaPieca(czPod,czPrz,czNaw,moNaw,asp):
    global autodopalanie
    global p
    global d
    p = 0
    d = 0
    autodopalanie = False
    if czNaw >= czPrz:
        czNaw = czPrz
        
    if czNaw > 0:
        c.setDmuchawa(True);
        c.setDmuchawaMoc(moNaw);
        d = 1
        wsd.startInterval(czNaw)
        autodopalanie = asp

    if czPod > 0:
        c.setPodajnik(True);
        p = 1
        wsp.startInterval(czPod)
        
    while p != 0 or d != 0:
        time.sleep(0.01)
    
    print ("praca wyjscie ...")
    return

#=========== FUNKCJA SPRAWDZENIA TMPERATURY CO ===============================================

def tempCO(tZadGora,tZadDol):
    global praca
    global hist
    global razy_jeden
    tco = c.getTempCO()
    if (tco < tZadDol):
        praca = 1
        hist = 1
        razy_jeden = ile_krokow * [False];
        print ('warunek spełniony Todcz < Tzad dolnej - uruchamiam grzanie')
        print ("Temperatura CO: " + str(tco) + "°C")
    elif (tco > tZadGora + 0.2):
        praca = 0
        hist = 0
        print ('warunek spełniony Todcz > Tzad górnej - zatrzymuję grzanie')
        print ("Temperatura CO: " + str(tco) + "°C")
        time.sleep(5);
    elif (hist == 1 or wymuszonahistereza == True) and (tco < tZadGora + 0.2):
        praca = 1
        print ('warunek spełniony Todcz < Tzad górnej - kontynuuję grzanie')
        print ("Temperatura CO: " + str(tco) + "°C")
    else:
        praca = 0
        print ("Temperatura CO: " + str(tco) + "°C. Oczekiwanie.")
        time.sleep(5);
    
    if praca:
        if wpod.is_running == True:
           wpod.stop()
    else:
        if wpod.is_running != True:
           wpod.startInterval(podtrzymanie_postoj*60)

#================ Przertwarzanie bloków ===============================================

def pracaBloki():
    global razy_jeden
    global ostatni_stop
    while True:
        licznik = 0
        if (c.getTrybAuto() != True):
            tZadGora = tempZadanaGora
            tZadDol = tempZadanaDol
            tempCO(tZadGora,tZadDol)
            
            if Tryb_autolato and c.getTempZew() > T_zewnetrzna_lato:
                if c.getPompaCO() == True:
                    c.setPompaCO(False)
            else:
                if c.getPompaCO() == False:
                    c.setPompaCO(True)
            
            for l in range(0,ile_krokow):
                if tryb[l] == 'stop':
                  ostatni_stop = l
            
            if praca == 1:
                for licznik in range(0,ile_krokow):
                    if czas_podawania[licznik] > 0:
                        czPod = czas_podawania[licznik] + czasPodawania
                    else:
                        czPod = 0
                    
                    if czas_przerwy[licznik] > 0:
                        czPrz = czas_przerwy[licznik] + czas_podawania[licznik] + czasPrzerwy + czasPodawania
                    else:
                        czPrz = 0
                    
                    if czas_nawiewu[licznik] > 0:
                        czNaw = czas_nawiewu[licznik] + czas_podawania[licznik] + czasNawiewu + czasPodawania
                    else:
                        czNaw = 0
                    
                    if moc_nawiewu[licznik] > 0:
                        moNaw = moc_nawiewu[licznik] + mocNawiewu
                    else:
                        moNaw = 0
                    
                    if tryb_autodopalania:
                       asp = licznik == ostatni_stop
                    else:
                       asp = False

                    TRYB = tryb[licznik]
                    tco = c.getTempCO()

                    if (tco <= tempZadanaDol):
                        if TRYB == 'start':
                            print ("uruchamiam blok START nr " + str(licznik))
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                        elif TRYB == 'jeden_start' and razy_jeden[licznik] == False:
                            print ("uruchamiam blok JEDEN_START nr " + str(licznik))
                            razy_jeden[licznik] = True
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                    elif (tco < tempZadanaGora) and (tco > tempZadanaDol):
                        if TRYB == 'normal':
                            print ("uruchamiam blok NORMAL nr " + str(licznik))
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                        elif TRYB == 'jeden_normal' and razy_jeden[licznik] == False:
                            print ("uruchamiam blok JEDEN_NORMAL nr " + str(licznik))
                            razy_jeden[licznik] = True
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                    elif (tco >= tempZadanaGora):
                        if TRYB == 'stop':
                            print ("uruchamiam blok STOP nr " + str(licznik))
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                        elif TRYB == 'jeden_stop' and razy_jeden[licznik] == False:
                            print ("uruchamiam blok JEDEN_STOP nr " + str(licznik))
                            razy_jeden[licznik] = True
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                    elif (tco >= tempZadanaGora) or (tco <= tempZadanaDol):
                        if TRYB == 'oba':
                            print ("uruchamiam blok OBA nr " + str(licznik))
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                    
#=================================================================================================
#                  PROGRAM GŁÓWNY
#=================================================================================================
praca = 0
hist = 1
wbl.startInterval(1)

try:
    while True:
        time.sleep(1);

finally:
    print ("Kończę działanie ...")
    c.setDmuchawa(False);
    c.setPodajnik(False);
    c.setPompaCWU(False);
    c.setPompaCO(False);
    os.kill(os.getpid(), signal.SIGTERM)
