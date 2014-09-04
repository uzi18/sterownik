#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import biblioteki
from sterownik import *

import sys
import gtk
import appindicator
import webbrowser

g_address = '192.168.0.111'
g_user = 'admin'
g_pass = 'admin'

class SterownikIndicator:

	def __init__(self):
		
		self.c = sterownik(g_address, g_user, g_pass);
		
		self.ind = appindicator.Indicator("SterownikIndicator", "emblem-web", appindicator.CATEGORY_APPLICATION_STATUS)
		self.ind.set_status(appindicator.STATUS_ACTIVE)
		self.ind.set_label("Sterownik")
		self.menu_setup()
		self.ind.set_menu(self.menu)
		
	def menu_setup(self):
		self.menu = gtk.Menu()
		self.menuinfo_item = gtk.MenuItem("Otwórz stronê sterownika w przegl¹darce")
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
			self.ind.set_label("CO: " + str(self.c.getTempCO()) + u"\u2103, Wew: " + str(self.c.getTempWew()) + u"\u2103, Zew: " + str(self.c.getTempZew()) + u"\u2103")
		else:
			self.ind.set_label("B³¹d");

		gtk.timeout_add(5000, self.refresh)
			

		
if __name__ == "__main__":
	indicator = SterownikIndicator()
	indicator.main()

