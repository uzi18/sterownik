/*
 * Autorewers v2.0 program v0.51 autor Stanislaw Gromowski
 * Program jest wsadem do urządzenia autorewers służącego do nadzorowania pracy podajnika
 * w piecach węglowych z podajnikiem ślimakowym.
 * Kalibracja, nacisnąć przycisk wówczas autorewer uruchomi podajnik na kilka sekund
 * i podczas jego pracy zmierzy płynący prąd przez silnik, zmierzoną wartość zapisze w pamięci eeprom.
 * Program po kalibracji prądem nominalnym podczas pracy podajnika wykrywa przeciążenie
 * silnika podajnika i uruchamia bieg wsteczny na ok 15 sekund, cykl ten wykonuje trzykrotnie
 * i jeśli trzy razy z rzędu nie uda mu się wejść do normalnej pracy zatrzymuje się i zgłasza alarm.
 * Wyjście z alarmu polega na odłączeniu zasilania od sterownika i ponownym podłączeniu,
 * skasowane zostaną wszystkie alarmy i autorewers wejdzie ponownie w tryb nadzoru.
 */
#include "EmonLib.h"                   // Include Emon Library
EnergyMonitor emon1;                   // Create an instance
#include <EEPROM.h>
int I_nominalny;
int licznik_rewers;
int licznik1=0;
//int k=0;      //tylko do zerowania eeprom
#define led_praca 8
#define led_kalibracja 7
#define przek_praca 5
#define przek_rewers 4
//=================================================================================
void setup()
{  
  pinMode(przek_rewers, OUTPUT);//przekaznik rewers obrotow
  pinMode(przek_praca, OUTPUT);//przekaznik praca podajnika
  pinMode(led_kalibracja, OUTPUT);//LED czerwona
  pinMode(led_praca, OUTPUT);//LED zielona
  pinMode(2, INPUT_PULLUP);
  pinMode(3, INPUT_PULLUP);
  Serial.begin(9600);
  emon1.current(1,5);             // Current:pin wejsciowy, wspolczynnik kalibracji dla CTS.
  attachInterrupt(digitalPinToInterrupt(2), praca, LOW);
  attachInterrupt(digitalPinToInterrupt(3), kalibracja, LOW);
  digitalWrite(5, LOW);


}
//==================================================================================
void loop()         //petla glowna programu
{
  pod_stop();
  obr_p();
  Serial.println("przerwa");
  Serial.println(EEPROM.read(0));
  Serial.println(EEPROM.read(1));
/* 
  while (k < 2)
  {
    EEPROM.write(0,0);
    EEPROM.write(1,0);
    k++;
    Serial.println("zerowanie licznikow wykonane");
  }
*/
  pod_stop();
}

//==================================================================================
void praca()          //wykrycie przeciazenia i reakcja
{
  pod_start();
 // Serial.println("praca");
  delaj(1); //pominiecie pradu rozruchu
  I_nominalny = EEPROM.read(0) *1.5; //powiekszony prad nominalny
  double Irms = emon1.calcIrms(1480) * 100;  // Wyliczenie Irms ; 1480:probek
  int I_nom = Irms;
  if (I_nom > I_nominalny && licznik1 <4)
  {
    rewers();
  }
  else
  {
   alarm();
  }
  licznik1=0;
}
//==================================================================================
void kalibracja()     //ustalenie pradu pracy podajnika
{
  pod_start();
  delaj(3);
  digitalWrite(led_kalibracja, LOW); 
  digitalWrite(led_praca, LOW); 
  digitalWrite(led_kalibracja, HIGH); 
  int I_nom = 0;
  for(int i=0;i<10;i++)
  {
   double Irms = emon1.calcIrms(1480)* 100;
   I_nom = I_nom + Irms;
  }
  int I_nominalny = (I_nom / 10);
  EEPROM.write(0,I_nominalny);
  digitalWrite(led_kalibracja, LOW); 
  delaj(2);
  digitalWrite(led_kalibracja, HIGH); 
  delaj(2);
  digitalWrite(led_kalibracja, LOW); 
  delaj(2);
  digitalWrite(led_kalibracja, HIGH);
  delaj(2);
  digitalWrite(led_kalibracja, LOW); 
  delaj(2);
  digitalWrite(led_kalibracja, HIGH);
  delaj(2);
  digitalWrite(led_kalibracja, LOW);  
  pod_stop();  
}
//==================================================================================
void pod_start()    //start podajnika
{
 digitalWrite(przek_praca, HIGH); 
 digitalWrite(led_praca, HIGH);
}
//==================================================================================
void pod_stop()     //zatrzymanie podajnika
{
 digitalWrite(przek_praca, LOW);
 digitalWrite(led_praca, LOW); 
}
//==================================================================================
void obr_p()        //podajnik obroty przod
{
 digitalWrite(przek_rewers, LOW); 
}
//==================================================================================
void obr_t()        //podajnik obroty tyl
{
 digitalWrite(przek_rewers, HIGH);
 digitalWrite(led_kalibracja, HIGH);
 digitalWrite(led_praca, HIGH);
}
//==================================================================================
void alarm()
{
  noInterrupts();
  while (licznik1 >= 3)
  {
    pod_stop();
    digitalWrite(led_kalibracja, HIGH);
    delaj(1);
    digitalWrite(led_kalibracja, LOW);
    delaj(1);
  }
  interrupts();
}
//==================================================================================
void rewers()
{
  noInterrupts();
  pod_stop();
  delaj(2);
  obr_t();
  delaj(2);
  pod_start();
  //Serial.println("obroty tyl");
  delaj(50);
  pod_stop();
  delaj(2);
  obr_p();
  licznik1++;
  licznik_rewers = EEPROM.read(1)+1;
  EEPROM.write(1,licznik_rewers);
  digitalWrite(led_kalibracja, LOW);
  digitalWrite(led_praca, LOW);
  delaj(2);
  digitalWrite(led_kalibracja, HIGH);
  digitalWrite(led_praca, HIGH); 
  delaj(2);
  digitalWrite(led_kalibracja, LOW);
  digitalWrite(led_praca, LOW);   
  //Serial.println("koniec");
  interrupts();
}
//==================================================================================
int delaj(int sek)  //funkcja opozniajaca - 1 sek = 0,25 sekundy (okolo)
{
 int i=0;
 while (i < sek)
 {
  double Irms = emon1.calcIrms(2000);
  i++;
 }
 return(0);
}
//==================================================================================

