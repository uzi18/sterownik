#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import biblioteki
from sterownik import *
import threading
import time;

#Nowy obiekt sterownika
c = sterownik('192.168.0.112', 'admin', 'admin');
	
# Funkcja wyświetlająca na ekranie podstawowe informacje 
def printStatus():
	# Odczytujemy status, funkcaj zwraca True jeżeli odczyt się powiódł
	if (bool(c.getStatus())):
		print ("");
		print ("Czy włączony tryb auto: " + str(c.getTrybAuto()));
		print ("Praca podajnika: " + str(c.getPodajnik()));
		print ("Dmuchawa praca: " + str(c.getDmuchawa()) + ", Moc: " + str(c.getDmuchawaMoc()) + "%");
		print ("Praca pompy CO: " + str(c.getPompaCO()));
		print ("Praca pompy CWU: " + str(c.getPompaCWU()));
		print ("Praca pompy mieszającej/obiegowej: " + str(c.getPompaMieszObieg()));
		
		print ("Temperatura wewnętrzna: " + str(c.getTempWew()) + "°C");
		print ("Temperatura zewnętrzna: " + str(c.getTempZew()) + "°C");
		print ("Temperatura CWU: " + str(c.getTempCWU()) + "°C");
		print ("Temperatura powrotu: " + str(c.getTempPowrot()) + "°C");
		print ("Temperatura podajnika: " + str(c.getTempPodajnik()) + "°C");
		print ("Temperatura CO: " + str(c.getTempCO()) + "°C");
		print ("Temperatura spalin: " + str(c.getTempSpaliny()) + "°C");
		
# Test wyjść sterownika
def test(): # Załączenie wszystkich wyjść i po 3 sekundach wyłączenie
	if (bool(c.getStatus())):
		if (c.getTrybAuto() != True):
			# Ustawienie mocy dmuchawy w procentach
			c.setDmuchawaMoc(51);
			# Właczenie dmuchawy
			c.setDmuchawa(True);
			# Właczenie podajnika
			c.setPodajnik(True);
			# Włączenie pompy CO
			c.setPompaCO(True);
			# Włączenie pompy CWU
			c.setPompaCWU(True);

			printStatus();
			time.sleep(3);

			# Wyłaczenie dmuchawy
			c.setDmuchawa(False);
			# Wyłaczenie podajnika
			c.setPodajnik(False);
			# Wyłączenie pompy CO
			c.setPompaCO(False);
			# Wyłącznie pompy CWU
			c.setPompaCWU(False);
			
			printStatus();
		else:
			printStatus();
			print ("\n\nUwaga: Nie jesteśmy w trybie ręcznym");
			
	else:
		print ("Odczyt statusu się nie powiódł");

test();

