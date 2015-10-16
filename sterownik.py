#!/usr/bin/python
# -*- coding: utf-8 -*-


# Licencja GNU/GPL
# Uwaga ! Firma Elektro-System s.c. nie ponosi odpowiedzialności z tytułu ewentualnych szkód powstałych w wyniku działania biblioteki i/lub algorytmów powstałych przy jej użyciu.

__author__ = "Maciej Komur (elektro-system s.c.)"
__date__ = "01-10-2014"
__version__ = "0.2"
# modyfikacje: Bartłomiej Zimoń

import urllib
    
import httplib2
import struct
import sys
import threading
import time

from base64 import b64encode

class sterownik:
        
        s_address = '127.0.0.';
        s_user = 'admin';
        s_password = 'admin';
        s_statusdata = None;
        s_typ_kotla = None
        h = None;
        last_res = None
        last_content = None
        testuj = False
        ile_razy_testuj = 20
        __temp=lambda self,hi,lo:((hi<<8|lo)-(hi>>7<<16))/10.0

        def __init__(self, address, user, password):
                """Konstruktor. Podajemy adres sterownika (adres ip), login i hasło"""
                self.s_address = address;
                self.s_user = user;
                self.s_password = password;
                self.crcTable = [0, 49, 98, 83, 196, 245,166, 151,185, 136,219, 234,125, 76, 31, 46, 67, 114,33, 16,
                135, 182,229, 212,250, 203,152, 169,62, 15, 92, 109,134, 183,228, 213,66, 115,32, 17,
                63, 14, 93, 108,251, 202,153, 168,197, 244,167, 150,1, 48, 99, 82, 124, 77, 30, 47,
                184, 137,218, 235,61, 12, 95, 110,249, 200,155, 170,132, 181,230, 215,64, 113,34, 19,
                126, 79, 28, 45, 186, 139,216, 233,199, 246,165, 148,3, 50, 97, 80, 187, 138,217, 232,
                127, 78, 29, 44, 2, 51, 96, 81, 198, 247,164, 149,248, 201,154, 171,60, 13, 94, 111,
                65, 112,35, 18, 133, 180,231, 214,122, 75, 24, 41, 190, 143,220, 237,195, 242,161, 144,
                7, 54, 101, 84, 57, 8, 91, 106,253, 204,159, 174,128, 177,226, 211,68, 117,38, 23,
                252, 205,158, 175,56, 9, 90, 107,69, 116,39, 22, 129, 176,227, 210,191, 142,221, 236,
                123, 74, 25, 40, 6, 55, 100, 85, 194, 243,160, 145,71, 118,37, 20, 131, 178,225, 208,
                254, 207,156, 173,58, 11, 88, 105,4, 53, 102, 87, 192, 241,162, 147,189, 140,223, 238,
                121, 72, 27, 42, 193, 240,163, 146,5, 52, 103, 86, 120, 73, 26, 43, 188, 141,222, 239,
                130, 179,224, 209,70, 119,36, 21, 59, 10, 89, 104,255, 206,157, 172];
                self.h = httplib2.Http()
                self.h.add_credentials(self.s_user, self.s_password)
                self.testuj = False;
                self.lock = threading.RLock()
                
        def setIleProb(self, potw):
                self.testuj = potw
            
        def getStatus(self):
                """Pobiera status ze sterownika i zapamiętuje go"""
                try:
                        self._getRequest("02010006000000006103")
                        
                        if (self.last_res.status == 200):
                                txt = str(self.last_content);
                                txt = txt[txt.index('[') + 1:txt.index(']')]
                                data = list(map(int, txt.split(',')));
                                self.s_statusdata = data;
                                return True;
                        else:
                                self.s_statusdata = None;
                                print ("Błąd: " + self.res.read());
                                return False
                except:
                        self.s_statusdata = None;
                        print ("Błąd: ", sys.exc_info()[0])
                        return False
                        
        def _getRequest(self, req):
                
                try:
                        with self.lock:
                             #time.sleep(0.001)
                             self.last_res, self.last_content = self.h.request("http://" + self.s_address + "/?com=" + req, "GET")
                        
                        if (self.last_res.status == 200):
                                return True;
                        else:
                                print ("Błąd: " + self.last_content);
                                return False
                except:
                        print ('Błąd: ', sys.exc_info()[0]);
                        return False
                        
        def getTrybAuto(self):
                """Zwraca True - jeżeli sterownik jest w trybie auto, False - jeżeli w trybie ręcznym"""
                if (bool(self.s_statusdata)):
                        return (self.s_statusdata[34] == 1);
                      
        def setTrybAuto(self, state):
            test = False
            for x in range(self.ile_razy_testuj):
                if (state):
                    test = self._getRequest("020100020033020001006503");
                else:
                    test = self._getRequest("020100020033020000009103");
                if (self.last_res.status == 200 ):
                    break
            
            return test

        #Temperatury
        def getTempWew(self):
                if (bool(self.s_statusdata)):
                        return self.__temp(self.s_statusdata[19],self.s_statusdata[18]);

        def getTempZew(self):
                if (bool(self.s_statusdata)):
                        return self.__temp(self.s_statusdata[21],self.s_statusdata[20]);
                        
        def getTempCWU(self):
                if (bool(self.s_statusdata)):
                        return self.__temp(self.s_statusdata[23],self.s_statusdata[22]);
                        
        def getTempPowrot(self):
                if (bool(self.s_statusdata)):
                        return self.__temp(self.s_statusdata[25],self.s_statusdata[24]);
                        
        def getTempPodajnik(self):
                if (bool(self.s_statusdata)):
                        return self.__temp(self.s_statusdata[27],self.s_statusdata[26]);

        def getTempCO(self):
                if (bool(self.s_statusdata)):
                        return self.__temp(self.s_statusdata[29],self.s_statusdata[28]);
                
        def getTempSpaliny(self):
                if (bool(self.s_statusdata)):
                        return self.__temp(self.s_statusdata[31],self.s_statusdata[30]);

        # Pompa CO
        def getPompaCO(self):
                if (bool(self.s_statusdata)):
                        return self.s_statusdata[32] & (1 << 2) != 0;

        def setPompaCO(self, state):
            test = False
            for x in range(self.ile_razy_testuj):
                if (state):
                    test = self._getRequest("02010005000D0100018D03");
                else:
                    test = self._getRequest("02010005000D010000BC03");
                if (self.last_res.status == 200 ):
                    break
            return test

        #Pompa CWU
        def getPompaCWU(self):
                if (bool(self.s_statusdata)):
                        return self.s_statusdata[32] & (1 << 3) != 0;

        def setPompaCWU(self, state):
            test = False
            for x in range(self.ile_razy_testuj):
                if (state):
                    test = self._getRequest("02010005000E0100011103");
                else:
                    test = self._getRequest("02010005000E0100002003");
                    
                if (self.last_res.status == 200 ):
                    break
            return test

        #Pompa Obiegowa
        def getPompaMieszObieg(self):
                if (bool(self.s_statusdata)):
                        return self.s_statusdata[32] & (1 << 4) != 0;
        
        # Podajnik
        def getPodajnik(self):
                if (bool(self.s_statusdata)):
                        return self.s_statusdata[32] & (1 << 1) != 0;

        def getCzasPodajnika(self):
                if (bool(self.s_statusdata)):
                        return (self.s_statusdata[65] << 8 | self.s_statusdata[64]) / 60.0;

        def setPodajnik(self, state):
            test = False
            for x in range(self.ile_razy_testuj):
                if (state):
                    test = self._getRequest("02010005000C0100011603");
                else:
                    test = self._getRequest("02010005000C0100002703");
                if (self.last_res.status == 200 ):
                    break
            
            return test
                        
        def WlaczPodajnik_Async(self, sek):
                threading.Thread(target=self.WlaczPodajnikNaXSekThread, args=[sek]).start()
        
        def WlaczPodajnikNaXSekThread(self, sek):
                self.setPodajnik(True);
                time.sleep(sek);        
                self.setPodajnik(False);

        # Dmuchawa
        def getDmuchawa(self):
                if (bool(self.s_statusdata)):
                        return self.s_statusdata[32] & (1 << 0) != 0;
                        
        def setDmuchawa(self, state):
            test = False
            for x in range(self.ile_razy_testuj):
                if (state):
                        test = self._getRequest("02010005000B0100018403");
                else:
                        test = self._getRequest("02010005000B010000B503");
                if (self.last_res.status == 200 ):
                    break
            
            return test

        def getDmuchawaMoc(self):
                if (bool(self.s_statusdata)):
                        return self.s_statusdata[39];
                
        def setDmuchawaMoc(self, value):
                tab = [0x01, 0x00, 0x02, 0x00, 0x08, 0x02, 0x00, value & 0xff, 0x00];
                crc = self.crc(tab);
                tab.insert(0, 0x02);
                tab.append(crc);
                tab.append(0x03);
                cmd = ''.join('{:02x}'.format(x) for x in tab);
                test = False
                for x in range(self.ile_razy_testuj):
                  test = self._getRequest(cmd);
                  if (self.last_res.status == 200 ):
                      break
                    
                return test


        def getTypKotla(self):
            test = False
            for x in range(self.ile_razy_testuj):
                test = self._getRequest("02010001005000006C03");
                if (self.last_res.status == 200 ):
                    break

            if (self.last_res.status == 200 ):
                txt = str(self.last_content);
                txt = txt[txt.index('[') + 1:txt.index(']')]
                data = list(map(int, txt.split(',')));
               
                if   (data[8] == 0):
                  self.s_typ_kotla = "RETORTOWY-RECZNY"
                elif (data[8] == 1):
                  self.s_typ_kotla = "RETORTOWY-GRUPOWY"
                elif (data[8] == 2):
                  self.s_typ_kotla = "TLOKOWY-RECZNY"
                elif (data[8] == 3):
                  self.s_typ_kotla = "TLOKOWY-AUTO"
                elif (data[8] == 4):
                  self.s_typ_kotla = "ZASYPOWY"
                else:
                  self.s_typ_kotla = None

            return self.s_typ_kotla


        def crc(self, msg):
                runningCRC = 0
                for c in msg:
                        runningCRC = self.crcByte(runningCRC, c)
                return runningCRC
                
        def crcByte(self, oldCrc, byte):
                res = self.crcTable[oldCrc & 0xFF ^ byte & 0xFF];
                return res


                        

