Akwizycja danych z Lucjana w bazie Domoticz, how-to: 

1. Instalujemy na Raspberry Domoticz

      sudo curl -L install.domoticz.com | sudo bash
        
      (dokładny opis - tutaj https://www.domoticz.com/wiki/Installing_and_running_Domoticz_on_a_Raspberry_PI)
        
2. kopiujemy pliki domoticz.py do malinki 

      mkdir ~/lucjan && cd ~/lucjan
      
      wget -O skrypt.py https://raw.githubusercontent.com/uzi18/sterownik/master/arduino/Domoticz/test.py
      
      wget https://raw.githubusercontent.com/uzi18/sterownik/master/arduino/Domoticz/konfiguracja.py
        
3. ustawiamy skrypt jako uruchamiany z systemem:  

      sudo echo "sudo -u pi python /home/pi/lucjan/skrypt.py" >> /etc/rc.local
        
      w pliku lucjan/konfiguracja.py wpisać IP Lucjana, port na którym pracuje domoticz, jeśli inny niż domyślny. 
        
4. Wejść do panela Domoticz (domyślnie http://IP_Malinki:8080) i w Konfiguracja -> Sprzęt dodajemy nowe urządzenie, nazywamy je dowolnie, np. Piec, wybieramy 
typ "Dummy (Does nothing, use for virtual switches only)"

5. Do utworzonego urządzenia dodajemy nowe wirtualne czujniki, tak, by ich numery IDX były w kolejności takiej, jak mapowane czujniki, tj:  
TPIEC,TPOWROT,TPODAJNIK,TZEW,TWEW,TCWU,TPODLOGA,TSPALINY,T1,T2,T3,T4,T5,T6,T7,T8. Nazywamy je dowolnie. 

6. Jeśli pierwszy czujnik TPIEC  ma numer IDX inny niż 1, to wpisujemy to w pliku konfiguracja.py 

7. Robimy restart malinki i sprawdzamy na stronie IP_Malinki:8080 czy wszystko działa jak trzeba. 

