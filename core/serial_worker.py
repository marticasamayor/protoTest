"""Worker de lectura serie en un thread separat.

Adaptat de ComToGraphic/ComToGraphic_app.py: mateix patró SerialWorker + QThread +
QTimer, pero emet linies de text lliure (els tests imprimeixen missatges humans,
no floats separats per espais per graficar).
"""

import serial
from PySide6.QtCore import QObject, Signal


class SerialWorker(QObject):
    line_received = Signal(str)
    error_occurred = Signal(str)
    connection_status = Signal(bool, str)

    def __init__(self):
        super().__init__()
        self.ser: serial.Serial | None = None
        self.running = False

    def connect_serial(self, port: str, baudrate: int) -> None:
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()

            self.ser = serial.Serial(port, baudrate, timeout=0.1)
            self.running = True
            self.connection_status.emit(True, f"Connectat a {port}")
        except Exception as e:
            self.connection_status.emit(False, f"Error: {e}")
            self.error_occurred.emit(f"Error obrint port: {e}")

    def read_data(self) -> None:
        if not self.running or not self.ser or not self.ser.is_open:
            return

        try:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    self.line_received.emit(line)
        except Exception as e:
            self.error_occurred.emit(f"Error llegint dades: {e}")

    def disconnect_serial(self) -> None:
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connection_status.emit(False, "Desconnectat")
