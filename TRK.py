#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import biblioteki
from sterownik import *
import threading
import time;
#===============================================================================
#               TRK by Stan v 0.3.62
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
ile_razy_jeden = 1;                                                    # jeden_normal, jeden_stop,

#=========== Parametry trybu Lato ==========================================================

T_zewnętrzna_lato = 15;
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
    if (bool(c.getStatus())):
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
    return praca

#================= Procedura przed startowa ==========================================

def procPStart(tempZadanaDol):
    while True:
        if (bool(c.getStatus())):
            if (c.getTrybAuto() != True):
                c.setPompaCO(True);
                if ((c.getTempCO()) >= tempZadanaDol):
                    print ("Temperatura CO: " + str(c.getTempCO()) + "°C. Oczekiwanie.")
                    time.sleep(30);
                else:
                    return


#================ Tryb Lato ===========================================================

def trybLato(T_zewnętrzna_lato,T_dolna_CWU,przerwa_minut,przerwa_podawanie,przerwa_nawiew_czas,przerwa_nawiew_moc ):
    if (bool(c.getStatus())):
        if (c.getTrybAuto() != True):
            c.setPompaCO(False);
            while (c.getTempZew()) > T_zewnętrzna_lato:
                if (bool(c.getStatus())):
                    if (c.getTrybAuto() != True):
                        c.setPodajnik(True);
                        time.sleep(przerwa_podawanie)
                        c.setPodajnik(False);
                        c.setDmuchawa(True);
                        c.setDmuchawaMoc(przerwa_nawiew_moc);
                        time.sleep(przerwa_nawiew_czas);
                        przerwa_l = 60 * przerwa_minut
                        for 1 in range (0, przerwa_l):
                            if (bool(c.getStatus())):
                                if (c.getTrybAuto() != True):
                                    if ((c.getTempCWU()) < T_dolna_CWU):
                                        c.setPompaCWU(True);
                                        break
                                    if ((c.getTempCWU()) >= T_dolna_CWU):
                                        time.sleep(60);
return




#=================================================================================================
#                  PROGRAM GŁÓWNY
#=================================================================================================
praca = 0
hist = 1
jeden_licznik = 0
procPStart(tempZadanaDol)
while True:
    licznik = 0
    if (bool(c.getStatus())):
        if (c.getTrybAuto() != True):
            c.setPompaCO(True);
            tZadGora = tempZadanaGora
            tZadDol = tempZadanaDol
            tempCO(tZadGora,tZadDol)
            if (c.getTempZew()) > T_zewnętrzna_lato:
                def trybLato(T_zewnętrzna_lato,T_dolna_CWU,przerwa_minut,przerwa_podawanie,przerwa_nawiew_czas,przerwa_nawiew_moc ):
            if (c.getTempCO()) < tempZadanaDol:
                jeden_licznik = 0
            for licznik in range(0,ile_krokow):
                if praca == 1:
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
                            print (TRYB)
                            pracaPieca(czPod,czPrz,czNaw,moNaw)
                        if TRYB == 'jeden_start' and jeden_licznik < ile_razy_jeden:
                            print ("uruchamiam blok JEDEN_START nr " + str(licznik))
                            print (TRYB)
                            jeden_licznik += 1
                            pracaPieca(czPod,czPrz,czNaw,moNaw)
                    if ((c.getTempCO()) < tempZadanaGora):
                        if ((c.getTempCO()) > tempZadanaDol):
                            if TRYB == 'normal':
                                print ("uruchamiam blok NORMAL nr " + str(licznik))
                                print (TRYB)
                                pracaPieca(czPod,czPrz,czNaw,moNaw)
                            if TRYB == 'jeden_normal' and jeden_licznik < ile_razy_jeden:
                                print ("uruchamiam blok JEDEN_NORMAL nr " + str(licznik))
                                print (TRYB)
                                jeden_licznik += 1
                                pracaPieca(czPod,czPrz,czNaw,moNaw)
                    if ((c.getTempCO()) >= tempZadanaGora):
                        if TRYB == 'stop':
                            print ("uruchamiam blok STOP nr " + str(licznik))
                            print (TRYB)
                            pracaPieca(czPod,czPrz,czNaw,moNaw)
                        if TRYB == 'jeden_stop' and jeden_licznik < ile_razy_jeden:
                            print ("uruchamiam blok JEDEN_STOP nr " + str(licznik))
                            print (TRYB)
                            jeden_licznik += 1
                            pracaPieca(czPod,czPrz,czNaw,moNaw)
                    if ((c.getTempCO()) >= tempZadanaGora) or ((c.getTempCO()) <= tempZadanaDol):
                        if TRYB == 'oba':
                            print ("uruchamiam blok OBA nr " + str(licznik))
                            print (TRYB)
                            pracaPieca(czPod,czPrz,czNaw,moNaw)
                    if tlo > 0:
                        c.setDmuchawa(True);
                        c.setDmuchawaMoc(tlo);





