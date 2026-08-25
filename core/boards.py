"""Registre de plaques ESP32 suportades. Afegir una placa nova = 1 entrada aqui."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BoardDefinition:
    id: str
    label: str
    fqbn: str
    supports_native_usb: bool
    cdc_option_key: str | None = "CDCOnBoot"
    led_builtin_pin: int | None = None
    pre_flash_note: str | None = None
    datasheet_url: str | None = None

    def fqbn_for(self, use_usb: bool) -> str:
        """FQBN complet, amb l'opcio CDCOnBoot afegida si la placa suporta USB natiu."""
        if not self.supports_native_usb or self.cdc_option_key is None:
            return self.fqbn
        value = "cdc" if use_usb else "default"
        return f"{self.fqbn}:{self.cdc_option_key}={value}"


BOARD_REGISTRY: dict[str, BoardDefinition] = {
    "esp32": BoardDefinition(
        id="esp32",
        label="ESP32 (Dev Module / WROOM)",
        fqbn="esp32:esp32:esp32",
        supports_native_usb=False,
        cdc_option_key=None,
        led_builtin_pin=2,
        datasheet_url="https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf",
    ),
    "esp32s2": BoardDefinition(
        id="esp32s2",
        label="ESP32-S2",
        fqbn="esp32:esp32:esp32s2",
        supports_native_usb=True,
        datasheet_url="https://www.espressif.com/sites/default/files/documentation/esp32-s2_datasheet_en.pdf",
    ),
    "esp32s3": BoardDefinition(
        id="esp32s3",
        label="ESP32-S3",
        fqbn="esp32:esp32:esp32s3",
        supports_native_usb=True,
        datasheet_url="https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf",
    ),
    "esp32c3": BoardDefinition(
        id="esp32c3",
        label="ESP32-C3",
        fqbn="esp32:esp32:esp32c3",
        supports_native_usb=True,
        datasheet_url="https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf",
    ),
    "esp32c6": BoardDefinition(
        id="esp32c6",
        label="ESP32-C6",
        fqbn="esp32:esp32:esp32c6",
        supports_native_usb=True,
        datasheet_url="https://www.espressif.com/sites/default/files/documentation/esp32-c6_datasheet_en.pdf",
    ),
    "uno": BoardDefinition(
        id="uno",
        label="Arduino Uno",
        fqbn="arduino:avr:uno",
        supports_native_usb=False,
        cdc_option_key=None,
        led_builtin_pin=13,
        datasheet_url="https://docs.arduino.cc/resources/datasheets/A000066-datasheet.pdf",
    ),
    "mega": BoardDefinition(
        id="mega",
        label="Arduino Mega 2560",
        fqbn="arduino:avr:mega",
        supports_native_usb=False,
        cdc_option_key=None,
        led_builtin_pin=13,
        datasheet_url="https://docs.arduino.cc/resources/datasheets/A000067-datasheet.pdf",
    ),
    "nano": BoardDefinition(
        id="nano",
        label="Arduino Nano",
        fqbn="arduino:avr:nano",
        supports_native_usb=False,
        cdc_option_key=None,
        led_builtin_pin=13,
        datasheet_url="https://docs.arduino.cc/resources/datasheets/A000005-datasheet.pdf",
    ),
    "uno_r4_minima": BoardDefinition(
        id="uno_r4_minima",
        label="Arduino Uno R4 Minima",
        fqbn="arduino:renesas_uno:minima",
        supports_native_usb=False,
        cdc_option_key=None,
        led_builtin_pin=13,
        pre_flash_note=(
            "Abans de Flashejar, posa la placa en mode bootloader pressionant dos cops "
            "seguits el boto RESET — aleshores el LED parpellejara de forma dinamica."
        ),
        datasheet_url="https://docs.arduino.cc/resources/datasheets/ABX00080-datasheet.pdf",
    ),
    "uno_r4_wifi": BoardDefinition(
        id="uno_r4_wifi",
        label="Arduino Uno R4 WiFi",
        fqbn="arduino:renesas_uno:unor4wifi",
        supports_native_usb=False,
        cdc_option_key=None,
        led_builtin_pin=13,
        pre_flash_note=(
            "Abans de Flashejar, posa la placa en mode bootloader pressionant dos cops "
            "seguits el boto RESET — aleshores el LED parpellejara de forma dinamica."
        ),
        datasheet_url="https://docs.arduino.cc/resources/datasheets/ABX00087-datasheet.pdf",
    ),
    "sparkfun_pro_micro": BoardDefinition(
        id="sparkfun_pro_micro",
        label="SparkFun Pro Micro (ATmega32U4)",
        fqbn="SparkFun:avr:promicro",
        supports_native_usb=False,
        cdc_option_key=None,
        datasheet_url="https://learn.sparkfun.com/tutorials/pro-micro--fio-v3-hookup-guide",
    ),
}
