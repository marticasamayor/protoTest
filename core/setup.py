"""Comprovacions i configuracio de primer arrencament: arduino-cli + core esp32.

Tot aixo pot trigar (descarrega + instal-lacio de core), aixi que corre en un
QThread separat via SetupWorker, no bloqueja la GUI.
"""

import json
import subprocess

from PySide6.QtCore import QObject, Signal

from core import arduino_cli

REQUIRED_LIBRARIES = ["Adafruit NeoPixel", "Adafruit GFX Library", "Adafruit SSD1306"]


def _run_and_stream(args: list[str], log) -> bool:
    """Executa arduino-cli amb els args donats, emet cada linia a `log`. Retorna True si exit 0."""
    log(f"[SETUP] $ arduino-cli {' '.join(args)}")
    process = subprocess.Popen(
        [str(arduino_cli.CLI_EXE), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    for line in process.stdout:
        line = line.rstrip()
        if line:
            log(f"[SETUP] {line}")
    process.wait()
    return process.returncode == 0


def _is_core_installed(core_id: str) -> bool:
    try:
        result = subprocess.run(
            [str(arduino_cli.CLI_EXE), "core", "list", "--format", "json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=30,
        )
        cores = json.loads(result.stdout or "{}")
        # arduino-cli >=0.35 wraps the list under "platforms"
        entries = cores.get("platforms", cores) if isinstance(cores, dict) else cores
        return any(entry.get("id") == core_id for entry in entries)
    except Exception:
        return False


def is_esp32_core_installed() -> bool:
    return _is_core_installed("esp32:esp32")


def is_avr_core_installed() -> bool:
    return _is_core_installed("arduino:avr")


def is_renesas_uno_core_installed() -> bool:
    return _is_core_installed("arduino:renesas_uno")


def is_sparkfun_avr_core_installed() -> bool:
    return _is_core_installed("SparkFun:avr")


class SetupWorker(QObject):
    log = Signal(str)
    finished = Signal(bool, str)

    def run_setup(self) -> None:
        try:
            if not arduino_cli.is_cli_installed():
                arduino_cli.download_and_install_cli(lambda msg: self.log.emit(msg))
            else:
                self.log.emit(f"[SETUP] arduino-cli ja instal-lat a {arduino_cli.CLI_EXE}")

            # config init pot fallar si ja existeix -- no es fatal
            _run_and_stream(["config", "init", "--overwrite"], self.log.emit)

            _run_and_stream(
                ["config", "add", "board_manager.additional_urls", arduino_cli.ESP32_BOARD_INDEX_URL],
                self.log.emit,
            )
            _run_and_stream(
                ["config", "add", "board_manager.additional_urls", arduino_cli.SPARKFUN_BOARD_INDEX_URL],
                self.log.emit,
            )

            if not _run_and_stream(["core", "update-index"], self.log.emit):
                self.finished.emit(False, "Error actualitzant l'index de cores")
                return

            if not is_esp32_core_installed():
                if not _run_and_stream(["core", "install", "esp32:esp32"], self.log.emit):
                    self.finished.emit(False, "Error instal-lant el core esp32:esp32")
                    return
            else:
                self.log.emit("[SETUP] Core esp32:esp32 ja instal-lat")

            if not is_avr_core_installed():
                if not _run_and_stream(["core", "install", "arduino:avr"], self.log.emit):
                    self.finished.emit(False, "Error instal-lant el core arduino:avr")
                    return
            else:
                self.log.emit("[SETUP] Core arduino:avr ja instal-lat")

            if not is_renesas_uno_core_installed():
                if not _run_and_stream(["core", "install", "arduino:renesas_uno"], self.log.emit):
                    self.finished.emit(False, "Error instal-lant el core arduino:renesas_uno")
                    return
            else:
                self.log.emit("[SETUP] Core arduino:renesas_uno ja instal-lat")

            if not is_sparkfun_avr_core_installed():
                if not _run_and_stream(["core", "install", "SparkFun:avr"], self.log.emit):
                    self.finished.emit(False, "Error instal-lant el core SparkFun:avr")
                    return
            else:
                self.log.emit("[SETUP] Core SparkFun:avr ja instal-lat")

            for lib in REQUIRED_LIBRARIES:
                _run_and_stream(["lib", "install", lib], self.log.emit)

            self.finished.emit(True, "Configuracio completada")
        except Exception as exc:
            self.finished.emit(False, f"Error de configuracio: {exc}")
