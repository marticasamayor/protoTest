"""Finestra principal: orquestra generacio -> compilacio -> pujada -> monitor serial."""

import shutil
from pathlib import Path

import serial.tools.list_ports
from PySide6.QtCore import QThread, QTimer
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from core import codegen, port_utils
from core.arduino_cli import CliRunner, compile_args, upload_args
from core.boards import BOARD_REGISTRY, BoardDefinition
from core.serial_worker import SerialWorker
from core.tests_registry import TEST_REGISTRY, TestDefinition
from gui.console_widget import ConsoleWidget
from gui.pin_fields_widget import PinFieldsWidget

BUILD_ROOT = Path(__file__).resolve().parent.parent / "build"

RECONNECT_POLL_MS = 300
RECONNECT_TIMEOUT_MS = 8000

BASIC_TEST_IDS = ("blink", "counter", "button")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("protoTest — banc de proves ESP32")
        self.setGeometry(100, 100, 650, 750)

        self._state = "IDLE"
        self._port_snapshot: set[str] = set()
        self._reconnect_elapsed_ms = 0
        self._preferred_port: str | None = None
        self._stopping = False
        self._last_compiled: dict | None = None

        self._setup_ui()
        self._setup_serial_worker()
        self._setup_cli_runner()

        self._reconnect_timer = QTimer(self)
        self._reconnect_timer.setInterval(RECONNECT_POLL_MS)
        self._reconnect_timer.timeout.connect(self._poll_reconnect)

        self._on_test_combo_changed(self.test_combo.currentIndex())

    # ---------- UI ----------

    def _setup_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)

        config_row = QHBoxLayout()
        config_row.addWidget(self._build_board_group())
        config_row.addWidget(self._build_uart_usb_group())
        config_row.addWidget(self._build_port_group())
        layout.addLayout(config_row)

        layout.addWidget(self._build_test_group())

        self.pin_fields = PinFieldsWidget()
        self.pin_fields.values_changed.connect(self._invalidate_compiled)
        pin_group = QGroupBox("Pins")
        pin_layout = QVBoxLayout(pin_group)
        pin_layout.addWidget(self.pin_fields)
        layout.addWidget(pin_group)

        run_row = QHBoxLayout()
        self.compile_burn_btn = QPushButton("Compilar i Flashejar")
        self.compile_burn_btn.clicked.connect(self._on_compile_burn_clicked)
        self.flash_btn = QPushButton("Flashejar")
        self.flash_btn.setEnabled(False)
        self.flash_btn.clicked.connect(self._on_flash_clicked)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        self.status_label = QLabel("Inactiu")
        self.status_label.setStyleSheet("padding: 5px; background-color: #eeeeee;")
        run_row.addWidget(self.compile_burn_btn)
        run_row.addWidget(self.flash_btn)
        run_row.addWidget(self.stop_btn)
        run_row.addWidget(self.status_label, 1)
        layout.addLayout(run_row)

        self.console = ConsoleWidget()
        self.console.stop_monitor_requested.connect(self._stop_monitor)
        layout.addWidget(self.console, 1)

        self.setCentralWidget(central)

    def _build_board_group(self) -> QGroupBox:
        group = QGroupBox("Microcontrolador")
        outer = QVBoxLayout(group)
        self.board_combo = QComboBox()
        for board in BOARD_REGISTRY.values():
            self.board_combo.addItem(board.label, board.id)
        self.board_combo.currentIndexChanged.connect(lambda _index: self._on_board_changed())
        outer.addWidget(self.board_combo)
        self.board_datasheet_label = QLabel("")
        self.board_datasheet_label.setOpenExternalLinks(True)
        self.board_datasheet_label.setVisible(False)
        outer.addWidget(self.board_datasheet_label)
        self.board_note_label = QLabel("")
        self.board_note_label.setWordWrap(True)
        self.board_note_label.setStyleSheet(
            "color: #7a5b00; background-color: #fff3cd; padding: 4px; border-radius: 3px;"
        )
        self.board_note_label.setVisible(False)
        outer.addWidget(self.board_note_label)
        return group

    def _build_uart_usb_group(self) -> QGroupBox:
        group = QGroupBox("Interficie")
        row = QHBoxLayout(group)
        self.uart_radio = QRadioButton("UART")
        self.usb_radio = QRadioButton("USB")
        self.uart_radio.setChecked(True)
        self.uart_usb_group = QButtonGroup(self)
        self.uart_usb_group.addButton(self.uart_radio)
        self.uart_usb_group.addButton(self.usb_radio)
        row.addWidget(self.uart_radio)
        row.addWidget(self.usb_radio)
        self.uart_radio.toggled.connect(lambda checked: self._invalidate_compiled() if checked else None)
        self.usb_radio.toggled.connect(lambda checked: self._invalidate_compiled() if checked else None)
        self._on_board_changed()
        return group

    def _build_test_group(self) -> QGroupBox:
        group = QGroupBox("Test")
        row = QHBoxLayout(group)

        row.addWidget(QLabel("Test:"))
        self.test_combo = QComboBox()
        for test in TEST_REGISTRY.values():
            self.test_combo.addItem(test.label, test.id)
        self.test_combo.currentIndexChanged.connect(self._on_test_combo_changed)
        row.addWidget(self.test_combo, 1)

        default_test_id = next(iter(TEST_REGISTRY))
        self.test_radio_group = QButtonGroup(self)
        for test_id in BASIC_TEST_IDS:
            test = TEST_REGISTRY[test_id]
            radio = QRadioButton(test.label)
            radio.setToolTip(test.description)
            radio.setProperty("test_id", test.id)
            if test_id == default_test_id:
                radio.setChecked(True)
            radio.toggled.connect(
                lambda checked, tid=test.id: self._on_test_radio_toggled(tid) if checked else None
            )
            self.test_radio_group.addButton(radio)
            row.addWidget(radio)
        return group

    def _build_port_group(self) -> QGroupBox:
        group = QGroupBox("Port")
        row = QHBoxLayout(group)
        self.port_combo = QComboBox()
        self._refresh_ports()
        refresh_btn = QPushButton("Actualitzar")
        refresh_btn.clicked.connect(self._refresh_ports)
        row.addWidget(QLabel("Port COM:"))
        row.addWidget(self.port_combo, 1)
        row.addWidget(refresh_btn)
        return group

    # ---------- helpers ----------

    def _selected_board(self) -> BoardDefinition:
        board_id = self.board_combo.currentData()
        return BOARD_REGISTRY[board_id]

    def _selected_test(self) -> TestDefinition:
        test_id = self.test_combo.currentData()
        return TEST_REGISTRY[test_id]

    def _refresh_ports(self) -> None:
        current = self.port_combo.currentText()
        self.port_combo.clear()
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo.addItems(ports)
        if current in ports:
            self.port_combo.setCurrentText(current)

    def _on_board_changed(self, refresh_pins: bool = True) -> None:
        board = self._selected_board()
        self.uart_radio.setEnabled(board.supports_native_usb)
        self.usb_radio.setEnabled(board.supports_native_usb)
        if not board.supports_native_usb:
            self.uart_radio.setChecked(True)
        if hasattr(self, "board_datasheet_label"):
            url = board.datasheet_url or ""
            self.board_datasheet_label.setText(f'<a href="{url}">Datasheet</a>' if url else "")
            self.board_datasheet_label.setVisible(bool(url))
        if hasattr(self, "board_note_label"):
            note = board.pre_flash_note or ""
            self.board_note_label.setText(note)
            self.board_note_label.setVisible(bool(note))
        if refresh_pins and hasattr(self, "pin_fields"):
            self.pin_fields.rebuild(self._selected_test(), board)
            self._invalidate_compiled()

    def _on_test_combo_changed(self, index: int) -> None:
        test_id = self.test_combo.itemData(index)
        buttons = self.test_radio_group.buttons()
        match = next((b for b in buttons if b.property("test_id") == test_id), None)
        if match is not None:
            if not match.isChecked():
                match.setChecked(True)
        else:
            # Un grup exclusiu no permet desmarcar l'unic boto marcat via setChecked(False)
            # (Qt el torna a marcar) -- cal desactivar l'exclusivitat temporalment.
            self.test_radio_group.setExclusive(False)
            for btn in buttons:
                btn.setChecked(False)
            self.test_radio_group.setExclusive(True)
        self._invalidate_compiled()
        if hasattr(self, "pin_fields"):
            self.pin_fields.rebuild(self._selected_test(), self._selected_board())

    def _on_test_radio_toggled(self, test_id: str) -> None:
        idx = self.test_combo.findData(test_id)
        if idx != -1 and idx != self.test_combo.currentIndex():
            self.test_combo.setCurrentIndex(idx)

    def _invalidate_compiled(self) -> None:
        if self._last_compiled is not None:
            shutil.rmtree(self._last_compiled["sketch_dir"], ignore_errors=True)
            self._last_compiled = None
        if hasattr(self, "flash_btn"):
            self.flash_btn.setEnabled(False)

    # ---------- serial worker ----------

    def _setup_serial_worker(self) -> None:
        self.worker_thread = QThread()
        self.serial_worker = SerialWorker()
        self.serial_worker.moveToThread(self.worker_thread)
        self.serial_worker.line_received.connect(self._on_serial_line)
        self.serial_worker.error_occurred.connect(self._on_serial_error)
        self.serial_worker.connection_status.connect(self._on_serial_status)
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.serial_worker.read_data)
        self.data_timer.setInterval(20)
        self.worker_thread.start()

    def _on_serial_line(self, line: str) -> None:
        self.console.append_tagged("SERIAL", line)

    def _on_serial_error(self, msg: str) -> None:
        self.console.append_tagged("ERROR", msg)

    def _on_serial_status(self, connected: bool, message: str) -> None:
        self.console.append_tagged("APP", message)
        self.console.set_monitor_active(connected)

    def _stop_monitor(self) -> None:
        self.data_timer.stop()
        self.serial_worker.disconnect_serial()
        self._set_state("IDLE")

    # ---------- arduino-cli ----------

    def _setup_cli_runner(self) -> None:
        self.cli_runner = CliRunner(self)
        self.cli_runner.line_output.connect(self._on_cli_line)

    def _on_cli_line(self, line: str) -> None:
        tag = "UPLOAD" if self._state == "UPLOADING" else "BUILD"
        self.console.append_tagged(tag, line)

    # ---------- state machine ----------

    def _set_state(self, state: str) -> None:
        self._state = state
        labels = {
            "IDLE": ("Inactiu", "#eeeeee"),
            "GENERATING": ("Generant sketch...", "#fff3cd"),
            "COMPILING": ("Compilant...", "#cfe2ff"),
            "UPLOADING": ("Pujant...", "#ffe5cc"),
            "WAITING_FOR_PORT": ("Esperant reconnexio...", "#ffe5cc"),
            "MONITORING": ("Monitoritzant", "#ccffcc"),
            "ERROR": ("Error", "#ffcccc"),
        }
        text, color = labels.get(state, (state, "#eeeeee"))
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"padding: 5px; background-color: {color};")
        busy = state in ("GENERATING", "COMPILING", "UPLOADING", "WAITING_FOR_PORT")
        self.compile_burn_btn.setEnabled(not busy)
        self.flash_btn.setEnabled(not busy and self._last_compiled is not None)
        self.stop_btn.setEnabled(busy)
        self.board_combo.setEnabled(not busy)
        self.port_combo.setEnabled(not busy)
        self.pin_fields.setEnabled(not busy)
        self.test_combo.setEnabled(not busy)
        for btn in self.test_radio_group.buttons():
            btn.setEnabled(not busy)
        if not busy:
            self._on_board_changed(refresh_pins=False)  # restaura uart/usb, sense refer els pins
        else:
            self.uart_radio.setEnabled(False)
            self.usb_radio.setEnabled(False)

    def _on_stop_clicked(self) -> None:
        self._stopping = True
        if self.cli_runner.is_running():
            self.cli_runner.kill()
        if self._reconnect_timer.isActive():
            self._reconnect_timer.stop()
        self.console.append_tagged("APP", "Aturat per l'usuari")
        self._set_state("IDLE")

    def _on_compile_burn_clicked(self) -> None:
        test = self._selected_test()
        board = self._selected_board()
        port = self.port_combo.currentText()

        if not port:
            QMessageBox.warning(self, "Falta port", "Selecciona un port COM")
            return

        field_error = self.pin_fields.validate()
        if field_error:
            QMessageBox.warning(self, "Valors invalids", field_error)
            return

        if self.console.stop_monitor_btn.isEnabled():
            self._stop_monitor()

        self._stopping = False
        self._set_state("GENERATING")
        try:
            field_values = self.pin_fields.get_values()
            sketch_path = codegen.generate_sketch(test, field_values, BUILD_ROOT)
        except codegen.CodegenError as exc:
            self.console.append_tagged("ERROR", str(exc))
            self._set_state("ERROR")
            return
        self.console.append_tagged("APP", f"Sketch generat: {sketch_path}")

        self._pending_test = test
        self._pending_board = board
        self._pending_port = port
        self._pending_sketch_dir = sketch_path.parent

        fqbn = board.fqbn_for(use_usb=self.usb_radio.isChecked())
        self._pending_fqbn = fqbn

        self._set_state("COMPILING")
        self.cli_runner.process_finished.connect(self._on_compile_finished)
        self.cli_runner.run(compile_args(fqbn, self._pending_sketch_dir))

    def _on_compile_finished(self, ok: bool) -> None:
        self.cli_runner.process_finished.disconnect(self._on_compile_finished)
        if self._stopping:
            self._stopping = False
            return
        if not ok:
            self.console.append_tagged("ERROR", "Compilacio fallida")
            self._set_state("ERROR")
            return

        self._last_compiled = {
            "test": self._pending_test,
            "board": self._pending_board,
            "fqbn": self._pending_fqbn,
            "sketch_dir": self._pending_sketch_dir,
        }
        self.flash_btn.setEnabled(True)

        self._port_snapshot = port_utils.snapshot()
        self._preferred_port = self._pending_port

        self._set_state("UPLOADING")
        self.cli_runner.process_finished.connect(self._on_upload_finished)
        self.cli_runner.run(upload_args(self._pending_fqbn, self._pending_port, self._pending_sketch_dir))

    def _on_flash_clicked(self) -> None:
        if self._last_compiled is None:
            return
        port = self.port_combo.currentText()

        if not port:
            QMessageBox.warning(self, "Falta port", "Selecciona un port COM")
            return

        if self.console.stop_monitor_btn.isEnabled():
            self._stop_monitor()

        self._stopping = False
        self._pending_test = self._last_compiled["test"]
        self._pending_board = self._last_compiled["board"]
        self._pending_port = port
        self._pending_sketch_dir = self._last_compiled["sketch_dir"]
        self._pending_fqbn = self._last_compiled["fqbn"]

        self._port_snapshot = port_utils.snapshot()
        self._preferred_port = port

        self._set_state("UPLOADING")
        self.cli_runner.process_finished.connect(self._on_upload_finished)
        self.cli_runner.run(upload_args(self._pending_fqbn, self._pending_port, self._pending_sketch_dir))

    def _on_upload_finished(self, ok: bool) -> None:
        self.cli_runner.process_finished.disconnect(self._on_upload_finished)
        if self._stopping:
            self._stopping = False
            return
        if not ok:
            self.console.append_tagged("ERROR", "Pujada fallida")
            self._set_state("ERROR")
            return

        self.console.append_tagged("APP", "Pujada completada, esperant reconnexio del port...")
        self._set_state("WAITING_FOR_PORT")
        self._reconnect_elapsed_ms = 0
        self._reconnect_timer.start()

    def _poll_reconnect(self) -> None:
        self._reconnect_elapsed_ms += RECONNECT_POLL_MS
        resolved = port_utils.resolve_port_after_reset(self._preferred_port, self._port_snapshot)

        if resolved is not None:
            self._reconnect_timer.stop()
            self.console.append_tagged("APP", f"Port trobat: {resolved}")
            baud = self._pending_test.baud_rate
            self.serial_worker.connect_serial(resolved, baud)
            self.data_timer.start()
            self._set_state("MONITORING")
            return

        if self._reconnect_elapsed_ms >= RECONNECT_TIMEOUT_MS:
            self._reconnect_timer.stop()
            self.console.append_tagged(
                "APP",
                "No s'ha pogut reconnectar automaticament — selecciona el port manualment i torna a provar",
            )
            self._set_state("IDLE")

    # ---------- cleanup ----------

    def closeEvent(self, event) -> None:
        self._reconnect_timer.stop()
        self.data_timer.stop()
        self.serial_worker.disconnect_serial()
        self.worker_thread.quit()
        self.worker_thread.wait()
        if self._last_compiled is not None:
            shutil.rmtree(self._last_compiled["sketch_dir"], ignore_errors=True)
        event.accept()
