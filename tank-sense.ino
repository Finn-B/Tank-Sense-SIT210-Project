// This #include statement was automatically added by the Particle IDE.
#include "HC_SR04.h"
/*
Connect an HC-SR04 Range finder as follows:
Argon   HC-SR04
GND     GND
5V VUSB VCC
D4      Trig
D5      Voltage divider output - see below

Echo --|
       >
       < 1k ohm resistor
       >
       ------ D5 on Argon
       >
       < 2.2k ohm resistor
       >
GND ---|

The HC-SR04 has 2cm (min) to 500cm (max) range. Under minCM -1 is returned as the distance. Over maxCM -2 is returned as the distance.

You can change this range with minCM and maxCM variables below.
*/

/*
---------------------------------
// Variables
---------------------------------
*/

double cm = 0.0;  // stores distance as cm
double inches = 0.0; // stares distance as inches
int perc = 0;  // percent value
double maxcm = 350;  // set max cm distance for hc-sr04
double mincm = 20;  // set min cm distance for hc-sr04
int control = 120;  // set initial control code to 120 to ensure water valve is in manual off
double cap = maxcm - mincm;  // water tank distance / range from being full to empty
int trigPin = D4;  // D4 pin is the tigger pin
int echoPin = D5;  // D5 pin is the echo pin
int valvePin = D7;  // D7 pin is the LED indicator for if the water valve is on / off
int valve_status = 10;  // Set the valve_status to manual off


/*
---------------------------------
// Functions
---------------------------------
*/

// Declare rangefinder function
HC_SR04 rangefinder = HC_SR04(trigPin, echoPin, mincm, maxcm );


// Declare control_valve function
int control_valve(String water_val);


// Declare check_comand function
int check_command(int control);


// Define control_valve function
int control_valve(String water_val)   // Remote unit calls cloud function control_word and passes string code for off (120) / on (110) / auto (0 - 100 percent).
{
   control = water_val.toInt();  // turns into integer
   valve_status = check_command(control);  // uses control code to turn water valve off / on or auto mode
   return valve_status;  // returns the status of the water valve. 1 = auto on, 0 = auto off, manual on = 11, manual off = 10
}
   
   
// Define check_command function   
int check_command(int control)  // commands water valve to be in auto, on or off depending on the control code passed in.
{
  if (control >= 0 && control <= 100){
       if (control <= 30){
           digitalWrite(valvePin, HIGH);
           return 1;
           }
        else{
            digitalWrite(valvePin, LOW);
            return 0;
        }
   } 
   
   if (control == 110){
       digitalWrite(valvePin, HIGH);
       return 11;
   }
   
   if (control == 120){
       digitalWrite(valvePin, LOW);
       return 10;
   }
}


/*
---------------------------------
// Setup
---------------------------------
*/
void setup() 
{
    Particle.function("control_word", control_valve);  // cloud function to control water valve mode
    Particle.variable("cm", &cm, DOUBLE);  // cloud variable distance in cm
    Particle.variable("inches", &inches, DOUBLE);  // cloud variable for distance in inches
    Particle.variable("valve_status", valve_status);  // cloud variable for water valve status
    pinMode(valvePin, OUTPUT);  // declare water valve pin an output pin
    digitalWrite(valvePin, LOW);  // initialise water valve pin as off
}


/*
---------------------------------
// Main Loop
---------------------------------
*/
void loop() 
{
    cm = rangefinder.getDistanceCM();  // get distance in cm
    inches = rangefinder.getDistanceInch();  // get distance in inches
    valve_status = check_command(control);  // control water valve and store the status the water valve is in
}




