#!/usr/bin/python
# -*- coding: utf-8 -*-

# IMPORT BIBLIOTEKI
from sterownik import *
import threading, time
import signal, os

# AUTOR Mark3k. na bazie RECZNY "PLUS" by VERB + fragmenty kodu: Stan & uzi18 

# PARAMETRY CO
tempMAX = 48.5
tempZadana = 47.4;          # TEMPERATURA CO
tempMIN = 46.6;             # HISTEREZA

tempZalaczeniaPomp = 35.0

# PARAMETRY ROZRUCHU
mocDmuchawaRozruch = 70;    # MOC DMUCHAWY W ROZRUCHU
czasDmuchawaRozruch = 5;    # CZAS PRACY DMUCHAWY W ROZRUCHU
czasPodajnikRozruch = 2;    # DODATKOWY CZAS PRACY PODAJNIKA W ROZRUCHU (CzasPodawania + czasPodajnikRozruch)

# PARAMETRY PRACY
mocDmuchawaPraca = 40;      # MOC DMUCHAWY W CZASIE PRACY
mocDmuchawaPrzedmuch = 43;  # MOC DMUCHAWY W CZASIE PRZEDMUCHU
czasPrzedmuchPlus = 5;      # PRACA DMUCHAWY PO ZAKOŃCZENIU PRACY PODAJNIKA
CzasPodawania = 3;          # CZAS PRACY PODAJNIKA
CzasNawiewu = 47;           # CZAS POSTOJU PODAJNIKA

# PARAMETRY DOPALANIA
mocDmuchawaDopalanie = 35;  # MOC DMUCHAWY W CZASIE DOPALANIA
czasDopalanie = 40;        # CZAS PRACY DMUCHAWY W CZASIE DOPALANIA

# PARAMETRY TŁA
mocDmuchawaTlo = 30

# PARAMETRY CWU
T_dolna_CWU = 38;            # TEMPERATURA MIN CWU

# TRYB AUTOLATO
T_zewnetrzna_lato = 16.5
Tryb_autolato = True

#PODTRZYMANIE
podtrzymanie_postoj = 7 #w minutach
podtrzymanie_podajnik = 3
podtrzymanie_przerwa = 60
podtrzymanie_nadmuch = 60
podtrzymanie_mocNawiewu = 42

global praca

try:
  import konf_polaczenie
except ImportError:
  raise ImportError('brak pliku konfiguracji polaczenia ze sterownikiem: konf_polaczenie.py')

c = sterownik(konf_polaczenie.ip, konf_polaczenie.login, konf_polaczenie.haslo);
c.getStatus()

try:
  import konf_4plus as konf
except ImportError:
  raise ImportError('brak pliku konfiguracji parametrow pracy 4plus: konf_4plus.py')

from timer import *

def status():   # Ok. Działa
    wstatus.stop()
    c.getStatus()
    if c.getTrybAuto() == True:
       print ("*** UWAGA! sterownik w trybie AUTO")
    wstatus.start()
		
# WORK
def work():
    if (bool(c.getStatus())):
        if (c.getTrybAuto() != True):
            # URUCHOMIENIE
            k = 0;
            i = 2;
            #c.setPompaCO(True);
            # PRACA
            while True:
                #c.setPompaCO(True);
                if (bool(c.getStatus())):
                    while c.getTrybAuto(): # jesli tryb auto wlaczony to czekamy ...
                        c.getStatus()
                        time.sleep(5);
                    if (c.getTempCO() < tempMAX):
                        if (i == 2):
                        # ROZRUCH
                            i = 1;
                            print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. * Rozruch *");
                            print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                            print ("  Czas podawania rozruch: " + str(czasPodajnikRozruch + CzasPodawania) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaPraca + 2) + "%")
                            print ("  Czas nawiewu: " + str(CzasNawiewu + czasPrzedmuchPlus + 5) + "s")
                            c.setDmuchawa(True);
                            c.setDmuchawaMoc(mocDmuchawaRozruch);
                            time.sleep(czasDmuchawaRozruch);
                            c.setDmuchawaMoc(mocDmuchawaPrzedmuch);
                            c.setPodajnik(True);
                            time.sleep(czasPodajnikRozruch);
                            time.sleep(CzasPodawania);
                            c.setPodajnik(False);
                            c.setDmuchawaMoc(mocDmuchawaPrzedmuch);
                            time.sleep(czasPrzedmuchPlus);
                            c.setDmuchawaMoc(mocDmuchawaPraca + 2);
                            time.sleep(CzasNawiewu);
                            k = 1;
                            
                        if (c.getTempCO() < tempMAX):    # MOC-1  1:27
                            if (c.getTempCO() > tempZadana):
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-1 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(CzasPodawania) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaPraca - 6) + "%")
                                print ("  Czas nawiewu: " + str(CzasNawiewu + 30 + czasPrzedmuchPlus + 5) + "s   1:23 - 3s/67s")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch - 6);
                                time.sleep(5);
                                c.setPodajnik(True);
                                time.sleep(CzasPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch - 6);
                                time.sleep(czasPrzedmuchPlus);
                                c.setDmuchawaMoc(mocDmuchawaPraca - 6);
                                time.sleep(CzasNawiewu + 30);
                                k = 1;
                        if (c.getTempCO() <= tempZadana):   # MOC-2 1:18
                            if (c.getTempCO() > tempMIN + 0.4):
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-2 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(CzasPodawania) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaPraca - 3) + "%")
                                print ("  Czas nawiewu: " + str(CzasNawiewu + 15 + czasPrzedmuchPlus + 5) + "s   1:19 - 3s/57s")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch - 3);
                                time.sleep(5);
                                c.setPodajnik(True);
                                time.sleep(CzasPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch - 3);
                                time.sleep(czasPrzedmuchPlus);
                                c.setDmuchawaMoc(mocDmuchawaPraca - 3);
                                time.sleep(CzasNawiewu + 15);
                                k = 1;
                        if (c.getTempCO() <= tempMIN + 0.4):   # MOC-3
                            if (c.getTempCO() > tempMIN):
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-3 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(CzasPodawania) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaPraca - 1) + "%")
                                print ("  Czas nawiewu: " + str(CzasNawiewu + 5 + czasPrzedmuchPlus + 5) + "s   1:17 - 3s/51s")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch);
                                time.sleep(5);
                                c.setPodajnik(True);
                                time.sleep(CzasPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch);
                                time.sleep(czasPrzedmuchPlus);
                                c.setDmuchawaMoc(mocDmuchawaPraca - 1);
                                time.sleep(CzasNawiewu + 5);
                                k = 1;
                        if (c.getTempCO() <= tempMIN):   # MOC-4
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-4 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(CzasPodawania + 1) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaPraca + 2) + "%")
                                print ("  Czas nawiewu: " + str(CzasNawiewu - 2 + czasPrzedmuchPlus + 5) + "s   1:14 - 4s/55s")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 2);
                                time.sleep(5);
                                c.setPodajnik(True);
                                time.sleep(CzasPodawania + 1);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 2);
                                time.sleep(czasPrzedmuchPlus);
                                c.setDmuchawaMoc(mocDmuchawaPraca + 2);
                                time.sleep(CzasNawiewu - 2);
                                k = 1;
                    else:
                        c.setPodajnik(False);
                        c.setDmuchawa(True);
                        if (k == 1):
                            # DOPALANIE
                            print ("* * DOPALANIE * *  CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C.");
                            print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                            print ("  Czas dopalania: " +  str(czasDopalanie) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaDopalanie) + "%")
                            #c.setDmuchawaMoc(mocDmuchawaTlo);
                            c.setDmuchawaMoc(mocDmuchawaDopalanie);
                            time.sleep(czasDopalanie);
                            k = 0;
                        c.setDmuchawa(False);
                        while True:
                            if (bool(c.getStatus())):
                                if (c.getTempCO() >= tempMAX and c.getTempCO() < (tempMAX + 8)):
                                    # ODSTAWIENIE
                                    print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. * TLO - ODSTAWIENIE *");
                                    print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                    print ("  * TLO *   Moc dmuchawy: " + str(mocDmuchawaTlo) + "%")
                                    c.setDmuchawa(True);
                                    c.setDmuchawaMoc(mocDmuchawaTlo);
                                    time.sleep(10);
                                #elif (c.getTempCO() <= tempMAX):
                                    #c.setDmuchawa(False);
                                    #time.sleep(10);
                                    if wpod.is_running != True:
                                        wpod.startInterval(podtrzymanie_postoj*60);
                                else:
                                    if wpod.is_running == True:
                                        wpod.stop()
                                    break;
                        i = 2;

                else:
                    print ("Odczyt statusu sie nie powiodl.");
                    c.setDmuchawa(False);
                    c.setPodajnik(False);
                    break
                                

def regulatorCWU():
    wcwu.stop()

    if (c.getTrybAuto() != True):
        #print ("Regulator CWU...")
        if (c.getTempCO() > tempZalaczeniaPomp):
            pompa = True
        if (c.getTempCO() < tempZalaczeniaPomp - 1):
            pompa = False       
        if c.getTempCO() < c.getTempCWU():
            pompa = False          
        if (c.getTempCWU() > T_dolna_CWU):
            pompa = False
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
        #print ("Regulator CO...")
        #print time.strftime("%Y:%m:%d__%H:%M:%S")
        if (c.getTempCO() > tempZalaczeniaPomp):
            pompa = True
        if (c.getTempCO() < tempZalaczeniaPomp):
            pompa = False      
        a = ''
        if Tryb_autolato and c.getTempZew() > T_zewnetrzna_lato and c.getTempWew() > 22.8:
            pompa = False
            a = "AUTOLATO"           
        if (pompa and c.getPompaCO() == False):
            c.setPompaCO(True)
            print ("*** CO->ON")
        elif (not pompa and c.getPompaCO() == True):
            c.setPompaCO(False)
            print ("*** CO->OFF " + a)
    
    wco.start()


def podtrzymanie():
    wpod.stop();
    print ("***Podtrzymanie***")
    print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
    #c.setDmuchawa(True);
    #c.setDmuchawaMoc(mocDmuchawaRozruch + 2);
    #time.sleep(czasDmuchawaRozruch);
    #c.setDmuchawaMoc(podtrzymanie_mocNawiewu);
    c.setPodajnik(True);
    time.sleep(podtrzymanie_podajnik);
    c.setPodajnik(False);
    print (" *&*  Start podajnik dokarmianie: " + str(podtrzymanie_podajnik) + "s")
    #time.sleep(podtrzymanie_nadmuch);
    #c.setDmuchawa(False);
    wpod.startInterval(podtrzymanie_postoj*60);


wstatus = RTimer(status)
wstatus.startInterval(2)
wcwu = RTimer(regulatorCWU)
wcwu.startInterval(60)
wco = RTimer(regulatorCO)
wco.startInterval(30)
wpod = RTimer(podtrzymanie)


work();

