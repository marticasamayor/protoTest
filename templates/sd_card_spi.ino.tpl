// Auto-generat per protoTest -- test SD Card (SPI)
#include <SPI.h>
#include <SD.h>

const int PIN_MISO = __MISO_PIN__;
const int PIN_MOSI = __MOSI_PIN__;
const int PIN_SCK = __SCK_PIN__;
const int PIN_CS = __CS_PIN__;

void listDir(fs::FS &fs, const char *dirname, uint8_t levels) {
  File root = fs.open(dirname);
  if (!root || !root.isDirectory()) {
    Serial.printf("[sd_card] no es un directori: %s\n", dirname);
    return;
  }
  File file = root.openNextFile();
  while (file) {
    if (file.isDirectory()) {
      Serial.printf("[sd_card]   [DIR]  %s\n", file.path());
      if (levels) listDir(fs, file.path(), levels - 1);
    } else {
      Serial.printf("[sd_card]   %-30s %8u B\n", file.path(), (unsigned)file.size());
    }
    file = root.openNextFile();
  }
}

void setup() {
  Serial.begin(__BAUD_RATE__);
  delay(500);
  Serial.println("[sd_card] test iniciat, inicialitzant...");

  SPI.begin(PIN_SCK, PIN_MISO, PIN_MOSI, PIN_CS);

  if (!SD.begin(PIN_CS, SPI, 4000000)) {
    Serial.println("[sd_card] ERROR: muntatge fallit. Revisa cablejat / format (FAT32) / pull-up a CS.");
    return;
  }

  uint8_t type = SD.cardType();
  if (type == CARD_NONE) {
    Serial.println("[sd_card] ERROR: no hi ha targeta SD connectada.");
    return;
  }

  const char *tipus = (type == CARD_MMC) ? "MMC" :
                       (type == CARD_SD) ? "SDSC" :
                       (type == CARD_SDHC) ? "SDHC" : "DESCONEGUT";
  Serial.printf("[sd_card] Tipus: %s\n", tipus);
  Serial.printf("[sd_card] Mida: %llu MB\n", SD.cardSize() / (1024ULL * 1024ULL));
  Serial.println("[sd_card] Fitxers arrel:");
  listDir(SD, "/", 2);
}

void loop() {
}
