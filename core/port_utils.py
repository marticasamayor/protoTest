"""Llistat de ports COM i reconnexio post-reset (upload esptool reinicia la placa)."""

import serial.tools.list_ports


def list_ports() -> list[str]:
    return [p.device for p in serial.tools.list_ports.comports()]


def snapshot() -> set[str]:
    """Conjunt de noms de port actuals -- per detectar ports nous despres d'un reset."""
    return set(list_ports())


def resolve_port_after_reset(preferred_device: str, previous_snapshot: set[str]) -> str | None:
    """Tria quin port fer servir despres d'una pujada.

    1. Si el port preferit (el que es feia servir abans de pujar) encara existeix, es fa servir
       (cas habitual: pont UART, el port es manté estable durant el reset).
    2. Si no, es busca un port nou que no fos al snapshot anterior (cas USB-CDC nadiu, que es
       pot re-enumerar amb un altre nom despres del reset).
    3. Si no es troba res, retorna None -- l'usuari haura de triar manualment.
    """
    current = set(list_ports())

    if preferred_device in current:
        return preferred_device

    new_ports = current - previous_snapshot
    if new_ports:
        return sorted(new_ports)[0]

    return None
