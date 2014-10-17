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
  import konf_TRK
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
global kold
global knew
global nowakonfiguracja
nowakonfiguracja = False
global ile_krokow
ile_krokow = len(konf_TRK.czas_podawania);
if not len(konf_TRK.czas_podawania) == len(konf_TRK.czas_przerwy) == len(konf_TRK.czas_nawiewu) == len(konf_TRK.moc_nawiewu) == len(konf_TRK.tryb):
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
       c.setDmuchawa(True); #workaround - na wylaczajaca sie dmuchawe
       max_licznik = max_licznik + 1
       
       if (c.getTempCO() < konf_TRK.tempZadanaGora): 
          autodopalanie = False
          wspaliny.start()
          return
       
       if opoznienie_licznik != konf_TRK.opoznienie:
          opoznienie_licznik = opoznienie_licznik + 1
          wspaliny.start()
          return
       
       opoznienie_licznik = 0
       
       if ts060 < 0 and ts060 < maxdelta:
          maxdelta = abs(ts060)
       
       if max_licznik > 6 * 15:
          print ("*** MAX CZAS DOPALANIA OSIAGNIETO delta:"+str(maxdelta))
          deltaspalin = abs(maxdelta)*0.9
          autodopalanie = False
          wspaliny.start()
          return
       
       if c.getTempPodajnik() > konf_TRK.max_temp_podajnika:
          print ("*** MAX TEMP PODAJNIKA OSIAGNIETA")
          autodopalanie = False
          wspaliny.start()
          return

       #if x - 20 <= konf_TRK.tempZadanaDol:
       #   print("a")
       #   autodopalanie = False
       #   wspaliny.start()
       #   return

       if ts060 <= -konf_TRK.deltaspalin and x < konf_TRK.tspalin:
          print("b")
          autodopalanie = False
          wspaliny.start()
          return
      
       elif ts060 < -konf_TRK.deltaspalin and tts060 < 0:
          print("c")
          autodopalanie = False
          wspaliny.start()
          return

       elif ts060 > 0 and ts061 < 0:
          print("d")
          autodopalanie = False
          wspaliny.start()
          return
      
       delta = konf_TRK.tspalin - x
       if delta < 0:
          delta = delta / 2
       moc = c.getDmuchawaMoc()
       if ts060 != 0:
          nowamoc = int(moc + delta/abs(ts060))
       else:
          nowamoc = moc
       
       if nowamoc > konf_TRK.max_obr_dmuchawy:
          nowamoc = konf_TRK.max_obr_dmuchawy

       if nowamoc < konf_TRK.min_obr_dmuchawy:
          nowamoc = konf_TRK.min_obr_dmuchawy
        
       print ("autodopalanie TSpal: " + str(x) + " delta: "+ str(delta) +" moc: "+ str(moc) + " nowamoc: "+ str(nowamoc))
       c.setDmuchawaMoc(nowamoc)
    else:
      max_licznik = 0
    wspaliny.start()

def status():
    wstatus.stop()
    c.getStatus()
    if c.getTrybAuto() == True:
       print ("*** UWAGA! sterownik w trybie AUTO")
    wstatus.start()

def files_to_timestamp(path):
    files = [os.path.join(path, f) for f in os.listdir(path)]
    return dict ([(f, os.path.getmtime(f)) for f in files])

def konfig():
    wkonf.stop()
    global kold
    global knew
    global nowakonfiguracja
    knew = files_to_timestamp('.')
    added = [f for f in knew.keys() if not f in kold.keys()]
    removed = [f for f in kold.keys() if not f in knew.keys()]
    modified = []

    for f in kold.keys():
        if not f in removed:
           if os.path.getmtime(f) != kold.get(f):
              modified.append(f)
       
    kold = knew
    for f in modified:
        if f == './konf_TRK.py':
           nowakonfiguracja = True
    
    wkonf.start()

def regulatorCWU():
    wcwu.stop()
    print ("Watek regulator CWU...")
    if (c.getTrybAuto() != True):
        if (c.getTempCO() >= konf_TRK.T_dolna_CWU):
            if (c.getTempCWU() < konf_TRK.T_dolna_CWU):
                if (c.getPompaCWU() == False):
                    c.setPompaCWU(True);
                    print ("*** CWU: ON")
        elif (c.getTempCWU() >= konf_TRK.T_dolna_CWU):
            if (c.getPompaCWU() == True):
             c.setPompaCWU(False);
             print ("*** CWU: OFF")
    wcwu.start()

def uruchomBloki():
    wbl.stop()
    pracaBloki()

def podtrzymanie():
    wpod.stop()
    print ("Podtrzymanie ...")
    pracaPieca(konf_TRK.podtrzymanie_podajnik,konf_TRK.podtrzymanie_przerwa + konf_TRK.podtrzymanie_podajnik,konf_TRK.podtrzymanie_przerwa,konf_TRK.podtrzymanie_nadmuch,False)
    #if tlo > 0:
    #    c.setDmuchawa(True);
    #    c.setDmuchawaMoc(konf_TRK.tlo);
    wpod.startInterval(konf_TRK.podtrzymanie_postoj*60)

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
kold = files_to_timestamp('.')
wkonf = RTimer(konfig)
wkonf.startInterval(10)
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
    elif (hist == 1 or konf_TRK.wymuszonahistereza == True) and (tco < tZadGora + 0.2):
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
           wpod.startInterval(konf_TRK.podtrzymanie_postoj*60)

#================ Przertwarzanie bloków ===============================================

def pracaBloki():
    global razy_jeden
    global ostatni_stop
    while True:
        licznik = 0
        if (c.getTrybAuto() != True):
            tZadGora = konf_TRK.tempZadanaGora
            tZadDol = konf_TRK.tempZadanaDol
            tempCO(tZadGora,tZadDol)
            
            if konf_TRK.Tryb_autolato and c.getTempZew() > konf_TRK.T_zewnetrzna_lato:
                if c.getPompaCO() == True:
                    print ("*** AUTOLATO: OFF")
                    c.setPompaCO(False)
            else:
                if c.getPompaCO() == False:
                    print ("*** AUTOLATO: ON")
                    c.setPompaCO(True)
            
            #for l in range(0,ile_krokow):
            #    if konf_TRK.tryb[l] == 'stop':
            #      ostatni_stop = l
            ostatni_stop = ile_krokow - 1
            
            if praca == 1:
                for licznik in range(0,ile_krokow):
                    if konf_TRK.czas_podawania[licznik] > 0:
                        czPod = konf_TRK.czas_podawania[licznik] + konf_TRK.czasPodawania
                    else:
                        czPod = 0
                    
                    if konf_TRK.czas_przerwy[licznik] > 0:
                        czPrz = konf_TRK.czas_przerwy[licznik] + konf_TRK.czas_podawania[licznik] + konf_TRK.czasPrzerwy + konf_TRK.czasPodawania
                    else:
                        czPrz = 0
                    
                    if konf_TRK.czas_nawiewu[licznik] > 0:
                        czNaw = konf_TRK.czas_nawiewu[licznik] + konf_TRK.czas_podawania[licznik] + konf_TRK.czasNawiewu + konf_TRK.czasPodawania
                    else:
                        czNaw = 0
                    
                    if konf_TRK.moc_nawiewu[licznik] > 0:
                        moNaw = konf_TRK.moc_nawiewu[licznik] + konf_TRK.mocNawiewu
                    else:
                        moNaw = 0
                    
                    if konf_TRK.tryb_autodopalania:
                       asp = licznik == ostatni_stop
                    else:
                       asp = False

                    TRYB = konf_TRK.tryb[licznik]
                    tco = c.getTempCO()

                    if (tco <= konf_TRK.tempZadanaDol):
                        if TRYB == 'start':
                            print ("uruchamiam blok START nr " + str(licznik))
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                        elif TRYB == 'jeden_start' and razy_jeden[licznik] == False:
                            print ("uruchamiam blok JEDEN_START nr " + str(licznik))
                            razy_jeden[licznik] = True
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                    elif (tco < konf_TRK.tempZadanaGora) and (tco > konf_TRK.tempZadanaDol):
                        if TRYB == 'normal':
                            print ("uruchamiam blok NORMAL nr " + str(licznik))
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                        elif TRYB == 'jeden_normal' and razy_jeden[licznik] == False:
                            print ("uruchamiam blok JEDEN_NORMAL nr " + str(licznik))
                            razy_jeden[licznik] = True
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                    elif (tco >= konf_TRK.tempZadanaGora):
                        if TRYB == 'stop':
                            print ("uruchamiam blok STOP nr " + str(licznik))
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                        elif TRYB == 'jeden_stop' and razy_jeden[licznik] == False:
                            print ("uruchamiam blok JEDEN_STOP nr " + str(licznik))
                            razy_jeden[licznik] = True
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                    elif (tco >= konf_TRK.tempZadanaGora) or (tco <= konf_TRK.tempZadanaDol):
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
        if nowakonfiguracja == True:
           print ('Nowa konfiguracja')
           reload(sys.modules["konf_TRK"])
           nowakonfiguracja = False
           ile_krokow = len(konf_TRK.czas_podawania);
           if not len(konf_TRK.czas_podawania) == len(konf_TRK.czas_przerwy) == len(konf_TRK.czas_nawiewu) == len(konf_TRK.moc_nawiewu) == len(konf_TRK.tryb):
              print ("Błąd: Zła ilość elementów w blokach")
              sys.exit()

           razy_jeden = ile_krokow * [False];
        time.sleep(0.2);

finally:
    print ("Kończę działanie ...")
    c.setDmuchawa(False);
    c.setPodajnik(False);
    c.setPompaCWU(False);
    c.setPompaCO(False);
    os.kill(os.getpid(), signal.SIGTERM)
