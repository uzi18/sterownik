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
razy_jeden = ile_krokow * [False];                                     # jeden_normal, jeden_stop,

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
    x = c.getTempSpaliny()
    daneTSpal.pop(0)
    daneTSpal.append(x)
    ts020 = daneTSpal[-1] - daneTSpal[-3]
    ts060 = daneTSpal[-1] - daneTSpal[-1 -1 * 6 * 1]
    ts120 = daneTSpal[-1] - daneTSpal[-1 -1 * 6 * 2]
    ts180 = daneTSpal[-1] - daneTSpal[-1 -1 * 6 * 3]
    print ("trend TSpal: " + str(ts020) + "/20s "+ str(ts060) + "/60s "+ str(ts120) + "/120s "+ str(ts180) + "/180s")

def status():
    c.getStatus()

def regulatorCWU():
    print ("Watek regulator CWU...")
    if (c.getTrybAuto() != True):
        if (c.getTempCO() >= T_dolna_CWU):
            if (c.getTempCWU() < T_dolna_CWU):
                if (c.getPompaCWU() == False):
                    c.setPompaCWU(True);
        if (c.getTempCWU() >= T_dolna_CWU):
            if (c.getPompaCWU() == True):
             c.setPompaCWU(False);

c.getStatus()    
daneTSpal = []
x = c.getTempSpaliny()
# 60 * 10s.
for y in range(60):
    daneTSpal.append(x) 

wstatus = RTimer(status)
wstatus.startInterval(1)
wspaliny = RTimer(spaliny)
wspaliny.startInterval(10) # co 10s.
wcwu = RTimer(regulatorCWU)
wcwu.startInterval(10)

#========= FUNKCJA PRACA PIECA ==============================================================

def pracaPieca(czPod,czPrz,czNaw,moNaw):
    a = 1
    b = czPrz
    if czNaw >= czPrz:
        czNaw = czPrz
    if czPod > 0:
        c.setPodajnik(True);
    if czNaw > 0:
        c.setDmuchawa(True);
        c.setDmuchawaMoc(moNaw);
        
    while a <= b:
        time.sleep(1)
        a += 1
        if czPod < a:
           c.setPodajnik(False);
        if czNaw < a:
           c.setDmuchawa(False);
    
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
        time.sleep(15);
    elif hist == 1 and ((c.getTempCO()) < tZadGora + 0.2):
        praca = 1
        print ('warunek spełniony Todcz < Tzad górnej - kontynuuję grzanie')
        print ("Temperatura CO: " + str(c.getTempCO()) + "°C")
    else:
        praca = 0
        print ("Temperatura CO: " + str(c.getTempCO()) + "°C. Oczekiwanie.")
        time.sleep(5);
        
    return

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
                        przerwa_l = 60 * przerwa_minut
                        for l in range (0, przerwa_l):
                                if (c.getTrybAuto() != True):
                                    if ((c.getTempCWU()) < T_dolna_CWU):
                                        break
                                    if ((c.getTempCWU()) >= T_dolna_CWU):
                                        time.sleep(60);

#=================================================================================================
#                  PROGRAM GŁÓWNY
#=================================================================================================
praca = 0
hist = 1
try:
    procPStart(tempZadanaDol)
    while True:
        licznik = 0
        if (c.getTrybAuto() != True):
            c.setPompaCO(True);
            tZadGora = tempZadanaGora
            tZadDol = tempZadanaDol
            tempCO(tZadGora,tZadDol)
            if (c.getTempZew()) > T_zewnetrzna_lato:
                trybLato(T_zewnetrzna_lato,T_dolna_CWU,przerwa_minut,przerwa_podawanie,przerwa_nawiew_czas,przerwa_nawiew_moc)
            if (c.getTempCO()) < tempZadanaDol:
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

                    if ((c.getTempCO()) <= tempZadanaDol):
                        if TRYB == 'start':
                            print ("uruchamiam blok START nr " + str(licznik))
                            pracaPieca(czPod,czPrz,czNaw,moNaw)
                        if TRYB == 'jeden_start' and razy_jeden[licznik] == False:
                            print ("uruchamiam blok JEDEN_START nr " + str(licznik))
                            razy_jeden[licznik] = True
                            pracaPieca(czPod,czPrz,czNaw,moNaw)
                    if ((c.getTempCO()) < tempZadanaGora):
                        if ((c.getTempCO()) > tempZadanaDol):
                            if TRYB == 'normal':
                                print ("uruchamiam blok NORMAL nr " + str(licznik))
                                pracaPieca(czPod,czPrz,czNaw,moNaw)
                            if TRYB == 'jeden_normal' and razy_jeden[licznik] == False:
                                print ("uruchamiam blok JEDEN_NORMAL nr " + str(licznik))
                                razy_jeden[licznik] = True
                                pracaPieca(czPod,czPrz,czNaw,moNaw)
                    if ((c.getTempCO()) >= tempZadanaGora):
                        if TRYB == 'stop':
                            print ("uruchamiam blok STOP nr " + str(licznik))
                            pracaPieca(czPod,czPrz,czNaw,moNaw)
                        if TRYB == 'jeden_stop' and razy_jeden[licznik] == False:
                            print ("uruchamiam blok JEDEN_STOP nr " + str(licznik))
                            print (TRYB)
                            razy_jeden[licznik] = True
                            pracaPieca(czPod,czPrz,czNaw,moNaw)
                    if ((c.getTempCO()) >= tempZadanaGora) or ((c.getTempCO()) <= tempZadanaDol):
                        if TRYB == 'oba':
                            print ("uruchamiam blok OBA nr " + str(licznik))
                            pracaPieca(czPod,czPrz,czNaw,moNaw)
                    if tlo > 0:
                        c.setDmuchawa(True);
                        c.setDmuchawaMoc(tlo);

finally:
    wstatus.stop()
    wspaliny.stop()
    wcwu.stop()
    c.setDmuchawa(False);
    c.setPodajnik(False);
    c.setPompaCWU(False);
    c.setPompaCO(False);
