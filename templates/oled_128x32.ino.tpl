// Auto-generat per protoTest -- test OLED 128x32 (I2C, SSD1306)
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C

const int SDA_PIN = __SDA_PIN__;
const int SCL_PIN = __SCL_PIN__;

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void setup() {
  Serial.begin(__BAUD_RATE__);
  Wire.begin(SDA_PIN, SCL_PIN);

  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println("[oled] ERROR: pantalla no trobada (SSD1306 allocation failed)");
    while (true) delay(1000);
  }
  Serial.println("[oled] pantalla inicialitzada correctament");

  display.clearDisplay();
  display.drawRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, SSD1306_WHITE);
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(4, 4);
  display.println("protoTest OK");
  display.display();
}

void loop() {
  static bool inverted = true;
  display.invertDisplay(inverted);
  Serial.println(inverted ? "[oled] invertit ON" : "[oled] invertit OFF");
  inverted = !inverted;
  delay(1000);
}
