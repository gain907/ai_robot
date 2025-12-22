// Step 1: Arduino connections to servo motors

//emma code
#include <cvzone.h>
#include <Servo.h>

// Declaration of servo objects
Servo LServo;  // Left arm servo
Servo RServo;  // Right arm servo
Servo HServo;  // Head servo

// Define the servo control pins
const int LS_pin = 8;   // Left servo pin
const int RS_pin = 9;  // Right servo pin
const int HS_pin = 10;  // Head servo pin

// Initialize serial data to receive 3 values, each up to 3 digits
SerialData serialData(3, 3); //python code sends angles
int valsRec[3];  // Array to store the received values for each servo {0,0,180}

void setup() {
  //Serial.begin(9600);  // Start serial communication at 9600 baud rate
  serialData.begin();  // Initialize the serial data communication

  // Attach servos to their respective pins
  LServo.attach(LS_pin);
  RServo.attach(RS_pin);
  HServo.attach(HS_pin);
}

void loop() {
    // Python sends in list of angles: {Lservo, RServo , HServo}
    serialData.Get(valsRec);   // Angles revceived from arduino
    LServo.write(valsRec[0]);  // Set the left servo to the received position
    RServo.write(valsRec[1]);  // Set the right servo to the received position
    HServo.write(valsRec[2]);  // Set the head servo to the received position
  
}
