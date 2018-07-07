/*
  This command parses receives commands via UART, parses it and passes parameters. Then it responds with data.
*/

#include "DHT.h"
#include <Servo.h>
#include <Wire.h>
#include "MutichannelGasSensor.h"

DHT dht_in(A0, DHT22);
DHT dht_out(A1, DHT22);

Servo myservo;
// gas MutichannelGasSensor;

int cmd[5];
float h, t, c;
int pos = 0;
int button_state = 0;
int prev_button_state = 0;

const int buttonPin = 6;
const int FanPin = 4;

void setup()
{
  pinMode(buttonPin, INPUT);
  pinMode(FanPin, OUTPUT);
  Serial.begin(115200);
  dht_in.begin();
  dht_out.begin();
  gas.begin(0x04);
  
  //Serial.print("Hello world\n");
}

void loop()
{
  while(Serial.available() > 0)
  {
    //Serial.print("Got something\n");    
    cmd[0] = Serial.read();
    cmd[1] = Serial.read();
    cmd[2] = Serial.read();
    switch (cmd[0])
    {
      case 'a':
        h = dht_in.readHumidity();
        t = dht_in.readTemperature();
        
        if (isnan(t) || isnan(h))
        {
          Serial.println("Failed to read from dht_in");
        }
        else
        {
          //Serial.print("Inside Humidity: "); 
          Serial.print(h);
          Serial.print(" ");
          //Serial.print("Temperature: "); 
          Serial.println(t);
          //Serial.println(" *C");
        }          
        break;
      
      case 'b':
        h = dht_out.readHumidity();
        t = dht_out.readTemperature();
        
        if (isnan(t) || isnan(h))
        {
          Serial.println("Failed to read from dht_out");
        }
        else
        {
          //Serial.print("Outside Humidity: "); 
          Serial.print(h);
          Serial.print(" ");
          //Serial.print("Temperature: "); 
          Serial.println(t);
        }          
        break;

      case 'c':
        // We basically slam the door shot.
        myservo.attach(7);
        myservo.write(180);
        delay(2500);
        pos = myservo.read();        
        myservo.detach();        
        Serial.println(pos);
        break;

      case 'o':
        // We open the door as fast as possible.
        myservo.attach(7);
        myservo.write(0);
        delay(2500);
        pos = myservo.read();
        myservo.detach();        
        Serial.println(pos);
        break;
        
      case 'd':
        myservo.attach(7);
        pos = myservo.read();
        //Serial.print("Servo position = ");
        myservo.detach();
        Serial.println(pos);
        break;

      case 'e':
        gas.powerOn();
        Serial.println('e');
        break;

      case 'f':
        gas.powerOff();
        Serial.println('f');
        break;

      case 'g':
        c = gas.measure_NH3();
        if (c >= 0) Serial.println(c);
        else Serial.println('e');
        break;

      case 'h':
        c = gas.measure_CO();
        if (c >= 0) Serial.println(c);
        else Serial.println('e');
        break;

      case 'i':
        c = gas.measure_NO2();
        if (c >= 0) Serial.println(c);
        else Serial.println('e');
        break;

      case 'j':
        c = gas.measure_C3H8();
        if (c >= 0) Serial.println(c);
        else Serial.println('e');
        break;

      case 'k':
        c = gas.measure_C4H10();
        if (c >= 0) Serial.println(c);
        else Serial.println('e');
        break;

      case 'l':
        c = gas.measure_CH4();        
        if (c >= 0) Serial.println(c);
        else Serial.println('e');
        break;

      case 'm':
        c = gas.measure_H2();
        if (c >= 0) Serial.println(c);
        else Serial.println('e');
        break;

      case 'n':
        c = gas.measure_C2H5OH();
        if (c >= 0) Serial.println(c);
        else Serial.println('e');
        break;

      case 'p':
        c = gas.getR0(0);
        if (c >= 0) Serial.println(c);
        else Serial.println('e');
        break;

      case 'q':
        c = gas.getR0(1);
        if (c >= 0) Serial.println(c);
        else Serial.println('e');
        break;

      case 'r':
        c = gas.getR0(2);
        if (c >= 0) Serial.println(c);
        else Serial.println('e');
        break;

      case 's':
        c = gas.getRs(0);
        if (c >= 0) Serial.println(c);
        else Serial.println('e');
        break;

      case 't':
        c = gas.getRs(1);
        if (c >= 0) Serial.println(c);
        else Serial.println('e');
        break;

      case 'u':
        c = gas.getRs(2);
        if (c >= 0) Serial.println(c);
        else Serial.println('e');
        break;

      case 'v':
        digitalWrite(FanPin, HIGH);
        Serial.println('1');
        break;

      case 'w':
        digitalWrite(FanPin, LOW);
        Serial.println('0');
        break;

      default:
        Serial.println("default");
        break;
    } //switch   
  } //while
  
  button_state = digitalRead(buttonPin);
  
  // Upon a button press we open or close the door. First we attach to the
  // servo and at the end detach.
  if (button_state == HIGH)
  {
    myservo.attach(7);
    pos = myservo.read();        
    if (pos < 90)
    {
      // The door is close and now we open it.
      myservo.write(180);
      delay(2500);
    }
    else
    {
      // The door is open and now we close it.
      myservo.write(0);
      delay(2500);
    }
    myservo.detach();
    //Serial.println("Button state change");    
  }
}
