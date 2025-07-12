#include <Keyboard.h>  // You can remove this if you don't use keyboard functions anymore

// === DEFINE YOUR RELAY OUTPUT PINS ===
// Arena 1 pin definitions
const int redLight1     = 2;
const int whiteLight1   = 3;
const int blower1       = 4;
const int extraRelay1   = 5; // Not Connected
const int roofLED1      = 6;
const int cameraPower1  = 7; // Not Connected

// Arena 2 pin definitions
const int redLight2     = 8;
const int whiteLight2   = 9;
const int blower2       = 10;
const int extraRelay2   = 11; // Not Connected
const int roofLED2      = 12;
const int cameraPower2  = 13; // Not Connected

// === BUTTON PINS ===
const int buttonPinA2 = A2;
const int buttonPinA3 = A3;
const int buttonPinA0 = A0;
const int buttonPinA1 = A1;

// Debounce timing
const unsigned long debounceDelay = 50; // milliseconds

// Variables to store previous button states and debounce info
bool prevStateA2 = HIGH;
bool prevStateA3 = HIGH;
bool prevStateA0 = HIGH;
bool prevStateA1 = HIGH;

bool lastButtonStateA2 = HIGH;
bool lastButtonStateA3 = HIGH;
bool lastButtonStateA0 = HIGH;
bool lastButtonStateA1 = HIGH;

unsigned long lastDebounceTimeA2 = 0;
unsigned long lastDebounceTimeA3 = 0;
unsigned long lastDebounceTimeA0 = 0;
unsigned long lastDebounceTimeA1 = 0;

void setup() {
  Serial.begin(9600);

  // Set relay pins as outputs
  pinMode(redLight1, OUTPUT);
  pinMode(redLight2, OUTPUT);
  pinMode(whiteLight1, OUTPUT);
  pinMode(whiteLight2, OUTPUT);
  pinMode(blower1, OUTPUT);
  pinMode(blower2, OUTPUT);
  pinMode(extraRelay1, OUTPUT);
  pinMode(extraRelay2, OUTPUT);
  pinMode(roofLED1, OUTPUT);
  pinMode(roofLED2, OUTPUT);
  pinMode(cameraPower1, OUTPUT);
  pinMode(cameraPower2, OUTPUT);

  // Set button pins as input with pull-up
  pinMode(buttonPinA2, INPUT_PULLUP);
  pinMode(buttonPinA3, INPUT_PULLUP);
  pinMode(buttonPinA0, INPUT_PULLUP);
  pinMode(buttonPinA1, INPUT_PULLUP);

  // If you still want Keyboard features remove this line or comment it out
  // Keyboard.begin();
}

void loop() {
  // === SERIAL COMMAND HANDLING ===
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.length() < 2) return;

    char arena = input.charAt(0);
    char cmd   = input.charAt(1);

    bool isArena1 = (arena == '1');
    bool isArena2 = (arena == '2');

    int pin = -1;

    switch (cmd) {
      case 'R': pin = isArena1 ? redLight1     : redLight2;     digitalWrite(pin, LOW); break;
      case 'r': pin = isArena1 ? redLight1     : redLight2;     digitalWrite(pin, HIGH); break;
      case 'W': pin = isArena1 ? whiteLight1   : whiteLight2;   digitalWrite(pin, LOW); break;
      case 'w': pin = isArena1 ? whiteLight1   : whiteLight2;   digitalWrite(pin, HIGH); break;
      case 'B': pin = isArena1 ? blower1       : blower2;       digitalWrite(pin, LOW); break;
      case 'b': pin = isArena1 ? blower1       : blower2;       digitalWrite(pin, HIGH); break;
      case 'E': pin = isArena1 ? extraRelay1   : extraRelay2;   digitalWrite(pin, LOW); break;
      case 'e': pin = isArena1 ? extraRelay1   : extraRelay2;   digitalWrite(pin, HIGH); break;
      case 'L': pin = isArena1 ? roofLED1      : roofLED2;      digitalWrite(pin, LOW); break;
      case 'l': pin = isArena1 ? roofLED1      : roofLED2;      digitalWrite(pin, HIGH); break;
      case 'C': pin = isArena1 ? cameraPower1  : cameraPower2;  digitalWrite(pin, LOW); break;
      case 'c': pin = isArena1 ? cameraPower1  : cameraPower2;  digitalWrite(pin, HIGH); break;
    }

    Serial.print("command successful: ");
    Serial.println(input);
  }

  // === BUTTON CHECKING with debounce ===
  checkButtonDebounced(buttonPinA2, prevStateA2, lastDebounceTimeA2, lastButtonStateA2, "ButtonA2");
  checkButtonDebounced(buttonPinA3, prevStateA3, lastDebounceTimeA3, lastButtonStateA3, "ButtonA3");
  checkButtonDebounced(buttonPinA0, prevStateA0, lastDebounceTimeA0, lastButtonStateA0, "ButtonA0");
  checkButtonDebounced(buttonPinA1, prevStateA1, lastDebounceTimeA1, lastButtonStateA1, "ButtonA1");
}

void checkButtonDebounced(int pin, bool &prevState, unsigned long &lastDebounceTime, bool &lastButtonState, const char* name) {
  bool reading = digitalRead(pin);

  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading != prevState) {
      prevState = reading;

      if (reading == LOW) {
        Serial.print(name);
        Serial.println(" pressed");
      } else {
        Serial.print(name);
        Serial.println(" released");
      }
    }
  }

  lastButtonState = reading;
}
