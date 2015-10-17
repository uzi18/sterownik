#!/usr/bin/python
# -*- coding: utf-8 -*-

#==================================================================================
# Algorytm proporcjonalnej korekcji pracy (auto) w trybie retortowym-recznym
# z zalozenia nalezy dobrac tak parametry aby nie wychodzic w podtrzymanie
#
# pomysl kol. janusz z forum http://esterownik.pl/forum
# pomysl z korekcjami kol. mark3k
#==================================================================================

# PARAMETRY
ip = '192.168.2.2'
login = 'admin'
password = 'admin'

zadana_co = 65

korekcja_podawania = 1.0
korekcja_postoju =  10.0
korekcja_dmuchania = 0.5

start_podawanie = 15
start_postoj = 35
start_dmuchawa = 43

czas_cyklu = 60

# PROGRAM GLOWNY
from sterownik import *
import time

c = sterownik(ip,login,password);
c.getStatus()
poprzednia_co = c.getTempCO()

while (c.getStatus()):
  if (c.getTrybAuto() && c.getTypKotla() == "RETORTOWY-RECZNY"):
    delta = int(zadana_co - c.getTempCO() +0.5)
    delta_poprzednia = int(poprzednia_co - c.getTempCO() +0.5)
    
    if (c.getTempCO() < zadana_co - 1):
      nowe_podawanie = delta * korekcja_podawania + start_podawanie
      nowe_postoj    = delta * korekcja_postoju   + start_postoj
      nowe_dmuchanie = delta * korekcja_dmuchania + start_dmuchawa
      c.setRetRecznyDmuchawa(nowe_dmuchanie)
      c.setRetRecznyPostoj(nowe_postoj)
      c.setRetRecznyPodawanie(nowe_podawanie)
      print("NOWE   Delta:"+ str(delta)+" dmuchanie:" + str(nowe_dmuchanie) + " podawanie:" + str(nowe_podawanie) + " postoj:" + str(nowe_postoj))
    elif (delta_poprzednia > 0):
      c.setRetRecznyDmuchawa(start_dmuchawa)
      c.setRetRecznyPostoj(start_postoj)
      c.setRetRecznyPodawani(start_podawanie)
      print("POWROT Delta:"+ str(delta)+" dmuchanie:" + str(start_dmuchawa) + " podawanie:" + str(start_podawanie) + " postoj:" + str(start_postoj))
      
  poprzednia_co = c.getTempCO()
  time.sleep(czas_cyklu)
