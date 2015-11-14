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

podawanie_min = 0
podawanie_max = 0
postoj_min = 0
postoj_max = 0
dmuchanie_min = 0
dmuchanie_max = 0

kg_na_minute = 0.240
praca_ciagla = True
moc_100 = 1.0/1.0
zadana_co = 65

korekcja_podawania=  2.5
korekcja_postoju  =-10.0
korekcja_dmuchania=  1.0

start_podawanie=  5
start_postoj   =105
start_dmuchawa = 38

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
poprzednie_opoznienie = 0
start_czas_podajnika = c.getCzasPodajnika()
start_czas = time.time()

if (praca_ciagla == True):
  c.setZadanaCO(zadana_co+5)
else:
  c.setZadanaCO(zadana_co)

if (c.version == "BRULI"):
  pod_min = 2
  pod_max = 180
else:
  pod_min = 3
  pod_max = 20

pos_min = 1
pos_max = 600
dmu_min = 25
dmu_max = 100

if (podawanie_min > 0 and podawanie_min > pod_min): pod_min = podawanie_min
if (podawanie_max > 0 and podawanie_max < pod_max): pod_max = podawanie_max
if (postoj_min > 0    and postoj_min > pos_min):    pos_min = postoj_min
if (postoj_max > 0    and postoj_max < pos_max):    pos_max = postoj_max
if (dmuchanie_min > 0 and dmuchanie_min > dmu_min): dmu_min = dmuchanie_min
if (dmuchanie_max > 0 and dmuchanie_max < dmu_max): dmu_max = dmuchanie_max

tryb_info = False
delta_ujemna = False

while (c.getStatus()):
  if (c.getTrybAuto() and c.getTypKotla() == "RETORTOWY-RECZNY"):
    tryb_info = False
    delta = int(zadana_co - c.getTempCO() +0.5)
    delta_poprzednia = int(poprzednia_co - c.getTempCO() +0.5)
    
    if (delta > 0 or praca_ciagla == True):
      #if (delta_ujemna == True and praca_ciagla == True): c.setZadanaCO(zadana_co+5)
      delta_ujemna = False
      nowe_podawanie = delta * korekcja_podawania + start_podawanie
      nowe_postoj    = delta * korekcja_postoju   + start_postoj
      nowe_dmuchanie = delta * korekcja_dmuchania + start_dmuchawa
      
      if (nowe_podawanie < 1):
        x = 1-nowe_podawanie
        nowe_podawanie = 1
        nowe_postoj = nowe_postoj + x
      
      nowe_moc = float(nowe_postoj)/float(nowe_podawanie)
      
      if (nowe_podawanie < pod_min):
        nowe_podawanie = pod_min
        nowe_postoj = int(nowe_moc*pod_min)
      if (nowe_podawanie > pod_max):
        nowe_podawanie = pod_max
        nowe_postoj = int(nowe_moc*pod_max)
      if (nowe_postoj    < pos_min): nowe_postoj = pos_min
      if (nowe_postoj    > pos_max): nowe_postoj = pos_max
      if (nowe_dmuchanie < dmu_min): nowe_dmuchanie = dmu_min
      if (nowe_dmuchanie > dmu_max): nowe_dmuchanie = dmu_max
      rozped = True
      rozped = False
    elif (delta < 0 and praca_ciagla == False):
      #if (delta_ujemna == False): c.setZadanaCO(zadana_co)
      delta_ujemna = True
        
    #  nowe_dmuchanie = rozped_dmuchawa
    #  nowe_postoj = rozped_postoj
    #  nowe_podawanie =rozped_podawanie
    #  rozped = False
    #  print("ROZPED Delta:"+ str(delta)+" dmuchanie:" + str(rozped_dmuchawa) + " podawanie:" + str(rozped_podawanie) + " postoj:" + str(rozped_postoj))
    #else:
    #  print("Delta:"+ str(delta)+" Poprzednia:" + str(delta_poprzednia))

  else:
    if (tryb_info == False):
      tryb_info = True
      print("Sterownik nie jest w trybie auto lub nie ma wlaczonego trybu RETORTOWY-RECZNY")

  nowe_dane = False
  if (nowe_dmuchanie != poprzednie_dmuchanie):
    c.setRetRecznyDmuchawa(nowe_dmuchanie)
    print(" dmuchanie:" + str(poprzednie_dmuchanie)+"->" + str(nowe_dmuchanie))
    poprzednie_dmuchanie = nowe_dmuchanie
    nowe_dane = True

  if (nowe_postoj != poprzednie_postoj):
    c.setRetRecznyPostoj(nowe_postoj)
    print(" postoj:" + str(poprzednie_postoj)+"->" + str(nowe_postoj))
    poprzednie_postoj = nowe_postoj
    nowe_dane = True

  if (nowe_podawanie != poprzednie_podawanie):
    c.setRetRecznyPodawanie(nowe_podawanie)
    print(" podawanie: " + str(poprzednie_podawanie)+"->" + str(nowe_podawanie))
    poprzednie_podawanie = nowe_podawanie
    nowe_dane = True

  if (nowe_dane == True):
    ile_min = (time.time() - start_czas)/60
    ile_kg = (c.getCzasPodajnika()-start_czas_podajnika)*kg_na_minute
    ile_kg_min = ile_kg / ile_min
    print("Nowa moc: " +str(int(100*(float(nowe_podawanie)/float(nowe_postoj))/moc_100))+"% "\
      + "%0.3f kg " % (ile_kg) + "%0.3f kg/min" % (ile_kg_min) + " %0.3f kg/24h" % (ile_kg_min*60*24))
    print("Delta:"+ str(delta)+" dmuchanie:" + str(nowe_dmuchanie) + " podawanie:" + str(nowe_podawanie) + " postoj:" + str(nowe_postoj))
    nowe_dane = False
  
  poprzednia_co = c.getTempCO()
  opoznienie = int(nowe_postoj+nowe_podawanie-2)/2
  if (opoznienie <= 0):
    opoznienie = 1
  if (poprzednie_opoznienie != opoznienie):
    print(" opoznienie: " + str(poprzednie_opoznienie) + "->" + str(opoznienie))
    poprzednie_opoznienie = opoznienie

  time.sleep(opoznienie)
