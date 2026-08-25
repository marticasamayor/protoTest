"""Genera un sketch .ino a partir d'un template + valors de pins."""

import re
from pathlib import Path

from core.tests_registry import TestDefinition

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

_PLACEHOLDER_RE = re.compile(r"__[A-Z0-9_]+__")


class CodegenError(Exception):
    pass


def generate_sketch(test: TestDefinition, field_values: dict[str, int], build_root: Path) -> Path:
    """Escriu build_root/<test.id>/<test.id>.ino i en retorna la ruta.

    El nom de carpeta ha de coincidir amb el nom del .ino (requisit d'arduino-cli).
    """
    template_path = TEMPLATES_DIR / test.template_file
    if not template_path.exists():
        raise CodegenError(f"Template no trobat: {template_path}")

    text = template_path.read_text(encoding="utf-8")

    for role in test.fields:
        token = f"__{role.key}__"
        if token not in text:
            raise CodegenError(f"{test.template_file} no conte el placeholder {token}")
        if role.key not in field_values:
            raise CodegenError(f"Falta valor per {role.key}")
        text = text.replace(token, str(field_values[role.key]))

    text = text.replace("__BAUD_RATE__", str(test.baud_rate))

    remaining = _PLACEHOLDER_RE.findall(text)
    if remaining:
        raise CodegenError(f"Placeholders sense substituir: {', '.join(sorted(set(remaining)))}")

    sketch_dir = build_root / test.id
    sketch_dir.mkdir(parents=True, exist_ok=True)
    ino_path = sketch_dir / f"{test.id}.ino"
    ino_path.write_text(text, encoding="utf-8")
    return ino_path
