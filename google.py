#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
  import konf_google as konf
except ImportError:
  raise ImportError('brak pliku konfiguracji polaczenia z google: konf_google.py')

import os,sys,time
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials

json_key = json.load(open(os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+konf.certyfikat))
scope = ['https://spreadsheets.google.com/feeds']
credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)

#credentials.invalid

gc = gspread.authorize(credentials)

m = {}

while True:
  for plik in konf.lista_plikow:
    print ("Sprawdzam arkusz: "+plik)
    try:
      wks = gc.open(plik).worksheet("konfiguracja")
    except gspread.exceptions.SpreadsheetNotFound:
      print ("Brak arkusza "+ plik +" lub brak dostepu do arkusza dla uzytkownika: "+json_key['client_email']) 
      continue

    if not m.has_key(plik):
      m.update({plik:wks.updated})
    
    if m[plik] == wks.updated:
      continue
    
    do_aktualizacji = False
    parametry = wks.get_all_values()
    for x in parametry:
      if x[0] == 'aktualizacja':
        if x[1] != 'OK':
          do_aktualizacji = True
    
    if do_aktualizacji != True:
      continue

    print ("Arkusz zaktualizowano")
    zakladka = None
    for x in parametry:
      if x[0] == 'zakladka':
        zakladka = x[1]

    if zakladka == None:
      continue

    print ("Wybrano zakładkę: " + zakladka)

    try:
      wks = wks.spreadsheet.worksheet(zakladka)
    except:
      print ("Brak zakladki "+ zakladka) 
      m.update({plik:wks.updated})
      continue
    
    nowe = wks.get_all_values()
    
    dane = []
    try:
      p = open("konf_"+plik+".py")
      dane = p.readlines()
      p.close()
    except:
      print ("Problem z odczytem pliku konfiguracji: konf_"+plik+".py")
      continue

    koniec = ''
    if dane[0].endswith("\r\n"):
      koniec = "\r\n"
    else:
      koniec = "\n"

    print ("\nStare dane:")
    print (dane)

    print ("\nNowe dane:")
    print (nowe)
    
    
    for x in range(len(nowe)):
      if type(x) is not list or len(x) != 2:
        continue
      
      nowa_linia = nowe[x][0] +" = "+nowe[x][1]+koniec
      znalezione = False
      
      for y in range(len(dane)):
         if dane[y].startswith(nowe[x][0]):
            dane[y] = nowa_linia
            znalezione = True
      
      #if znalezione == False:
      #   dane.append(nowa_linia)
    
    print ("\nZaktualizowane dane:")
    print (dane)
    
    if konf.modyfikuj_pliki == True:
      print ("\nZapisuje dane !!")
      try:
        p = open("konf_"+plik+".py","w")
        p.writelines(dane)
        p.close()
      except:
        print ("Problem z zapisem do pliku konfiguracji: konf_"+plik+".py")
        continue
    else:
      print ("Plik nie został zaktualizowany - opcja: modyfikuj_pliki")
    
    try:
      wks = gc.open(plik).worksheet("konfiguracja")
      a = wks.find("aktualizacja")
      wks.update_cell(a.row,a.col+1,'OK')
      print ("Zaktualizowano arkusz: "+plik+" "+wks.updated)
    except:
      print ("Problem z aktualizacją arkusza")
      continue
    
    m.update({plik:wks.updated})
    
  time.sleep(10)

