// Auto-generat per protoTest -- test I2C Scanner
#include <Wire.h>

const int SDA_PIN = __SDA_PIN__;
const int SCL_PIN = __SCL_PIN__;

void setup() {
  Serial.begin(__BAUD_RATE__);
  Wire.begin(SDA_PIN, SCL_PIN);
  Serial.println("[i2c_scanner] test iniciat, SDA=" + String(SDA_PIN) + " SCL=" + String(SCL_PIN));
}

void loop() {
  Serial.println("[i2c_scanner] escanejant...");
  int trobats = 0;

  for (byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    byte error = Wire.endTransmission();

    if (error == 0) {
      Serial.print("[i2c_scanner] dispositiu trobat a 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
      trobats++;
    }
  }

  if (trobats == 0) {
    Serial.println("[i2c_scanner] cap dispositiu trobat");
  } else {
    Serial.println("[i2c_scanner] " + String(trobats) + " dispositiu(s) trobat(s)");
  }

  delay(5000);
}
