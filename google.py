#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
  import konf_google as konf
except ImportError:
  raise ImportError('brak pliku konfiguracji polaczenia z google: konf_google.py')

import time
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
json_key = json.load(open(konf.certyfikat))
scope = ['https://spreadsheets.google.com/feeds']
credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)

#credentials.invalid

gc = gspread.authorize(credentials)

m = {}

while True:
  for plik in konf.lista_plikow:
    try:
      wks = gc.open(plik).worksheet("konfiguracja")
      #sheet1
    except SpreadsheetNotFound:
      print ("Brak arkusza "+ plik +" lub brak dostepu do arkusza dla uzytkownika: "+json_key['client_email']) 
      break

    if not m.has_key(plik):
      m.update({plik:wks.updated})
    
    if m[plik] == wks.updated:
      break
    
    m.update({plik:wks.updated})
    
    do_aktualizacji = False
    parametry = wks.get_all_values()
    for x in parametry:
      if x[0] == 'aktualizacja':
        if x[1] != 'OK':
          do_aktualizacji = True
    
    if do_aktualizacji != True:
      break

    zakladka = None
    for x in parametry:
      if x[0] == 'zakladka':
        zakladka = x[1]

    if zakladka == None:
      break

    try:
      wks = wks.spreadsheet.worksheet(zakladka)
    except:
      print ("Brak zakladki "+ zakladka) 
      m.update({plik:wks.updated})
      break
    
    nowe = wks.get_all_values()
    print (nowe)
    
    p = open("konf_"+plik+".py")
    dane = p.readlines()
    p.close()
    
    for x in nowe:
      for t in dane:
        if t.startswith(x[0]):
          print t
          
    #p = open("konf_"+plik+".py","w")
    #p.writelines(dane)
    #p.close()
    
    wks = gc.open(plik).sheet1
    a = wks.find("aktualizacja")
    wks.update_cell(a.row,a.col+1,'OK')
    print ("zaktualizowano plik: "+plik+" "+wks.updated)
    m.update({plik:wks.updated})
    
  time.sleep(10)