"""Registre de tests disponibles. Afegir un test nou = 1 entrada aqui + 1 template .ino."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldRole:
    key: str  # token del placeholder al template, p.ex. "LED_PIN" -> __LED_PIN__
    label: str  # text mostrat al formulari
    kind: str  # "pin" (GPIO -- participa en la validacio de duplicats) | "param" (numero lliure, p.ex. quantitat)
    default: int  # nomes usat com a placeholder/suggeriment, el camp comença en blanc
    min_value: int = 0
    max_value: int = 48
    direction: str | None = None  # "output" | "input" | "input_pullup" | "io" -- informatiu, nomes per pins


@dataclass(frozen=True)
class TestDefinition:
    id: str
    label: str
    description: str
    template_file: str
    fields: tuple[FieldRole, ...] = ()
    baud_rate: int = 115200


TEST_REGISTRY: dict[str, TestDefinition] = {
    "blink": TestDefinition(
        id="blink",
        label="Blink",
        description="Parpelleja un LED connectat a un pin digital.",
        template_file="blink.ino.tpl",
        fields=(
            FieldRole(key="LED_PIN", label="Pin LED", kind="pin", direction="output", default=2),
        ),
    ),
    "blink_digital": TestDefinition(
        id="blink_digital",
        label="Blink Digital (WS2812)",
        description="Parpelleja LEDs addressables WS2812/NeoPixel.",
        template_file="blink_digital.ino.tpl",
        fields=(
            FieldRole(key="DATA_PIN", label="Pin de dades", kind="pin", direction="output", default=4),
            FieldRole(key="NUM_PIXELS", label="Nombre de LEDs", kind="param", default=1, min_value=1, max_value=300),
        ),
    ),
    "counter": TestDefinition(
        id="counter",
        label="Counter",
        description="Imprimeix un comptador incremental per Serial (sense hardware extern).",
        template_file="counter.ino.tpl",
        fields=(),
    ),
    "button": TestDefinition(
        id="button",
        label="Button",
        description="Llegeix un pin de boto i imprimeix els canvis d'estat per Serial (sense LED).",
        template_file="button.ino.tpl",
        fields=(
            FieldRole(key="BUTTON_PIN", label="Pin boto (input pull-up)", kind="pin", direction="input_pullup", default=9),
        ),
    ),
    "i2c_scanner": TestDefinition(
        id="i2c_scanner",
        label="I2C Scanner",
        description="Escaneja el bus I2C i imprimeix les adreces dels dispositius trobats.",
        template_file="i2c_scanner.ino.tpl",
        fields=(
            FieldRole(key="SDA_PIN", label="Pin SDA", kind="pin", direction="io", default=8),
            FieldRole(key="SCL_PIN", label="Pin SCL", kind="pin", direction="io", default=9),
        ),
    ),
    "sd_card_spi": TestDefinition(
        id="sd_card_spi",
        label="SD Card (SPI)",
        description="Munta una targeta microSD per SPI i llista els fitxers arrel per Serial.",
        template_file="sd_card_spi.ino.tpl",
        fields=(
            FieldRole(key="MISO_PIN", label="Pin MISO", kind="pin", direction="input", default=3),
            FieldRole(key="MOSI_PIN", label="Pin MOSI", kind="pin", direction="output", default=7),
            FieldRole(key="SCK_PIN", label="Pin SCK", kind="pin", direction="output", default=6),
            FieldRole(key="CS_PIN", label="Pin CS", kind="pin", direction="output", default=10),
        ),
    ),
    "oled_128x32": TestDefinition(
        id="oled_128x32",
        label="OLED 128x32 (I2C)",
        description="Inicialitza una pantalla SSD1306 128x32 per I2C i mostra un patro de prova.",
        template_file="oled_128x32.ino.tpl",
        fields=(
            FieldRole(key="SDA_PIN", label="Pin SDA", kind="pin", direction="io", default=8),
            FieldRole(key="SCL_PIN", label="Pin SCL", kind="pin", direction="io", default=9),
        ),
    ),
    "wifi_scan": TestDefinition(
        id="wifi_scan",
        label="WiFi Scan",
        description="Escaneja xarxes WiFi properes i les imprimeix per Serial (sense hardware extern).",
        template_file="wifi_scan.ino.tpl",
        fields=(),
    ),
}
