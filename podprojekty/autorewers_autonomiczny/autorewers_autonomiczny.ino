/*
 * Autorewers 2.0 program v0.65 autor Stanislaw Gromowski
 * Program jest wsadem do urządzenia autorewers służącego do nadzorowania pracy podajnika
 * w piecach węglowych z podajnikiem ślimakowym.
 * Kalibracja, nacisnąć przycisk wówczas autorewer uruchomi podajnik na kilka sekund
 * i podczas jego pracy zmierzy płynący prąd przez silnik, zmierzoną wartość zapisze w pamięci eeprom.
 * Program po kalibracji prądem nominalnym podczas pracy podajnika wykrywa przeciążenie
 * silnika podajnika i uruchamia bieg wsteczny na ok 15 sekund,po czym wykonuje ruch testowy do przodu
 * jeśli zakleszczenie ustąpiło przechodzi do nadzoru, jeżeli nie,  uruchamia ponownie bieg wsteczny.
 * Cykl ten zostanie  wykonany trzykrotnie.
 * Jeśli trzy razy z rzędu nie uda mu się wejść do normalnej pracy zatrzymuje się i zgłasza alarm.
 * Wyjście z alarmu polega na odłączeniu zasilania od sterownika i ponownym podłączeniu,
 * skasowane zostaną wszystkie alarmy i autorewers wejdzie ponownie w tryb nadzoru.
 */
#include <Bounce2.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h> 
#include "EmonLib.h"                   // Include Emon Library
EnergyMonitor emon1;                   // Create an instance
#include <EEPROM.h>
LiquidCrystal_I2C lcd(0x27,2,1,0,4,5,6,7);

int I_nominalny;
int licznik_rewers;
int licznik1=0;
int k=0;
int I_nom;
int czas_cofania=15000;

float korekta_Ik=1.3;
float Irms;
float Ik;
float I_n;
float I_por;

#define BACKLIGHT_PIN 3
#define przek_podajnik 6
#define przek_rewers_t 4
#define przek_rewers_p 7
#define przek_alarm 5

int addr_I_nominalny = 0;
int addr_licznik_rewers = 1;
int wej_podajnik = 2; //konfiguracja pinow dla Bounce
int wej_kalibracja = 3; //konfiguracja pinow dla Bounce

Bounce podajnik = Bounce(wej_podajnik, 50);
Bounce kalibracja = Bounce(wej_kalibracja, 50);
//=================================================================================
void setup()
{  
  digitalWrite(6, HIGH);//wylaczenie podajnika(przekaznik stanu niskiego)
  digitalWrite(4, HIGH);//wylaczenie biegu do tylu(przekaznik stanu niskiego)
  digitalWrite(7, LOW);//wlaczenie biegu do przodu(przekaznik stanu niskiego)
  digitalWrite(5, HIGH);//wylaczenie alarmu(przekaznik stanu niskiego)
  
  pinMode(przek_rewers_t, OUTPUT);//przekaznik SSR obrotow do tylu
  pinMode(przek_rewers_p, OUTPUT);//przekaznik SSR obrotow do przodu
  pinMode(przek_podajnik, OUTPUT);//przekaznik SSR praca podajnika
  pinMode(przek_alarm, OUTPUT);//przekaznik alarmu zewnentrznego
  pinMode(wej_podajnik, INPUT);
  pinMode(wej_kalibracja, INPUT);
  
  Serial.begin(9600);
  
  lcd.begin (16,2);
  lcd.setBacklightPin(BACKLIGHT_PIN, POSITIVE);
  lcd.setBacklight(HIGH);
  
  emon1.current(1,5); // Current:pin wejsciowy, wspolczynnik kalibracji dla CTS.
 
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("autorewers v0.65");
  lcd.setCursor(0,1);
  lcd.print("     czekaj     ");
  delay(3000);  
}
//==================================================================================
void loop()         //petla glowna programu
{
podajnik.update(); //aktualizacja stanu wejscia podajnika
int value_podajnik = podajnik.read(); //pobranie stanu wejścia podajnika
if (value_podajnik == HIGH)
{
  pod_stop();
  lcd_stop();
}

if (value_podajnik == LOW)
{
  praca();
}

kalibracja.update();  //aktualizacja stanu wejscia kalibracji
int value_kalibracja = kalibracja.read(); //pobranie stanu wejscia kalibracji
if (value_kalibracja == LOW)
{
    kalibrowanie();
}
//kasowanie_eeprom();
}

//==================================================================================
void praca()          //wykrycie przeciazenia i reakcja
{
  I_n = EEPROM.read(addr_I_nominalny);
  Ik = I_n / 100;
  I_por = Ik * korekta_Ik; //powiekszony prad nominalny
  lcd_praca();  
  pod_start();
  delay(500); //pominiecie pradu rozruchu
  Irms = emon1.calcIrms(740);  // Wyliczenie Irms ; 740:probek
  delay(50);
  if (Irms > I_por && licznik1 <4)
  {
    rewers();
  }

  if (Irms < I_por)
  {
    licznik1=0;
  }
}
//==================================================================================
void kalibrowanie()     //ustalenie pradu pracy podajnika
{
  pod_start();
  lcd.setCursor(0,0);
  lcd.print("KALIBRUJE czekaj");
  lcd.setCursor(0,1);
  lcd.print("                ");
  delay(500);
  I_nom = 0;
  for(int i=0;i<10;i++)
  {
   Irms = emon1.calcIrms(1480)* 100;
   I_nom = I_nom + Irms;
  }
  I_nominalny = (I_nom / 10);
  I_n = I_nominalny;
  Ik = I_n / 100;
  lcd.setCursor(0,1);
  lcd.print("Ik:");
  lcd.setCursor(3,1);
  lcd.print(Ik, 2);
  EEPROM.write(addr_I_nominalny,I_nominalny);
  delay(3000);  
  pod_stop(); 
}
//==================================================================================
void pod_start()    //start podajnika
{
 digitalWrite(przek_podajnik, LOW); 

}
//==================================================================================
void pod_stop()     //zatrzymanie podajnika
{
 digitalWrite(przek_podajnik, HIGH);

}
//==================================================================================
void obr_p()        //podajnik obroty przod
{
 pod_stop();
 delay(50);
 digitalWrite(przek_rewers_t, HIGH);
 delay(50); 
 digitalWrite(przek_rewers_p, HIGH);
 delay(50); 
 digitalWrite(przek_rewers_p, LOW); 
}
//==================================================================================
void obr_t()        //podajnik obroty tyl
{
 pod_stop(); 
 delay(50); 
 digitalWrite(przek_rewers_p, HIGH);
 delay(50);
 digitalWrite(przek_rewers_t, HIGH);
 delay(50);
 digitalWrite(przek_rewers_t, LOW);
}
//==================================================================================
void alarm()
{
  while (licznik1 >= 3)
  {
    pod_stop();
    digitalWrite(przek_alarm, LOW);
    lcd.setCursor(0,0);
    lcd.print(" ALARM- 3x rew. ");
    lcd.setCursor(0,1);
    lcd.print("odlacz zasilanie");
    delay(1);
  }
}
//==================================================================================
void rewers()
{
  pod_stop();
  lcd.setCursor(0,0);
  lcd.print(" UWAGA! - cofam ");
  lcd.setCursor(0,1);
  lcd.print("    czekaj      ");
  delay(1000);
  obr_t();
  delay(1000);
  pod_start();
  delay(czas_cofania);
  pod_stop();
  delay(1000);
  obr_p();
  licznik1++;
  licznik_rewers = EEPROM.read(addr_licznik_rewers)+1;
  EEPROM.write(addr_licznik_rewers,licznik_rewers);
  if (licznik1 > 3)
  {
    alarm();
  }
  else
  {
  ruch_testowy();
  }  
}
//==================================================================================
void ruch_testowy()
{
  obr_p();
  delay(1000);  
  pod_start();
  for(int b=0;b<50;b++)
  {
  delay(300); //pominiecie pradu rozruchu
  I_n = EEPROM.read(addr_I_nominalny);
  Ik = I_n / 100;
  float I_por = Ik * korekta_Ik; //powiekszony prad nominalny
  Irms = emon1.calcIrms(370);  // Wyliczenie Irms ; 740:probek
  if (Irms > I_por)
  {
    rewers();
  }
  lcd_ruch_testowy();
  }
}
//==================================================================================
void kasowanie_eeprom()
{
  while (k < 2)
  {
    EEPROM.write(addr_I_nominalny,0);
    EEPROM.write(1,0);
    k++;
    lcd.setCursor(0,0);
    lcd.print("KASOWANIE EEPROM");
    lcd.setCursor(0,1);
    lcd.print("   WYKONANO!    ");
    delay(3000);
  }

}
//==================================================================================
void lcd_praca()
{
 //I_n = EEPROM.read(addr_I_nominalny);
 //Ik = (I_n / 100)*korekta_Ik;
 lcd.setCursor(0,0);
 lcd.print("  PRACA -czekaj ");
 lcd.setCursor(0,1);
 lcd.print("Ip:");
 lcd.print(Irms, 2);
 lcd.setCursor(7,1);
 lcd.print(" Iz:");
 lcd.print(I_por, 1);  
}
//=================================================================================
void lcd_ruch_testowy()
{
 I_n = EEPROM.read(addr_I_nominalny);
 Ik = (I_n / 100)*korekta_Ik;
 lcd.setCursor(0,0);
 lcd.print("TEST odbl-czekaj");
 lcd.setCursor(0,1);
 lcd.print("Ip:");
 lcd.print(Irms, 2);
 lcd.setCursor(7,1);
 lcd.print(" Iz:");
 lcd.print(Ik, 1);  
}
//=================================================================================
void lcd_stop()
{
 I_n = EEPROM.read(addr_I_nominalny);
 Ik = I_n / 100;
 lcd.setCursor(0,0);
 lcd.print("    OCZEKUJE    ");
 lcd.setCursor(0,1);
 lcd.print("Ik:");
 lcd.print( Ik, 2);  
 lcd.setCursor(7,1);
 lcd.print("  rew:");
 lcd.print(EEPROM.read(addr_licznik_rewers));
}
