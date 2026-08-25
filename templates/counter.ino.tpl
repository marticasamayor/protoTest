// Auto-generat per protoTest -- test Counter
int comptador = 0;

void setup() {
  Serial.begin(__BAUD_RATE__);
  Serial.println("[counter] test iniciat");
}

void loop() {
  Serial.println("[counter] " + String(comptador++));
  delay(500);
}
