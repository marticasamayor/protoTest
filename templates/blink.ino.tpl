// Auto-generat per protoTest -- test Blink
const int LED_PIN = __LED_PIN__;

void setup() {
  Serial.begin(__BAUD_RATE__);
  pinMode(LED_PIN, OUTPUT);
  Serial.println("[blink] test iniciat, LED_PIN=" + String(LED_PIN));
}

void loop() {
  digitalWrite(LED_PIN, HIGH);
  Serial.println("[blink] LED = HIGH");
  delay(1000);
  digitalWrite(LED_PIN, LOW);
  Serial.println("[blink] LED = LOW");
  delay(1000);
}
