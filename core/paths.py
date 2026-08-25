"""Rutes centralitzades, compatibles amb execucio des de codi font i des d'un
executable PyInstaller (frozen).

- Recursos read-only (templates) es lligen del bundle (`sys._MEIPASS` en onefile).
- Directoris escrivibles (tools, build) van al costat de l'.exe, no dins del
  temp del bundle -- aixi arduino-cli i els sketches generats persisteixen entre
  execucions.
"""

import sys
from pathlib import Path

_SOURCE_ROOT = Path(__file__).resolve().parent.parent


def _is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def resource_dir() -> Path:
    """Arrel dels recursos empaquetats (read-only)."""
    if _is_frozen():
        return Path(getattr(sys, "_MEIPASS", _SOURCE_ROOT))
    return _SOURCE_ROOT


def app_dir() -> Path:
    """Directori escrivible persistent (al costat de l'executable)."""
    if _is_frozen():
        return Path(sys.executable).resolve().parent
    return _SOURCE_ROOT


TEMPLATES_DIR = resource_dir() / "templates"
TOOLS_DIR = app_dir() / "tools"
BUILD_ROOT = app_dir() / "build"
