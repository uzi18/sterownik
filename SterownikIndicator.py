#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import biblioteki
from sterownik import *

import sys
import gtk
import appindicator
import webbrowser

try:
  import konf_polaczenie
except ImportError:
  raise ImportError('brak pliku konfiguracji polaczenia ze sterownikiem: konf_polaczenie.py')

class SterownikIndicator:

        def __init__(self):
                
                self.c = sterownik(konf_polaczenie.ip, konf_polaczenie.login, konf_polaczenie.haslo);
                
                self.ind = appindicator.Indicator("SterownikIndicator", "emblem-web", appindicator.CATEGORY_APPLICATION_STATUS)
                self.ind.set_status(appindicator.STATUS_ACTIVE)
                self.ind.set_label("Sterownik")
                self.menu_setup()
                self.ind.set_menu(self.menu)
                
        def menu_setup(self):
                self.menu = gtk.Menu()
                self.menuinfo_item = gtk.MenuItem("Otwórz stronę sterownika w przeglądarce")
                self.menuinfo_item.connect("activate", self.openwww)
                self.menuinfo_item.show()
                self.menu.append(self.menuinfo_item)
                
                self.quit_item = gtk.MenuItem("Zamknij")
                self.quit_item.connect("activate", self.quit)
                self.quit_item.show()
                self.menu.append(self.quit_item)
        
        def main(self):
                self.refresh()
                gtk.main()
                
        def openwww(self, widget):
                webbrowser.open("http://" + g_address)
                
        def quit(self, widget):
                sys.exit(0)
                
        def refresh(self):
            if (bool(self.c.getStatus())):
                print ("CO: " + str(self.c.getTempCO()) + u"\u2103, Wew: " + str(self.c.getTempWew()) + u"\u2103, Zew: " + str(self.c.getTempZew()) + u"\u2103")
                self.ind.set_label("CO: " + str(self.c.getTempCO()) + u"\u2103, Wew: " + str(self.c.getTempWew()) + u"\u2103, Zew: " + str(self.c.getTempZew()) + u"\u2103")
            else:
                self.ind.set_label("Błąd");
                
            gtk.timeout_add(5000, self.refresh)

if __name__ == "__main__":
        indicator = SterownikIndicator()
        indicator.main()

