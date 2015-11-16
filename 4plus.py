#!/usr/bin/python
# -*- coding: utf-8 -*-

# IMPORT BIBLIOTEKI
from sterownik import *
import threading, time
import signal, os

# AUTOR Mark3k. na bazie RECZNY "PLUS" by VERB + fragmenty kodu: Stan & uzi18 

# PARAMETRY  w pliku konf_4plus.py

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
                    if (c.getTempCO() < konf.tempMAX):
                        if (i == 2):
                        # ROZRUCH
                            i = 1;
                            print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. * Rozruch *");
                            print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                            print ("  Czas podawania rozruch: " + str(konf.czasPodajnikRozruch + konf.CzasPodawania) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaPraca + 2) + "%")
                            print ("  Czas nawiewu: " + str(konf.CzasNawiewu + konf.czasPrzedmuchPlus + 5) + "s")
                            c.setDmuchawa(True);
                            c.setDmuchawaMoc(konf.mocDmuchawaRozruch);
                            time.sleep(konf.czasDmuchawaRozruch);
                            c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch);
                            c.setPodajnik(True);
                            time.sleep(konf.czasPodajnikRozruch);
                            time.sleep(konf.CzasPodawania);
                            c.setPodajnik(False);
                            c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch);
                            time.sleep(konf.czasPrzedmuchPlus);
                            c.setDmuchawaMoc(konf.mocDmuchawaPraca + 2);
                            time.sleep(konf.CzasNawiewu);
                            k = 1;
                            
                        if (c.getTempCO() < konf.tempMAX):    # MOC-1  1:27
                            if (c.getTempCO() > konf.tempZadana):
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-1 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(konf.CzasPodawania) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaPraca - 6) + "%")
                                print ("  Czas nawiewu: " + str(konf.CzasNawiewu + 30 + konf.czasPrzedmuchPlus + 5) + "s   1:23 - 3s/67s")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch - 6);
                                time.sleep(5);
                                c.setPodajnik(True);
                                time.sleep(konf.CzasPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch - 6);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setDmuchawaMoc(konf.mocDmuchawaPraca - 6);
                                time.sleep(konf.CzasNawiewu + 30);
                                k = 1;
                        if (c.getTempCO() <= konf.tempZadana):   # MOC-2 1:18
                            if (c.getTempCO() > konf.tempMIN + 0.4):
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-2 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(konf.CzasPodawania) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaPraca - 3) + "%")
                                print ("  Czas nawiewu: " + str(konf.CzasNawiewu + 15 + konf.czasPrzedmuchPlus + 5) + "s   1:19 - 3s/57s")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch - 3);
                                time.sleep(5);
                                c.setPodajnik(True);
                                time.sleep(konf.CzasPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch - 3);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setDmuchawaMoc(konf.mocDmuchawaPraca - 3);
                                time.sleep(konf.CzasNawiewu + 15);
                                k = 1;
                        if (c.getTempCO() <= konf.tempMIN + 0.4):   # MOC-3
                            if (c.getTempCO() > konf.tempMIN):
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-3 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(konf.CzasPodawania) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaPraca - 1) + "%")
                                print ("  Czas nawiewu: " + str(konf.CzasNawiewu + 5 + konf.czasPrzedmuchPlus + 5) + "s   1:17 - 3s/51s")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch);
                                time.sleep(5);
                                c.setPodajnik(True);
                                time.sleep(konf.CzasPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setDmuchawaMoc(konf.mocDmuchawaPraca - 1);
                                time.sleep(konf.CzasNawiewu + 5);
                                k = 1;
                        if (c.getTempCO() <= konf.tempMIN):   # MOC-4
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-4 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(konf.CzasPodawania + 1) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaPraca + 2) + "%")
                                print ("  Czas nawiewu: " + str(konf.CzasNawiewu - 2 + konf.czasPrzedmuchPlus + 5) + "s   1:14 - 4s/55s")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 2);
                                time.sleep(5);
                                c.setPodajnik(True);
                                time.sleep(konf.CzasPodawania + 1);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 2);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setDmuchawaMoc(konf.mocDmuchawaPraca + 2);
                                time.sleep(konf.CzasNawiewu - 2);
                                k = 1;
                    else:
                        c.setPodajnik(False);
                        c.setDmuchawa(True);
                        if (k == 1):
                            # DOPALANIE
                            print ("* * DOPALANIE * *  CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C.");
                            print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                            print ("  Czas dopalania: " +  str(konf.czasDopalanie) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaDopalanie) + "%")
                            #c.setDmuchawaMoc(konf.mocDmuchawaTlo);
                            c.setDmuchawaMoc(konf.mocDmuchawaDopalanie);
                            time.sleep(konf.czasDopalanie);
                            k = 0;
                        c.setDmuchawa(False);
                        while True:
                            if (bool(c.getStatus())):
                                if (c.getTempCO() >= konf.tempMAX and c.getTempCO() < (konf.tempMAX + 8)):
                                    # ODSTAWIENIE
                                    print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. * TLO - ODSTAWIENIE *");
                                    print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                    print ("  * TLO *   Moc dmuchawy: " + str(konf.mocDmuchawaTlo) + "%")
                                    c.setDmuchawa(True);
                                    c.setDmuchawaMoc(konf.mocDmuchawaTlo);
                                    time.sleep(10);
                                #elif (c.getTempCO() <= konf.tempMAX):
                                    #c.setDmuchawa(False);
                                    #time.sleep(10);
                                    if wpod.is_running != True:
                                        wpod.startInterval(konf.podtrzymanie_postoj*60);
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
        if (c.getTempCO() > konf.tempZalaczeniaPomp):
            pompa = True
        if (c.getTempCO() < konf.tempZalaczeniaPomp - 1):
            pompa = False       
        if c.getTempCO() < c.getTempCWU():
            pompa = False          
        if (c.getTempCWU() > konf.T_dolna_CWU):
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
        if (c.getTempCO() > konf.tempZalaczeniaPomp):
            pompa = True
        if (c.getTempCO() < konf.tempZalaczeniaPomp):
            pompa = False      
        a = ''
        if konf.Tryb_autolato and c.getTempZew() > konf.T_zewnetrzna_lato and c.getTempWew() > 22.8:
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
    #c.setDmuchawaMoc(konf.mocDmuchawaRozruch + 2);
    #time.sleep(konf.czasDmuchawaRozruch);
    #c.setDmuchawaMoc(konf.podtrzymanie_mocNawiewu);
    c.setPodajnik(True);
    time.sleep(konf.podtrzymanie_podajnik);
    c.setPodajnik(False);
    print (" *&*  Start podajnik dokarmianie: " + str(konf.podtrzymanie_podajnik) + "s")
    #time.sleep(konf.podtrzymanie_nadmuch);
    #c.setDmuchawa(False);
    wpod.startInterval(konf.podtrzymanie_postoj*60);


wstatus = RTimer(status)
wstatus.startInterval(2)
wcwu = RTimer(regulatorCWU)
wcwu.startInterval(60)
wco = RTimer(regulatorCO)
wco.startInterval(30)
wpod = RTimer(podtrzymanie)


work();

