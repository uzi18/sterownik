#!/usr/bin/python
# -*- coding: utf-8 -*-

#==================================================================================
# Algorytm proporcjonalnej korekcji pracy (auto) w trybie retortowym-recznym
# z zalozenia nalezy dobrac tak parametry aby nie wychodzic w podtrzymanie
#
# pomysl algorytmu kol. janusz z forum http://esterownik.pl/forum
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

rozped_podawanie= start_podawanie
rozped_postoj   = start_postoj
rozped_dmuchawa = start_dmuchawa


# PROGRAM GLOWNY
from sterownik import *
import time

rozped = True
c = sterownik(ip,login,password)
c.getStatus()
c.setRetRecznyDmuchawa(rozped_dmuchawa)
c.setRetRecznyPostoj(rozped_postoj)
c.setRetRecznyPodawanie(rozped_podawanie)
poprzednia_co = c.getTempCO()
poprzednie_dmuchanie = nowe_dmuchanie = rozped_dmuchawa
poprzednie_postoj = nowe_postoj = rozped_postoj
poprzednie_podawanie = nowe_podawanie = rozped_podawanie

while (c.getStatus()):
  if (c.getTrybAuto() and c.getTypKotla() == "RETORTOWY-RECZNY"):
    delta = int(zadana_co - c.getTempCO() +0.5)
    delta_poprzednia = int(poprzednia_co - c.getTempCO() +0.5)
    
    if (c.getTempCO() < zadana_co or rozped == False):
      nowe_podawanie = int(delta * korekcja_podawania + start_podawanie)
      nowe_postoj    = int(delta * korekcja_postoju   + start_postoj)
      nowe_dmuchanie = int(delta * korekcja_dmuchania + start_dmuchawa)
      if (nowe_podawanie <= 0): nowe_podawanie = 1
      if (nowe_postoj    <= 0): nowe_postoj = 1
      if (nowe_dmuchanie <=25): nowe_dmuchanie = 25
      rozped = True
      print("NOWE   Delta:"+ str(delta)+" dmuchanie:" + str(nowe_dmuchanie) + " podawanie:" + str(nowe_podawanie) + " postoj:" + str(nowe_postoj))
    elif (delta_poprzednia >= 0 and delta <= 0 and rozped == True):
      nowe_dmuchanie = rozped_dmuchawa
      nowe_postoj = rozped_postoj
      nowe_podawanie =rozped_podawanie
      rozped = False
      print("ROZPED Delta:"+ str(delta)+" dmuchanie:" + str(rozped_dmuchawa) + " podawanie:" + str(rozped_podawanie) + " postoj:" + str(rozped_postoj))
    else:
      print("Delta:"+ str(delta)+" Poprzednia:" + str(delta_poprzednia))

  else:
    print("Sterownik nie jest w trybie auto lub nie ma wlaczonego trybu RETORTOWY-RECZNY")

  if (nowe_dmuchanie <> poprzednie_dmuchanie):
    c.setRetRecznyDmuchawa(nowe_dmuchanie)
    poprzednie_dmuchanie = nowe_dmuchanie

  if (nowe_postoj <> poprzednie_postoj):
    c.setRetRecznyPostoj(nowe_postoj)
    poprzednie_postoj = nowe_postoj

  if (nowe_podawanie <> poprzednie_podawanie):
    c.setRetRecznyPodawanie(nowe_podawanie)
    poprzednie_podawanie = nowe_podawanie

  poprzednia_co = c.getTempCO()
  time.sleep(czas_cyklu)
