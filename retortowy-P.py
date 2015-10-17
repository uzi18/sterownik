#!/usr/bin/python
# -*- coding: utf-8 -*-

#==================================================================================
# Algorytm proporcjonalnej korekcji pracy (auto) w trybie retortowym-recznym
# z zalozenia mialby nie wychodzic w podtrzymanie.
#
# pomysl kol. janusz z forum http://esterownik.pl/forum
#==================================================================================

from sterownik import *
import threading, time

