#!/usr/bin/python
# -*- coding: utf-8 -*-

#==================================================================================
#               TRK by Stan v 0.3.62            5au.py Automatyczne pob. konf_TRK
#==================================================================================

# Import bibliotek
from sterownik import *
import threading, time
import signal, os
try:
  import konf_polaczenie
except ImportError:
  raise ImportError('brak pliku konfiguracji polaczenia ze sterownikiem: konf_polaczenie.py')

c = sterownik(konf_polaczenie.ip, konf_polaczenie.login, konf_polaczenie.haslo);
c.getStatus()

try:
  import konf_TRK
except ImportError:
  raise ImportError('brak pliku konfiguracji parametrow pracy TRK: konf_TRK.py')

poprzednitryb = c.getTrybAuto()
if konf_TRK.autotrybmanual:
   c.setTrybAuto(False)

#===============================================================================
#                KOD PROGRAMU
#===============================================================================
global tp
global td
tp = 0
td = 0
global czPod
global czPrz
global czNaw
global moNaw
global tlo
global tKmax
global tK2
global tKzadana
global tK4
global tKmin
global praca
global p
global d
global kold
global knew
global nowakonfiguracja
nowakonfiguracja = False
global ile_krokow
ile_krokow = len(konf_TRK.czas_podawania);
if not len(konf_TRK.czas_podawania) == len(konf_TRK.czas_przerwy) == len(konf_TRK.czas_nawiewu) == len(konf_TRK.moc_nawiewu) == len(konf_TRK.tryb):
   print ("Blad: Zla ilosc elementow w blokach")
   sys.exit()

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
    knew = files_to_timestamp(os.path.abspath(os.path.dirname(sys.argv[0])))
    added = [f for f in knew.keys() if not f in kold.keys()]
    removed = [f for f in kold.keys() if not f in knew.keys()]
    modified = []

    for f in kold.keys():
        if not f in removed:
           if os.path.getmtime(f) != kold.get(f):
              modified.append(f)
       
    kold = knew
    for f in modified:
        if os.path.isfile(f) and os.path.basename(f) == 'konf_TRK.py':
           nowakonfiguracja = True
    
    wkonf.start()


def regulatorCWU():
    wcwu.stop()

    if (c.getTrybAuto() != True):
        print ("Regulator CWU...")
        if (c.getTempCO() > konf_TRK.tempZalaczeniaPomp):
            pompa = True
        if (c.getTempCO() < konf_TRK.tempZalaczeniaPomp - 3.0):
            pompa = False
        
        if c.getTempCO() < c.getTempCWU():
            pompa = False
          
        if (c.getTempCWU() > konf_TRK.T_dolna_CWU and not konf_TRK.CWU_jako_bufor):
            pompa = False
        #elif (c.getTempCO() < konf_TRK.tempZalaczeniaPomp - 3.0) or (c.getTempCWU() > konf_TRK.T_dolna_CWU) or (c.getTempCO() < c.getTempCWU()):
        if (pompa and c.getPompaCWU() == False):
            c.setPompaCWU(True);
            print ("*** CWU: ON")
        
        elif (not pompa and c.getPompaCWU() == True):
            c.setPompaCWU(False);
            print ("*** CWU: OFF")

    wcwu.start()

def regulatorCO():
    wco.stop()

    if (c.getTrybAuto() != True):
        print ("Regulator CO...")
        if (c.getTempCO() > konf_TRK.tempZalaczeniaPomp):
            pompa = True
        if (c.getTempCO() < konf_TRK.tempZalaczeniaPomp - 5.0):
            pompa = False
            
        a = ''
        if konf_TRK.Tryb_autolato and c.getTempZew() > konf_TRK.T_zewnetrzna_lato:
            pompa = False
            a = "AUTOLATO"
           
        if (pompa and c.getPompaCO() == False):
            c.setPompaCO(True)
            print ("*** CO->ON")
        elif (not pompa and c.getPompaCO() == True):
            c.setPompaCO(False)
            print ("*** CO->OFF " + a)
    
    wco.start()

def uruchomBloki():
    wbl.stop()
    pracaBloki()

def podtrzymanie():
    wpod.stop()
    print ("*** Podtrzymanie ...")
    #konf_TRK.czas_tla = 20
    #konf_TRK.tlo = 38
    pracaPieca(konf_TRK.podtrzymanie_podajnik,konf_TRK.podtrzymanie_przerwa,konf_TRK.podtrzymanie_nadmuch,konf_TRK.podtrzymanie_mocNawiewu)
    #if tlo > 0:
    #    c.setDmuchawa(True);
    #    c.setDmuchawaMoc(konf_TRK.tlo);
    wpod.startInterval(konf_TRK.podtrzymanie_postoj*60)

def stopPodajnik():
    global p
    wsp.stop()
    c.setPodajnik(False);
    print (" <<< Stop podajnik realny czas: "+ str(time.time() - tp))
    p = 0

def stopDmuchawa():
    global d
    wsd.stop()
    
    c.setDmuchawa(False);
    print (" @<@ Stop dmuchawa realny czas: "+ str(time.time() - td))
    d = 0

c.getStatus()

wstatus = RTimer(status)
wstatus.startInterval(2)
#wspaliny = RTimer(spaliny)
#wspaliny.startInterval(10) # co 10s.
wcwu = RTimer(regulatorCWU)
wcwu.startInterval(60)
wco = RTimer(regulatorCO)
wco.startInterval(20)
kold = files_to_timestamp(os.path.abspath(os.path.dirname(sys.argv[0])))
wkonf = RTimer(konfig)
wkonf.startInterval(10)
wbl = RTimer(uruchomBloki)
wsp = RTimer(stopPodajnik)
wsd = RTimer(stopDmuchawa)
wpod = RTimer(podtrzymanie)


#========= FUNKCJA PRACA PIECA ==============================================================

def pracaPieca(czPod,czPrz,czNaw,moNaw):
    global tp
    global td
    global p
    global d
    p = 0
    d = 0
    if czNaw >= czPrz:
        czNaw = czPrz
        
    if czNaw > 0:
        c.setDmuchawa(True);
        td = time.time()
        c.setDmuchawaMoc(moNaw);
        d = 1
        print (" @>@ Start dmuchawa na czas: " + str(czNaw) + "s moc:"+ str(moNaw) + "%")
        wsd.startInterval(czNaw)

    if czPod > 0:
        c.setPodajnik(True);
        tp = time.time()
        p = 1
        print (" >>> Start podajnik na czas: " + str(czPod))
        wsp.startInterval(czPod)
        
    while p != 0 or d != 0:
        time.sleep(0.01)

    return


#=========== FUNKCJA SPRAWDZENIA TMPERATURY CO ===============================================

def tempCO(tKmax,tK2,tKzadana,tK4,tKmin):
    global praca
    if ((c.getTempCO()) <= tKmax):
                praca = 1
                #hist = 1
                print ('** Todcz <= Temp. MAX-CO TKmax - ** PRACA **')
                print (" * Temperatura CO: " + str(c.getTempCO()) + "°C")
    elif ((c.getTempCO()) > tKmax):
                praca = 0
                #hist = 0
                print (' ** Todcz > Temp. max CO TKmax - ** STOP **')
                print (" * Temperatura CO: " + str(c.getTempCO()) + "°C")
                print (" # Temperatura spalin: " + str(c.getTempSpaliny()) + "°C")
                time.sleep(20);

    if praca:
        if wpod.is_running == True:
           wpod.stop()
    else:
        if wpod.is_running != True:
           wpod.startInterval(konf_TRK.podtrzymanie_postoj*60)

    #return praca


#================ Tryb Lato ===========================================================

def trybLato():
    pass



#=================================================================================================
#                  PROGRAM GŁÓWNY
#================================================================================================

def pracaBloki():
 while True:
     licznik = 0
     if (bool(c.getStatus())):
         if (c.getTrybAuto() != True):
            c.setPompaCO(True);
            tKmax = konf_TRK.TKmax
            tK2 = konf_TRK.TK2
            tKzadana = konf_TRK.TKzadana
            tK4 = konf_TRK.TK4
            tKmin = konf_TRK.TKmin
            tempCO(tKmax,tK2,tKzadana,tK4,tKmin)
            #if ((c.getTempCO()) < tKzadana):
                #jeden_licznik = 0    # do sprawdzenia dlaczego po wycieciu nie dziala skrypt
            for licznik in range(0,ile_krokow):
                if praca == 1:
                    if konf_TRK.czas_podawania[licznik] > 0:
                        czPod = konf_TRK.czas_podawania[licznik] + konf_TRK.czasPodawania
                    else:
                        czPod = 0
                    if konf_TRK.czas_przerwy[licznik] > 0:
                        czPrz = konf_TRK.czas_przerwy[licznik] + konf_TRK.czas_podawania[licznik] + konf_TRK.czasPrzerwy + konf_TRK.czasPodawania
                    else:
                        czPrz = 0
                    if konf_TRK.czas_nawiewu[licznik] > 0:
                        czNaw = konf_TRK.czas_nawiewu[licznik] + konf_TRK.czasNawiewu + konf_TRK.czas_podawania[licznik]
                    else:
                        czNaw = 0
                    if konf_TRK.moc_nawiewu[licznik] > 0:
                       moNaw = konf_TRK.moc_nawiewu[licznik] + konf_TRK.mocNawiewu
                    else:
                        moNaw = 0
                    TRYB = konf_TRK.tryb[licznik]

                    if ((c.getTempCO()) <= konf_TRK.TKmin):
                        if TRYB == 'MOC-5':
                            print ("Uruchamiam blok MOC-5 nr " + str(licznik))
                            print (" * Temperatura CO: " + str(c.getTempCO()) + "°C")
                            print (" # Temperatura spalin: " + str(c.getTempSpaliny()) + "°C")
                            print (" Temp CO < TKmin ")
                            print (TRYB)
                            pracaPieca(czPod,czPrz,czNaw,moNaw)
                    if ((c.getTempCO()) <= konf_TRK.TK4):
                        if ((c.getTempCO()) > konf_TRK.TKmin):
                            if TRYB == 'MOC-4':
                                print ("Uruchamiam blok MOC-4 nr " + str(licznik))
                                print (" * Temperatura CO: " + str(c.getTempCO()) + "°C")
                                print (" # Temperatura spalin: " + str(c.getTempSpaliny()) + "°C")
                                print (" TKmin < Temp CO <= TK4 ")
                                print (TRYB)
                                pracaPieca(czPod,czPrz,czNaw,moNaw)
                    if ((c.getTempCO()) <= konf_TRK.TKzadana):
                        if ((c.getTempCO()) > konf_TRK.TK4):
                            if TRYB == 'MOC-3':
                                print ("Uruchamiam blok MOC-3 nr " + str(licznik))
                                print (" * Temperatura CO: " + str(c.getTempCO()) + "°C")
                                print (" # Temperatura spalin: " + str(c.getTempSpaliny()) + "°C")
                                print (" TK4 < Temp CO <= TKzadana ")
                                print (TRYB)
                                pracaPieca(czPod,czPrz,czNaw,moNaw)
                    if ((c.getTempCO()) <= konf_TRK.TK2):
                        if ((c.getTempCO()) > konf_TRK.TKzadana):
                            if TRYB == 'MOC-2':
                                print ("Uruchamiam blok MOC-2 nr " + str(licznik))
                                print (" * Temperatura CO: " + str(c.getTempCO()) + "°C")
                                print (" # Temperatura spalin: " + str(c.getTempSpaliny()) + "°C")
                                print (" TKzadana < Temp CO <= TK2 ")
                                print (TRYB)
                                pracaPieca(czPod,czPrz,czNaw,moNaw)         
                    if ((c.getTempCO()) <= konf_TRK.TKmax):
                        if ((c.getTempCO()) > konf_TRK.TK2):
                            if TRYB == 'MOC-1':
                                print ("Uruchamiam blok MOC-1 nr " + str(licznik))
                                print (" * Temperatura CO: " + str(c.getTempCO()) + "°C")
                                print (" # Temperatura spalin: " + str(c.getTempSpaliny()) + "°C")
                                print (" TK2 < Temp CO <= TKmax ")
                                print (TRYB)
                                pracaPieca(czPod,czPrz,czNaw,moNaw)
                    if ((c.getTempCO()) > konf_TRK.TKmax):
                        if TRYB == 'STOP':
                            print ("Uruchamiam blok STOP nr " + str(licznik))
                            print (" * Temperatura CO: " + str(c.getTempCO()) + "°C")
                            print (" # Temperatura spalin: " + str(c.getTempSpaliny()) + "°C")
                            print (" Temp CO > TKmax ")
                            print (TRYB)
                            pracaPieca(czPod,czPrz,czNaw,moNaw)
                        
                    if (((c.getTempCO()) > konf_TRK.TKmax) and konf_TRK.tlo > 0):
                        c.setDmuchawa(True);
                        c.setDmuchawaMoc(konf_TRK.tlo);
                        print (" *** Uruchamiam TLO *** ")
                        print (" * Start dmuchawa TLO: moc:" + str(tlo) + "%")
         else:
           time.sleep(0.1);

praca = 0
wbl.startInterval(1)
try:
    while True:
        if nowakonfiguracja == True:
           print ('** = * = Nowa konfiguracja: Wczytywanie ...')
           stare_tryby = konf_TRK.tryb
           reload(sys.modules["konf_TRK"])
           nowakonfiguracja = False
           ile_krokow = len(konf_TRK.czas_podawania);
           if not len(konf_TRK.czas_podawania) == len(konf_TRK.czas_przerwy) == len(konf_TRK.czas_nawiewu) == len(konf_TRK.moc_nawiewu) == len(konf_TRK.tryb):
              print ("Blad: Zla ilosc elementow w blokach")
              if konf_TRK.autotrybmanual:
                c.setTrybAuto(poprzednitryb)
              os.kill(os.getpid(), signal.SIGTERM)
           
           if stare_tryby != konf_TRK.tryb:
              razy_jeden = ile_krokow * [False];
           
        time.sleep(0.2);

finally:
    print (" Koncze dzialanie ...")
    c.setDmuchawa(False);
    c.setPodajnik(False);
    c.setPompaCWU(False);
    c.setPompaCO(False);
    if konf_TRK.autotrybmanual:
       c.setTrybAuto(poprzednitryb)

    os.kill(os.getpid(), signal.SIGTERM)




