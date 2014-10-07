#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import biblioteki
from sterownik import *
import threading
import time;
#===============================================================================
#               TRK by Stan v 0.3.63
#===============================================================================
#============ Parametry logowania do sterownika ================================
#     wpisz nr IP sterownika , swój login i hasło
c = sterownik('192.168.1.199', 'login', 'haslo');

#===============================================================================
#                         Parametry wspólne
#
# Tutaj wpisz parametry globalne pracy
#===============================================================================
#======== parametry CO ===============

tempZadanaGora = 50.2;
tempZadanaDol = 50;
tlo = 38;

#======== paramtery autoregulacji spalin
tspalin = 100
deltaspalin = 10
max_obr_dmuchawy = 52
tryb_autodopalania = False

#======== Korekta grupowa =============

czasPodawania = 0;
czasPrzerwy = 0;
czasNawiewu = 0;
mocNawiewu = 0;

#========== Parametry bloków ===============================================================

ile_krokow = 6;
czas_podawania = [5,0,0,3,0,0]
czas_przerwy = [20,30,60,13,20,100]
czas_nawiewu = [20,30,60,13,20,100]
moc_nawiewu = [46,43,40,43,40,40]
tryb = ['start','start','jeden_normal','normal','normal','stop']       # możliwe stany to - start, stop, normal, oba, jeden_start,

#=========== Parametry trybu Lato ==========================================================

T_zewnetrzna_lato = 15;
T_dolna_CWU = 44;
przerwa_minut = 60;
przerwa_podawanie = 5;
przerwa_nawiew_czas = 90;
przerwa_nawiew_moc = 41;

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
global autodopalanie
autodopalanie = False
ts060 = 0
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
    global autodopalanie
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
       #if x - 20 <= tempZadanaDol:
       #   print("a")
       #   autodopalanie = False
       #   wsp.start()
       #   return

       if ts060 <= -deltaspalin:
          print("b")
          autodopalanie = False
          wspaliny.start()
          return
      
       if ts060 < -deltaspalin and tts060 < 0:
          print("c")
          autodopalanie = False
          wspaliny.start()
          return

       if ts060 > 0 and ts061 < 0:
          print("d")
          autodopalanie = False
          wspaliny.start()
          return
      
       delta = tspalin - x
       moc = c.getDmuchawaMoc()
       if ts060 != 0:
          nowamoc = int(moc + delta/abs(ts060))
       else:
          nowamoc = moc
       
       if nowamoc > max_obr_dmuchawy:
          nowamoc = max_obr_dmuchawy

       if nowamoc < 25:
          nowamoc = 25
        
       print ("autospaliny TSpal: " + str(x) + " delta: "+ str(delta) +" moc: "+ str(moc) + " nowamoc: "+ str(nowamoc))
       c.setDmuchawaMoc(nowamoc)
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
        if (c.getTempCWU() >= T_dolna_CWU):
            if (c.getPompaCWU() == True):
             c.setPompaCWU(False);
    wcwu.start()

def uruchomBloki():
    wbl.stop()
    pracaBloki()

def stopPodajnik():
    global p
    wsp.stop()
    c.setPodajnik(False);
    p = 0

def stopDmuchawa():
    global d
    global autodopalanie
    global koniec
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
    if czPod > 0:
        c.setPodajnik(True);
        p = 1
        wsp.startInterval(czPod)
        
    if czNaw > 0:
        c.setDmuchawa(True);
        c.setDmuchawaMoc(moNaw);
        d = 1
        wsd.startInterval(czNaw)
        autodopalanie = asp
        
    while p != 0 or d != 0:
        time.sleep(0.01)
    
    return

#=========== FUNKCJA SPRAWDZENIA TMPERATURY CO ===============================================

def tempCO(tZadGora,tZadDol):
    global praca
    global hist
    if ((c.getTempCO()) < tZadDol):
        praca = 1
        hist = 1
        print ('warunek spełniony Todcz < Tzad dolnej - uruchamiam grzanie')
        print ("Temperatura CO: " + str(c.getTempCO()) + "°C")
    elif ((c.getTempCO()) > tZadGora + 0.2):
        praca = 0
        hist = 0
        print ('warunek spełniony Todcz > Tzad górnej - zatrzymuję grzanie')
        print ("Temperatura CO: " + str(c.getTempCO()) + "°C")
        time.sleep(5);
    elif hist == 1 and ((c.getTempCO()) < tZadGora + 0.2):
        praca = 1
        print ('warunek spełniony Todcz < Tzad górnej - kontynuuję grzanie')
        print ("Temperatura CO: " + str(c.getTempCO()) + "°C")
    else:
        praca = 0
        print ("Temperatura CO: " + str(c.getTempCO()) + "°C. Oczekiwanie.")
        time.sleep(5);

#================= Procedura przed startowa ==========================================

def procPStart(tempZadanaDol):
    while True:
          if (c.getTrybAuto() != True):
              c.setPompaCO(True);
              if ((c.getTempCO()) >= tempZadanaDol):
                  print ("Temperatura CO: " + str(c.getTempCO()) + "°C. Oczekiwanie.")
                  time.sleep(5);
              else:
                  break
     

#================ Tryb Lato ===========================================================

def trybLato(T_zewnetrzna_lato,T_dolna_CWU,przerwa_minut,przerwa_podawanie,przerwa_nawiew_czas,przerwa_nawiew_moc ):
        if (c.getTrybAuto() != True):
            print ("uruchamiam tryb LATO")
            c.setPompaCO(False);
            while (c.getTempZew()) > T_zewnetrzna_lato:
                    if (c.getTrybAuto() != True):
                        c.setPodajnik(True);
                        time.sleep(przerwa_podawanie)
                        c.setPodajnik(False);
                        c.setDmuchawa(True);
                        c.setDmuchawaMoc(przerwa_nawiew_moc);
                        time.sleep(przerwa_nawiew_czas);
                        przerwa_l = przerwa_minut
                        for l in range (0, przerwa_l):
                                if (c.getTrybAuto() != True):
                                    if ((c.getTempCWU()) < T_dolna_CWU):
                                        break
                                    if ((c.getTempCWU()) >= T_dolna_CWU):
                                        time.sleep(60);

def pracaBloki():
    global razy_jeden
    while True:
        licznik = 0
        if (c.getTrybAuto() != True):
            c.setPompaCO(True);
            tZadGora = tempZadanaGora
            tZadDol = tempZadanaDol
            tempCO(tZadGora,tZadDol)
            if (c.getTempZew()) > T_zewnetrzna_lato:
                trybLato(T_zewnetrzna_lato,T_dolna_CWU,przerwa_minut,przerwa_podawanie,przerwa_nawiew_czas,przerwa_nawiew_moc)
            if praca == 0 and (c.getTempCO()) < tempZadanaDol:
                razy_jeden = ile_krokow * [False];
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
                    TRYB = tryb[licznik]
                    asp = tryb_autodopalania

                    if ((c.getTempCO()) <= tempZadanaDol):
                        if TRYB == 'start':
                            print ("uruchamiam blok START nr " + str(licznik))
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                        if TRYB == 'jeden_start' and razy_jeden[licznik] == False:
                            print ("uruchamiam blok JEDEN_START nr " + str(licznik))
                            razy_jeden[licznik] = True
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                    if ((c.getTempCO()) < tempZadanaGora) and ((c.getTempCO()) > tempZadanaDol):
                        if TRYB == 'normal':
                            print ("uruchamiam blok NORMAL nr " + str(licznik))
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                        if TRYB == 'jeden_normal' and razy_jeden[licznik] == False:
                            print ("uruchamiam blok JEDEN_NORMAL nr " + str(licznik))
                            razy_jeden[licznik] = True
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                    if ((c.getTempCO()) >= tempZadanaGora):
                        if TRYB == 'stop':
                            print ("uruchamiam blok STOP nr " + str(licznik))
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                        if TRYB == 'jeden_stop' and razy_jeden[licznik] == False:
                            print ("uruchamiam blok JEDEN_STOP nr " + str(licznik))
                            razy_jeden[licznik] = True
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                    if ((c.getTempCO()) >= tempZadanaGora) or ((c.getTempCO()) <= tempZadanaDol):
                        if TRYB == 'oba':
                            print ("uruchamiam blok OBA nr " + str(licznik))
                            pracaPieca(czPod,czPrz,czNaw,moNaw,asp)
                    if tlo > 0:
                        c.setDmuchawa(True);
                        c.setDmuchawaMoc(tlo);
        
#=================================================================================================
#                  PROGRAM GŁÓWNY
#=================================================================================================
praca = 0
hist = 1
procPStart(tempZadanaDol)
wbl.startInterval(1)

try:
    while True:
        time.sleep(1);

finally:
    print ("Koncze dzialanie ...")
    wsd.stop()
    wsp.stop()
    wbl.stop()
    wcwu.stop()
    wspaliny.stop()
    wstatus.stop()
    c.setDmuchawa(False);
    c.setPodajnik(False);
    c.setPompaCWU(False);
    c.setPompaCO(False);
