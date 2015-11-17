#!/usr/bin/python
# -*- coding: utf-8 -*-

# IMPORT BIBLIOTEKI
from sterownik import *
import threading, time
import signal, os

# AUTOR Mark3k. na bazie RECZNY "PLUS" by VERB + fragmenty kodu: Stan & uzi18 

# PARAMETRY  w pliku konf_10plush.py

try:
  import konf_polaczenie
except ImportError:
  raise ImportError('brak pliku konfiguracji polaczenia ze sterownikiem: konf_polaczenie.py')

c = sterownik(konf_polaczenie.ip, konf_polaczenie.login, konf_polaczenie.haslo);
c.getStatus()

try:
  import konf_10plush as konf
except ImportError:
  raise ImportError('brak pliku konfiguracji parametrow pracy 10plush: konf_10plush.py')

from timer import *

global praca

global kold
global knew
global nowakonfiguracja
nowakonfiguracja = False

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
        if os.path.isfile(f) and os.path.basename(f) == 'konf_10plush.py':
           nowakonfiguracja = True

    for f in added:
        if os.path.isfile(f) and os.path.basename(f) == 'konf_10plush.py':
           nowakonfiguracja = True

def status():   # Ok. Działa
    wstatus.stop()
    c.getStatus()
    if c.getTrybAuto() == True:
       print ("*** UWAGA! sterownik w trybie AUTO")
    wstatus.start()

global k
global i

# URUCHOMIENIE
k = 0
i = 2

# WORK
def work():
            wwork.stop();
            # PRACA
            while True:
                #c.setPompaCO(True);
                if (bool(c.getStatus())):
                    while c.getTrybAuto(): # jesli tryb auto wlaczony to czekamy ...
                        c.getStatus()
                        time.sleep(5);
                    if (c.getTempCO() <= konf.tempZadana):
                        if (i == 2):
                        # ROZRUCH
                            i = 1;
                            print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. * Rozruch *");
                            print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                            print ("  Czas podawania rozruch: " + str(konf.czasPodajnikRozruch+konf.CzasPodawania)+"s"+"   Moc dmuchawy: "+ str(konf.mocDmuchawaPraca+11)+"%")
                            print ("  Czas nawiewu: " + str(konf.CzasNawiewu - 40 + konf.czasPrzedmuchPlus * 2) + "s"  + "   1:14")
                            c.setDmuchawa(True);
                            c.setDmuchawaMoc(konf.mocDmuchawaRozruch);
                            time.sleep(konf.czasDmuchawaRozruch);
                            c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 11);
                            c.setPodajnik(True);
                            time.sleep(konf.czasPodajnikRozruch);
                            time.sleep(konf.CzasPodawania + konf.korektaPodawania);
                            c.setPodajnik(False);
                            c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 11);
                            time.sleep(konf.czasPrzedmuchPlus);
                            c.setDmuchawaMoc(konf.mocDmuchawaPraca + 11);
                            time.sleep(konf.CzasNawiewu - konf.korektaDmuchawy * 4);
                            k = 1;
                            
                        if (c.getTempCO() <= konf.tempZadana):             # 49.0 MOC-1  1:37
                            if (c.getTempCO() > konf.tempZadana - konf.histereza):   # 48.7
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MIN POWER *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(konf.CzasPodawania) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaPraca) + "%")
                                print ("  Czas nawiewu: " + str(konf.CzasNawiewu + konf.czasPrzedmuchPlus * 2) + "s   1:37")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(konf.CzasPodawania + konf.korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setDmuchawaMoc(konf.mocDmuchawaPraca);
                                time.sleep(konf.CzasNawiewu);
                                k = 1;
                        if (c.getTempCO() <= konf.tempZadana - konf.histereza):         # 48.7   MOC-2 1:33
                            if (c.getTempCO() > konf.tempZadana - konf.histereza * 2):  # 48.4
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-2 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(konf.CzasPodawania) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaPraca + 1) + "%")
                                print ("  Czas nawiewu: " + str(konf.CzasNawiewu - konf.korektaDmuchawy * 1 + konf.czasPrzedmuchPlus * 2) + "s   1:33")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 1);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(konf.CzasPodawania + konf.korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 1);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setDmuchawaMoc(konf.mocDmuchawaPraca + 1);
                                time.sleep(konf.CzasNawiewu - konf.korektaDmuchawy * 1);
                                k = 1;
                        if (c.getTempCO() <= konf.tempZadana - konf.histereza * 2):     # 48.4  MOC-3 1:30
                            if (c.getTempCO() > konf.tempZadana - konf.histereza * 3):  # 48.1
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-3 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(konf.CzasPodawania) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaPraca + 2) + "%")
                                print ("  Czas nawiewu: " + str(konf.CzasNawiewu - konf.korektaDmuchawy * 2 + konf.czasPrzedmuchPlus * 2) + "s   1:30")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 2);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(konf.CzasPodawania + konf.korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 2);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setDmuchawaMoc(konf.mocDmuchawaPraca + 2);
                                time.sleep(konf.CzasNawiewu - konf.korektaDmuchawy * 2);
                                k = 1;
                        if (c.getTempCO() <= konf.tempZadana - konf.histereza * 3):      # 48.1  MOC-4  1:27
                            if (c.getTempCO() > konf.tempZadana - konf.histereza * 4):   # 47.8
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-4 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(konf.CzasPodawania) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaPraca + 3) + "%")
                                print ("  Czas nawiewu: " + str(konf.CzasNawiewu - konf.korektaDmuchawy * 3 + konf.czasPrzedmuchPlus * 2) + "s   1:27")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 3);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(konf.CzasPodawania + konf.korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 3);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setDmuchawaMoc(konf.mocDmuchawaPraca + 3);
                                time.sleep(konf.CzasNawiewu - konf.korektaDmuchawy * 3);
                                k = 1;
                        if (c.getTempCO() <= konf.tempZadana - konf.histereza * 4):        # 47.8  MOC-5  1:23
                            if (c.getTempCO() > konf.tempZadana - konf.histereza * 5):     # 47.5
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-5 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(konf.CzasPodawania) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaPraca + 4) + "%")
                                print ("  Czas nawiewu: " + str(konf.CzasNawiewu - konf.korektaDmuchawy * 4 + konf.czasPrzedmuchPlus * 2) + "s   1:23")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 4);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(konf.CzasPodawania + konf.korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 4);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setDmuchawaMoc(konf.mocDmuchawaPraca + 4);
                                time.sleep(konf.CzasNawiewu - konf.korektaDmuchawy * 4);
                                k = 1;
                        if (c.getTempCO() <= konf.tempZadana - konf.histereza * 5):         # 47.5  MOC-6  1:20
                            if (c.getTempCO() > konf.tempZadana - konf.histereza * 6):      # 47.2
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-6 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(konf.CzasPodawania) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaPraca + 5) + "%")
                                print ("  Czas nawiewu: " + str(konf.CzasNawiewu - konf.korektaDmuchawy * 4.8 + konf.czasPrzedmuchPlus * 2) + "s   1:20")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch +5);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(konf.CzasPodawania + konf.korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 5);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setDmuchawaMoc(konf.mocDmuchawaPraca + 5);
                                time.sleep(konf.CzasNawiewu - konf.korektaDmuchawy * 4.8);
                                k = 1;
                        if (c.getTempCO() <= konf.tempZadana - konf.histereza * 7):         # 47.2  MOC-7  1:17
                            if (c.getTempCO() > konf.tempZadana - konf.histereza * 8):      # 46.9
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-7 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(konf.CzasPodawania) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaPraca + 6) + "%")
                                print ("  Czas nawiewu: " + str(konf.CzasNawiewu - konf.korektaDmuchawy * 5.6 + konf.czasPrzedmuchPlus * 2) + "s   1:17")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 6);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(konf.CzasPodawania + konf.korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 6);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setDmuchawaMoc(konf.mocDmuchawaPraca + 6);
                                time.sleep(konf.CzasNawiewu - konf.korektaDmuchawy * 5.6);
                                k = 1;
                        if (c.getTempCO() <= konf.tempZadana - konf.histereza * 8):         # 46.9  MOC-8  1:14
                            if (c.getTempCO() > konf.tempZadana - konf.histereza * 9):      # 46.6
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-8 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(konf.CzasPodawania) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaPraca + 7) + "%")
                                print ("  Czas nawiewu: " + str(konf.CzasNawiewu - konf.korektaDmuchawy * 6.4 + konf.czasPrzedmuchPlus * 2) + "s   1:14")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 7);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(konf.CzasPodawania + konf.korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 7);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setDmuchawaMoc(konf.mocDmuchawaPraca + 7);
                                time.sleep(konf.CzasNawiewu - konf.korektaDmuchawy * 6.2);
                                k = 1;
                        if (c.getTempCO() <= konf.tempZadana - konf.histereza * 9):         # 46.6  MOC-9  1:12
                            if (c.getTempCO() > konf.tempZadana - konf.histereza * 10):      # 46.3
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MOC-9 *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(konf.CzasPodawania) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaPraca + 8) + "%")
                                print ("  Czas nawiewu: " + str(konf.CzasNawiewu - konf.korektaDmuchawy * 7.2 + konf.czasPrzedmuchPlus * 2) + "s   1:12")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 8);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(konf.CzasPodawania + konf.korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 8);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setDmuchawaMoc(konf.mocDmuchawaPraca + 8);
                                time.sleep(konf.CzasNawiewu - konf.korektaDmuchawy * 6.8);
                                k = 1;
                        if (c.getTempCO() <= konf.tempZadana - konf.histereza * 10):          # 46.3  MOC-10  1:10
                                print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. Praca * MAX POWER *");
                                print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                print ("  Czas podawania: " + str(konf.CzasPodawania) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaPraca + 10) + "%")
                                print ("  Czas nawiewu: " + str(konf.CzasNawiewu - konf.korektaDmuchawy * 8 + konf.czasPrzedmuchPlus * 2) + "s   1:10")
				c.setDmuchawa(True);	
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 11);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setPodajnik(True);
                                time.sleep(konf.CzasPodawania + konf.korektaPodawania);
                                c.setPodajnik(False);
                                c.setDmuchawaMoc(konf.mocDmuchawaPrzedmuch + 11);
                                time.sleep(konf.czasPrzedmuchPlus);
                                c.setDmuchawaMoc(konf.mocDmuchawaPraca + 12);
                                time.sleep(konf.CzasNawiewu - konf.korektaDmuchawy * 7.5);
                                k = 1;
                    else:
                        c.setPodajnik(False);
                        c.setDmuchawa(True);
                        if (k == 1):
                            # DOPALANIE
                            print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C.  * * DOPALANIE * *")
                            print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                            print ("  Czas dopalania: " +  str(konf.czasDopalanie) + "s" + "   Moc dmuchawy: " + str(konf.mocDmuchawaDopalanie) + "%")
                            #c.setDmuchawaMoc(konf.mocDmuchawaTlo);
                            c.setDmuchawaMoc(konf.mocDmuchawaDopalanie);
                            time.sleep(konf.czasDopalanie);
                            k = 0;
                        c.setDmuchawa(False);
                        while True:
                            if (bool(c.getStatus())):
                                if (c.getTempCO() > konf.tempZadana and c.getTempCO() < (konf.tempZadana + 8)):
                                    # ODSTAWIENIE + TLO
                                    print ("CO: " + str(c.getTempCO()) + "°C." + "   Spaliny: " + str(c.getTempSpaliny()) + "°C. * TLO - ODSTAWIENIE *");
                                    print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
                                    print ("  * TLO *   Moc dmuchawy: " + str(konf.mocDmuchawaTlo) + "%")
                                    c.setDmuchawa(True);
                                    c.setDmuchawaMoc(konf.mocDmuchawaTlo);
                                    time.sleep(10);
                                #elif (c.getTempCO() <= konf.tempZadana):
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
    print ("*** PODTRZYMANIE ***")
    print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
    #c.setDmuchawa(True);
    #c.setDmuchawaMoc(konf.mocDmuchawaRozruch + 2);
    #time.sleep(konf.czasDmuchawaRozruch);
    #c.setDmuchawaMoc(konf.podtrzymanie_mocNawiewu);
    c.setPodajnik(True);
    time.sleep(konf.podtrzymanie_podajnik);
    c.setPodajnik(False);
    print (" *&*  Start podajnik DOKARMIANIE: " + str(konf.podtrzymanie_podajnik) + "s")
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
wwork = RTimer(work)
wwork.startInterval(2)
kold = files_to_timestamp(os.path.abspath(os.path.dirname(sys.argv[0])))
wkonf = RTimer(konfig)
wkonf.startInterval(10)

try:
  while True:
    if nowakonfiguracja == True:
        print time.strftime("Data: %Y.%m.%d  Czas: %H.%M:%S")
        print ('== Konfiguracja: Wczytywanie ...')
        reload(sys.modules["konf_10plush"])
        nowakonfiguracja = False
    time.sleep(0.2);

finally:
    print ("Kończę działanie ...")
    c.setDmuchawa(False);
    c.setPodajnik(False);
    c.setPompaCWU(False);
    c.setPompaCO(False);
    os.kill(os.getpid(), signal.SIGTERM)

