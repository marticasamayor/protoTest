// Auto-generat per protoTest -- test WiFi Scan
#include "WiFi.h"

void setup() {
  Serial.begin(__BAUD_RATE__);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  Serial.println("[wifi_scan] test iniciat");
}

void loop() {
  Serial.println("[wifi_scan] escanejant...");
  int n = WiFi.scanNetworks();

  if (n == 0) {
    Serial.println("[wifi_scan] cap xarxa trobada");
  } else {
    Serial.println("[wifi_scan] " + String(n) + " xarxa/es trobada/es");
    for (int i = 0; i < n; ++i) {
      String seguretat = (WiFi.encryptionType(i) == WIFI_AUTH_OPEN) ? "oberta" : "xifrada";
      Serial.println("[wifi_scan] " + String(i + 1) + ": " + WiFi.SSID(i) +
                      " (" + String(WiFi.RSSI(i)) + " dBm, " + seguretat + ")");
      delay(10);
    }
  }

  delay(5000);
}
