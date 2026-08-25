"""Formulari de camps generat dinamicament segons TestDefinition.fields.

Els camps comencen en blanc (sense valor predefinit) -- nomes es mostra el
GPIO/valor suggerit com a placeholder (text gris), per evitar que l'usuari
flashegi sense haver triat conscientment els pins reals de la seva PCB.

Excepcio: el camp LED_PIN es preomple amb el LED_BUILTIN de la placa
seleccionada (quan es coneix), ja que aquest pin no depen del cablejat de
l'usuari sino nomes de la placa.
"""

from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QFormLayout, QLineEdit, QWidget

from core.boards import BoardDefinition
from core.tests_registry import TestDefinition


class PinFieldsWidget(QWidget):
    values_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QFormLayout(self)
        self._fields: dict[str, QLineEdit] = {}
        self._pin_keys: set[str] = set()

    def rebuild(self, test: TestDefinition, board: BoardDefinition | None = None) -> None:
        while self._layout.rowCount():
            self._layout.removeRow(0)
        self._fields.clear()
        self._pin_keys.clear()

        if not test.fields:
            self._layout.addRow("(aquest test no necessita cap valor)", QWidget())
            return

        for role in test.fields:
            edit = QLineEdit()
            edit.setValidator(QIntValidator(role.min_value, role.max_value, edit))
            edit.setPlaceholderText(f"p.ex. {role.default}")
            if role.key == "LED_PIN" and board is not None and board.led_builtin_pin is not None:
                edit.setText(str(board.led_builtin_pin))
            edit.textChanged.connect(lambda _text: self.values_changed.emit())
            self._fields[role.key] = edit
            if role.kind == "pin":
                self._pin_keys.add(role.key)
            self._layout.addRow(f"{role.label}:", edit)

    def get_values(self) -> dict[str, int]:
        return {key: int(edit.text()) for key, edit in self._fields.items()}

    def validate(self) -> str | None:
        """Retorna un missatge d'error si falta algun valor o hi ha pins duplicats, sino None."""
        for key, edit in self._fields.items():
            if not edit.text().strip():
                return f"Falta introduir un valor per '{key}'"

        seen: dict[int, str] = {}
        for key in self._pin_keys:
            value = int(self._fields[key].text())
            if value in seen:
                return f"Pin {value} assignat dues vegades ({seen[value]} i {key})"
            seen[value] = key

        return None
