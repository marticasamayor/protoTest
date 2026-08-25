// Auto-generat per protoTest -- test Blink Digital (WS2812/NeoPixel)
#include <Adafruit_NeoPixel.h>

#define DATA_PIN __DATA_PIN__
#define NUM_PIXELS __NUM_PIXELS__

Adafruit_NeoPixel strip(NUM_PIXELS, DATA_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(__BAUD_RATE__);
  strip.begin();
  strip.show();
  Serial.println("[blink_digital] test iniciat, DATA_PIN=" + String(DATA_PIN));
}

void loop() {
  strip.fill(strip.Color(0, 150, 0));
  strip.show();
  Serial.println("[blink_digital] LEDs = ON (verd), NUM_PIXELS=" + String(NUM_PIXELS));
  delay(1000);

  strip.clear();
  strip.show();
  Serial.println("[blink_digital] LEDs = OFF");
  delay(1000);
}
