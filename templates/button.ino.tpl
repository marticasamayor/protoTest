// Auto-generat per protoTest -- test Button
const int BUTTON_PIN = __BUTTON_PIN__;

int lastState = -1;

void setup() {
  Serial.begin(__BAUD_RATE__);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  Serial.println("[button] test iniciat, BUTTON_PIN=" + String(BUTTON_PIN));
}

void loop() {
  int state = digitalRead(BUTTON_PIN);
  if (state != lastState) {
    bool pressed = (state == LOW);  // INPUT_PULLUP: LOW = premut
    Serial.println(pressed ? "[button] PREMUT" : "[button] SOLTAT");
    lastState = state;
  }
  delay(20);
}
