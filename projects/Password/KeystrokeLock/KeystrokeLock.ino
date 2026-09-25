#include "model.h"

KeystrokeBaseline clf;

const int FEATURES_COUNT = 15;
float input_features[FEATURES_COUNT];

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    for (int i = 0; i < FEATURES_COUNT; i++) {
      input_features[i] = Serial.parseFloat();
    }

    while (Serial.available() > 0) {
      Serial.read();
    }

    int result = clf.predict(input_features);

    if (result == 0) {
      Serial.println("[WARNING] Intruder rhythm detected! Out of bounds timing.");
      for (int i = 0; i < 5; i++) {
        digitalWrite(LED_BUILTIN, HIGH);
        delay(80);
        digitalWrite(LED_BUILTIN, LOW);
        delay(80);
      }
    } else {
      Serial.println("[OK] Genuine rhythm verified. Access granted.");
      digitalWrite(LED_BUILTIN, HIGH);
      delay(400);
      digitalWrite(LED_BUILTIN, LOW);
    }
  }
}