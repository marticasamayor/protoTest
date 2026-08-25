"""Consola negra unificada: sortida de build/upload (subprocess) i serial en viu."""

from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QHBoxLayout, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget

TAG_COLORS = {
    "BUILD": "#5599ff",
    "UPLOAD": "#ffaa33",
    "SERIAL": "#55ff55",
    "APP": "#cccccc",
    "ERROR": "#ff5555",
}


class ConsoleWidget(QWidget):
    stop_monitor_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setStyleSheet(
            "background-color: #0c0c0c; color: #dddddd; font-family: Consolas, monospace;"
        )

        clear_btn = QPushButton("Netejar")
        clear_btn.clicked.connect(self.text.clear)

        self.stop_monitor_btn = QPushButton("Aturar monitor")
        self.stop_monitor_btn.setEnabled(False)
        self.stop_monitor_btn.clicked.connect(self.stop_monitor_requested.emit)

        toolbar = QHBoxLayout()
        toolbar.addWidget(clear_btn)
        toolbar.addWidget(self.stop_monitor_btn)
        toolbar.addStretch()

        layout = QVBoxLayout(self)
        layout.addWidget(self.text)
        layout.addLayout(toolbar)

    def set_monitor_active(self, active: bool) -> None:
        self.stop_monitor_btn.setEnabled(active)

    def append_tagged(self, tag: str, line: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = TAG_COLORS.get(tag, "#dddddd")
        html = f'<span style="color:#777777">[{timestamp}]</span> <span style="color:{color}">[{tag}]</span> {_escape(line)}'
        self.text.appendHtml(html)
        cursor = self.text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.text.setTextCursor(cursor)
        self.text.ensureCursorVisible()


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
