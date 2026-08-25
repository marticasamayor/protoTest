import sys

from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication, QDialog, QPlainTextEdit, QPushButton, QVBoxLayout

from core import arduino_cli, setup
from gui.main_window import MainWindow


class SetupDialog(QDialog):
    """Diàleg de primer arrencament: instal·la arduino-cli + core esp32 si cal."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuracio inicial")
        self.resize(700, 400)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.close_btn = QPushButton("Continuar")
        self.close_btn.setEnabled(False)
        self.close_btn.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(self.log_view)
        layout.addWidget(self.close_btn)

        self.thread = QThread()
        self.worker = setup.SetupWorker()
        self.worker.moveToThread(self.thread)
        self.worker.log.connect(self.log_view.appendPlainText)
        self.worker.finished.connect(self._on_finished)
        self.thread.started.connect(self.worker.run_setup)
        self.thread.start()

    def _on_finished(self, ok: bool, message: str) -> None:
        self.log_view.appendPlainText(("[OK] " if ok else "[ERROR] ") + message)
        self.close_btn.setEnabled(True)
        self.thread.quit()
        self.thread.wait()


def needs_setup() -> bool:
    return (
        not arduino_cli.is_cli_installed()
        or not setup.is_esp32_core_installed()
        or not setup.is_avr_core_installed()
        or not setup.is_renesas_uno_core_installed()
        or not setup.is_sparkfun_avr_core_installed()
    )


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    if needs_setup():
        dialog = SetupDialog()
        dialog.exec()

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
