#!/usr/bin/python
# -*- coding: utf-8 -*-

# IMPORT BIBLIOTEKI
from sterownik import *
import threading, time
import signal, os

# AUTOR Mark3k. na bazie RECZNY "PLUS" by VERB + fragmenty kodu: Stan & uzi18 

# PARAMETRY CO
tempZadana = 50.0           # TEMPERATURA CO
#tempZadana1 = 48.4;        # TEMP Zadana CO
#tempMIN = 47.0;             
histereza = 0.3             # HISTEREZA
korektaDmuchawy = 10        # KOREKTA DMUCHAWY
korektaPodawania = 0        # KOREKTA PODAWANIA

tempZalaczeniaPomp = 35.0

# PARAMETRY ROZRUCHU
mocDmuchawaRozruch = 60;    # MOC DMUCHAWY W ROZRUCHU
czasDmuchawaRozruch = 6;    # CZAS PRACY DMUCHAWY W ROZRUCHU
czasPodajnikRozruch = 2;    # DODATKOWY CZAS PRACY PODAJNIKA W ROZRUCHU (CzasPodawania + czasPodajnikRozruch)

# PARAMETRY PRACY
mocDmuchawaPraca = 31;      # MOC DMUCHAWY W CZASIE PRACY
mocDmuchawaPrzedmuch = 34;  # MOC DMUCHAWY W CZASIE PRZEDMUCHU
czasPrzedmuchPlus = 5;      # PRACA DMUCHAWY PO ZAKOŃCZENIU PRACY PODAJNIKA
CzasPodawania = 3;          # CZAS PRACY PODAJNIKA
CzasNawiewu = 100;          # CZAS POSTOJU PODAJNIKA

# PARAMETRY DOPALANIA
mocDmuchawaDopalanie = 31;  # MOC DMUCHAWY W CZASIE DOPALANIA
czasDopalanie = 30;         # CZAS PRACY DMUCHAWY W CZASIE DOPALANIA

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
                    if (c.getTempCO() <= tempZadana):
                        if (i == 2):
                        # ROZRUCH
                            i = 1;
                            print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. * Rozruch *");
                            print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                            print ("  Czas podawania rozruch: " + str(czasPodajnikRozruch+CzasPodawania)+"s"+"   Moc dmuchawy: "+ str(mocDmuchawaPraca+11)+"%")
                            print ("  Czas nawiewu: " + str(CzasNawiewu - 40 + czasPrzedmuchPlus * 2) + "s"  + "   1:14")
                            c.setDmuchawa(True);
                            c.setDmuchawaMoc(mocDmuchawaRozruch);
                            time.sleep(czasDmuchawaRozruch);
                            c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 11);
                            c.setPodajnik(True);
                            time.sleep(czasPodajnikRozruch);
                            time.sleep(CzasPodawania + korektaPodawania);
                            c.setPodajnik(False);
                            c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 11);
                            time.sleep(czasPrzedmuchPlus);
                            c.setDmuchawaMoc(mocDmuchawaPraca + 11);
                            time.sleep(CzasNawiewu - korektaDmuchawy * 4);
                            k = 1;
                            
                        if (c.getTempCO() <= tempZadana):             # 49.0 MOC-1  1:37
                            if (c.getTempCO() > tempZadana - histereza):   # 48.7
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MIN POWER *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(CzasPodawania) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaPraca) + "%")
                                print ("  Czas nawiewu: " + str(CzasNawiewu + czasPrzedmuchPlus * 2) + "s   1:37")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch);
                                time.sleep(czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(CzasPodawania + korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch);
                                time.sleep(czasPrzedmuchPlus);
                                c.setDmuchawaMoc(mocDmuchawaPraca);
                                time.sleep(CzasNawiewu);
                                k = 1;
                        if (c.getTempCO() <= tempZadana - histereza):         # 48.7   MOC-2 1:33
                            if (c.getTempCO() > tempZadana - histereza * 2):  # 48.4
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-2 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(CzasPodawania) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaPraca + 1) + "%")
                                print ("  Czas nawiewu: " + str(CzasNawiewu - korektaDmuchawy * 1 + czasPrzedmuchPlus * 2) + "s   1:33")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 1);
                                time.sleep(czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(CzasPodawania + korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 1);
                                time.sleep(czasPrzedmuchPlus);
                                c.setDmuchawaMoc(mocDmuchawaPraca + 1);
                                time.sleep(CzasNawiewu - korektaDmuchawy * 1);
                                k = 1;
                        if (c.getTempCO() <= tempZadana - histereza * 2):     # 48.4  MOC-3 1:30
                            if (c.getTempCO() > tempZadana - histereza * 3):  # 48.1
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-3 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(CzasPodawania) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaPraca + 2) + "%")
                                print ("  Czas nawiewu: " + str(CzasNawiewu - korektaDmuchawy * 2 + czasPrzedmuchPlus * 2) + "s   1:30")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 2);
                                time.sleep(czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(CzasPodawania + korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 2);
                                time.sleep(czasPrzedmuchPlus);
                                c.setDmuchawaMoc(mocDmuchawaPraca + 2);
                                time.sleep(CzasNawiewu - korektaDmuchawy * 2);
                                k = 1;
                        if (c.getTempCO() <= tempZadana - histereza * 3):      # 48.1  MOC-4  1:27
                            if (c.getTempCO() > tempZadana - histereza * 4):   # 47.8
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-4 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(CzasPodawania) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaPraca + 3) + "%")
                                print ("  Czas nawiewu: " + str(CzasNawiewu - korektaDmuchawy * 3 + czasPrzedmuchPlus * 2) + "s   1:27")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 3);
                                time.sleep(czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(CzasPodawania + korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 3);
                                time.sleep(czasPrzedmuchPlus);
                                c.setDmuchawaMoc(mocDmuchawaPraca + 3);
                                time.sleep(CzasNawiewu - korektaDmuchawy * 3);
                                k = 1;
                        if (c.getTempCO() <= tempZadana - histereza * 4):        # 47.8  MOC-5  1:23
                            if (c.getTempCO() > tempZadana - histereza * 5):     # 47.5
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-5 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(CzasPodawania) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaPraca + 4) + "%")
                                print ("  Czas nawiewu: " + str(CzasNawiewu - korektaDmuchawy * 4 + czasPrzedmuchPlus * 2) + "s   1:23")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 4);
                                time.sleep(czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(CzasPodawania + korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 4);
                                time.sleep(czasPrzedmuchPlus);
                                c.setDmuchawaMoc(mocDmuchawaPraca + 4);
                                time.sleep(CzasNawiewu - korektaDmuchawy * 4);
                                k = 1;
                        if (c.getTempCO() <= tempZadana - histereza * 5):         # 47.5  MOC-6  1:20
                            if (c.getTempCO() > tempZadana - histereza * 6):      # 47.2
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-6 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(CzasPodawania) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaPraca + 5) + "%")
                                print ("  Czas nawiewu: " + str(CzasNawiewu - korektaDmuchawy * 4.8 + czasPrzedmuchPlus * 2) + "s   1:20")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch +5);
                                time.sleep(czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(CzasPodawania + korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 5);
                                time.sleep(czasPrzedmuchPlus);
                                c.setDmuchawaMoc(mocDmuchawaPraca + 5);
                                time.sleep(CzasNawiewu - korektaDmuchawy * 4.8);
                                k = 1;
                        if (c.getTempCO() <= tempZadana - histereza * 7):         # 47.2  MOC-7  1:17
                            if (c.getTempCO() > tempZadana - histereza * 8):      # 46.9
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-7 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(CzasPodawania) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaPraca + 6) + "%")
                                print ("  Czas nawiewu: " + str(CzasNawiewu - korektaDmuchawy * 5.6 + czasPrzedmuchPlus * 2) + "s   1:17")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 6);
                                time.sleep(czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(CzasPodawania + korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 6);
                                time.sleep(czasPrzedmuchPlus);
                                c.setDmuchawaMoc(mocDmuchawaPraca + 6);
                                time.sleep(CzasNawiewu - korektaDmuchawy * 5.6);
                                k = 1;
                        if (c.getTempCO() <= tempZadana - histereza * 8):         # 46.9  MOC-8  1:14
                            if (c.getTempCO() > tempZadana - histereza * 9):      # 46.6
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-8 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(CzasPodawania) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaPraca + 7) + "%")
                                print ("  Czas nawiewu: " + str(CzasNawiewu - korektaDmuchawy * 6.4 + czasPrzedmuchPlus * 2) + "s   1:14")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 7);
                                time.sleep(czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(CzasPodawania + korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 7);
                                time.sleep(czasPrzedmuchPlus);
                                c.setDmuchawaMoc(mocDmuchawaPraca + 7);
                                time.sleep(CzasNawiewu - korektaDmuchawy * 6.2);
                                k = 1;
                        if (c.getTempCO() <= tempZadana - histereza * 9):         # 46.6  MOC-9  1:12
                            if (c.getTempCO() > tempZadana - histereza * 10):      # 46.3
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-9 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(CzasPodawania) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaPraca + 8) + "%")
                                print ("  Czas nawiewu: " + str(CzasNawiewu - korektaDmuchawy * 7.2 + czasPrzedmuchPlus * 2) + "s   1:12")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 8);
                                time.sleep(czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(CzasPodawania + korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 8);
                                time.sleep(czasPrzedmuchPlus);
                                c.setDmuchawaMoc(mocDmuchawaPraca + 8);
                                time.sleep(CzasNawiewu - korektaDmuchawy * 6.8);
                                k = 1;
                        if (c.getTempCO() <= tempZadana - histereza * 10):          # 46.3  MOC-10  1:10
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MAX POWER *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(CzasPodawania) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaPraca + 10) + "%")
                                print ("  Czas nawiewu: " + str(CzasNawiewu - korektaDmuchawy * 8 + czasPrzedmuchPlus * 2) + "s   1:10")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 11);
                                time.sleep(czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(CzasPodawania + korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(mocDmuchawaPrzedmuch + 11);
                                time.sleep(czasPrzedmuchPlus);
                                c.setDmuchawaMoc(mocDmuchawaPraca + 12);
                                time.sleep(CzasNawiewu - korektaDmuchawy * 7.5);
                                k = 1;
                    else:
                        c.setPodajnik(False);
                        c.setDmuchawa(True);
                        if (k == 1):
                            # DOPALANIE
                            print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C.  * * DOPALANIE * *")
                            print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                            print ("  Czas dopalania: " +  str(czasDopalanie) + "s" + "   Moc dmuchawy: " + str(mocDmuchawaDopalanie) + "%")
                            #c.setDmuchawaMoc(mocDmuchawaTlo);
                            c.setDmuchawaMoc(mocDmuchawaDopalanie);
                            time.sleep(czasDopalanie);
                            k = 0;
                        c.setDmuchawa(False);
                        while True:
                            if (bool(c.getStatus())):
                                if (c.getTempCO() > tempZadana and c.getTempCO() < (tempZadana + 8)):
                                    # ODSTAWIENIE + TLO
                                    print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. * TLO - ODSTAWIENIE *");
                                    print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                    print ("  * TLO *   Moc dmuchawy: " + str(mocDmuchawaTlo) + "%")
                                    c.setDmuchawa(True);
                                    c.setDmuchawaMoc(mocDmuchawaTlo);
                                    time.sleep(10);
                                #elif (c.getTempCO() <= tempZadana):
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
    print ("*** PODTRZYMANIE ***")
    print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
    #c.setDmuchawa(True);
    #c.setDmuchawaMoc(mocDmuchawaRozruch + 2);
    #time.sleep(czasDmuchawaRozruch);
    #c.setDmuchawaMoc(podtrzymanie_mocNawiewu);
    c.setPodajnik(True);
    time.sleep(podtrzymanie_podajnik);
    c.setPodajnik(False);
    print (" *&*  Start podajnik DOKARMIANIE: " + str(podtrzymanie_podajnik) + "s")
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

