"""Deteccio, auto-instal-lacio i invocacio d'arduino-cli.

arduino-cli.exe es descarrega dins de protoTest/tools/ (gitignored) si no
es troba -- no es toca el PATH global de l'usuari, sempre es crida amb
ruta absoluta.
"""

import json
import re
import urllib.request
import zipfile
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, Signal

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"
CLI_EXE = TOOLS_DIR / "arduino-cli.exe"

LATEST_RELEASE_API = "https://api.github.com/repos/arduino/arduino-cli/releases/latest"
ASSET_NAME_RE = re.compile(r"^arduino-cli_.*_Windows_64bit\.zip$")
ESP32_BOARD_INDEX_URL = "https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json"
SPARKFUN_BOARD_INDEX_URL = "https://raw.githubusercontent.com/sparkfun/Arduino_Boards/master/IDE_Board_Manager/package_sparkfun_index.json"


def is_cli_installed() -> bool:
    return CLI_EXE.exists()


def _resolve_download_url() -> str:
    """Release assets son versionats (p.ex. arduino-cli_1.5.1_Windows_64bit.zip),
    no hi ha cap fitxer literal "latest" -- cal consultar l'API per trobar-lo."""
    with urllib.request.urlopen(LATEST_RELEASE_API, timeout=15) as resp:
        release = json.loads(resp.read().decode("utf-8"))

    for asset in release.get("assets", []):
        if ASSET_NAME_RE.match(asset["name"]):
            return asset["browser_download_url"]

    raise FileNotFoundError(
        f"Cap asset Windows_64bit.zip trobat a la darrera release ({release.get('tag_name')})"
    )


def download_and_install_cli(log) -> None:
    """Descarrega arduino-cli.exe i el desa a tools/. Bloquejant -- cridar des d'un worker thread."""
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = TOOLS_DIR / "arduino-cli.zip"

    download_url = _resolve_download_url()
    log(f"[SETUP] Descarregant arduino-cli des de {download_url} ...")
    urllib.request.urlretrieve(download_url, zip_path)
    log("[SETUP] Descarrega completada, extraient...")

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(TOOLS_DIR)

    zip_path.unlink(missing_ok=True)

    if not CLI_EXE.exists():
        raise FileNotFoundError(f"arduino-cli.exe no trobat despres d'extreure a {TOOLS_DIR}")

    log(f"[SETUP] arduino-cli instal-lat a {CLI_EXE}")


class CliRunner(QObject):
    """Executa una comanda arduino-cli via QProcess, emetent sortida linia a linia."""

    line_output = Signal(str)
    process_finished = Signal(bool)  # True si exit code == 0

    def __init__(self, parent=None):
        super().__init__(parent)
        self._process: QProcess | None = None

    def run(self, args: list[str]) -> None:
        if self._process is not None:
            self.line_output.emit("Ja hi ha un proces arduino-cli en marxa")
            return

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._on_ready_read)
        self._process.finished.connect(self._on_finished)
        self._process.start(str(CLI_EXE), args)

    def _on_ready_read(self) -> None:
        data = bytes(self._process.readAllStandardOutput())
        text = data.decode("utf-8", errors="ignore")
        for line in text.splitlines():
            if line.strip():
                self.line_output.emit(line.rstrip())

    def _on_finished(self, exit_code: int, _exit_status) -> None:
        self._process = None
        self.process_finished.emit(exit_code == 0)

    def is_running(self) -> bool:
        return self._process is not None

    def kill(self) -> None:
        if self._process is not None:
            self._process.kill()


def compile_args(fqbn: str, sketch_dir: Path) -> list[str]:
    return ["compile", "--fqbn", fqbn, str(sketch_dir)]


def upload_args(fqbn: str, port: str, sketch_dir: Path) -> list[str]:
    return ["upload", "-p", port, "--fqbn", fqbn, str(sketch_dir)]
