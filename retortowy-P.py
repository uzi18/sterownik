#!/usr/bin/python
# -*- coding: utf-8 -*-

#==================================================================================
# Algorytm proporcjonalnej korekcji pracy (auto) w trybie retortowym-recznym
# z zalozenia nalezy dobrac parametry aby nie wychodzic w podtrzymanie
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
korekcja_postoju = 1.0
korekcja_dmuchania = 1.0

start_podawanie = 15
start_postoj = 35
start_dmuachawa = 43

czas_cyklu = 60

# PROGRAM GLOWNY
from sterownik import *
import time

c = sterownik(ip,login,password);
c.getStatus()
poprzednia_co = c.getTempCO()

while (c.getStatus()):
  if (c.getTrybAuto() && c.getTypKotla() == "RETORTOWY-RECZNY"):
    if (c.getTempCO() < zadana_co - 1):
      delta = int(zadana_co - c.getTempCO() +0.5)
      c.setRetRecznyDmuchawa( delta * korekcja_dmuchania + start_dmuachawa)
      c.setRetRecznyPostoj(   delta * korekcja_postoju   + start_postoj)
      c.setRetRecznyPodawanie(delta * korekcja_podawania + start_podawanie)
    else:
      c.setRetRecznyDmuchawa(start_dmuachawa)
      c.setRetRecznyPostoj(start_postoj)
      c.setRetRecznyPodawani(start_podawanie)
      
  poprzednia_co = c.getTempCO()
  time.sleep(czas_cyklu)
