"""Main application window."""

from __future__ import annotations

import sys
import time

from PySide6.QtCore import Qt, QSettings, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .. import brand
from ..paths import auth_helper_path
from ..platforms import create_platform
from ..presets import PRESETS, label as preset_label
from ..state import (
    EVENT_AUTHENTICATION_FAILED,
    EVENT_AUTHENTICATION_REQUIRED,
    EVENT_AUTHENTICATION_SUCCEEDED,
    EVENT_DEVICE_CONNECTED,
    EVENT_DEVICE_TRUST_REQUIRED,
    EVENT_ERROR,
    EVENT_FINISHED,
    EVENT_IDENTIFICATION_ACCEPTED,
    EVENT_LINK_READY,
    EVENT_LOCATION_LINK_ACKNOWLEDGED,
    EVENT_LOCATION_REQUESTED,
    EVENT_LOCATION_STOPPED,
    EVENT_RESTORE_REQUIRED,
    EVENT_RETRANSMIT,
    EngineEvent,
    SessionPhase,
)
from .dialogs import (
    AboutDialog,
    DeviceConfirmDialog,
    FirstRunDialog,
    LicenseDialog,
    RestoreConfirmDialog,
)
from .qr import make_qr_pixmap
from .style import THEME_NAMES, apply_theme
from .worker import EngineWorker

_PHASE_TEXT = {
    SessionPhase.IDLE: "就绪",
    SessionPhase.DETECTING: "正在检测设备…",
    SessionPhase.CONNECTING: "正在连接设备…",
    SessionPhase.HANDSHAKING: "正在进行 iAP2 握手…",
    SessionPhase.IDENTIFYING: "正在识别配件身份…",
    SessionPhase.AUTHENTICATING: "正在配件认证…",
    SessionPhase.LOCATING: "正在发送定位信息…",
    SessionPhase.STOPPING: "正在停止…",
    SessionPhase.DONE: "已结束",
    SessionPhase.ERROR: "出错",
}


class _DetectWorker(QThread):
    result = Signal(list)

    def __init__(self, adapter, parent=None):
        super().__init__(parent)
        self._adapter = adapter

    def run(self):  # noqa: D102
        import asyncio

        try:
            self.result.emit(asyncio.run(self._adapter.list_devices()))
        except Exception:  # noqa: BLE001
            self.result.emit([])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OUYE Location Studio · 欧耶哥爱数码")
        self.resize(760, 720)
        self.setMinimumSize(640, 600)

        self.settings = QSettings("OUYE", "LocationStudio")
        self._theme = self.settings.value("theme", "light", str)
        if self._theme not in THEME_NAMES:
            self._theme = "light"
        self.adapter = create_platform()
        self._worker: EngineWorker | None = None
        self._detect: _DetectWorker | None = None
        self._remaining = 0.0
        self._needs_restore = False

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        self._build_ui()
        self._load_credentials()
        self._check_driver()
        self._log("就绪。请连接 iPhone 并点击「检测设备」。")

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 14, 16, 12)
        root.setSpacing(10)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("OUYE Location Studio")
        title.setObjectName("titleLabel")
        brand_label = QLabel(f"{brand.BRAND} · 作者 {brand.AUTHOR} · 开源 GPL-3.0")
        brand_label.setObjectName("brandLabel")
        title_box.addWidget(title)
        title_box.addWidget(brand_label)
        header.addLayout(title_box, stretch=1)
        about_btn = QPushButton("关于作者")
        about_btn.setObjectName("linkButton")
        about_btn.clicked.connect(lambda: AboutDialog(self).exec())
        license_btn = QPushButton("开源许可")
        license_btn.setObjectName("linkButton")
        license_btn.clicked.connect(lambda: LicenseDialog(self).exec())
        self.theme_btn = QPushButton(self._theme_label())
        self.theme_btn.setObjectName("linkButton")
        self.theme_btn.clicked.connect(self._toggle_theme)
        header.addWidget(about_btn)
        header.addWidget(license_btn)
        header.addWidget(self.theme_btn)
        root.addLayout(header)

        # Driver / device banner
        self.banner = QLabel()
        self.banner.setWordWrap(True)
        self.banner.setVisible(False)
        root.addWidget(self.banner)

        # Device group
        device_group = QGroupBox("设备")
        device_layout = QVBoxLayout(device_group)
        device_row = QHBoxLayout()
        self.detect_btn = QPushButton("检测设备")
        self.detect_btn.clicked.connect(self._detect_devices)
        device_row.addWidget(self.detect_btn)
        self.device_status = QLabel("尚未检测")
        device_row.addWidget(self.device_status, stretch=1)
        device_layout.addLayout(device_row)
        root.addWidget(device_group)

        # Location group
        loc_group = QGroupBox("定位设置")
        loc_layout = QVBoxLayout(loc_group)

        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("定位预设："))
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("自定义坐标", None)
        for preset in PRESETS:
            self.preset_combo.addItem(preset_label(preset), preset["id"])
        self.preset_combo.currentIndexChanged.connect(self._on_preset)
        preset_row.addWidget(self.preset_combo, stretch=1)
        loc_layout.addLayout(preset_row)

        coord_row = QHBoxLayout()
        self.lat_spin = self._make_coord_spin(-90.0, 90.0, "纬度")
        self.lon_spin = self._make_coord_spin(-180.0, 180.0, "经度")
        self.lat_spin.setValue(31.2304)  # 上海
        self.lon_spin.setValue(121.4737)
        coord_row.addWidget(QLabel("纬度："))
        coord_row.addWidget(self.lat_spin)
        coord_row.addWidget(QLabel("经度："))
        coord_row.addWidget(self.lon_spin)
        coord_row.addStretch(1)
        loc_layout.addLayout(coord_row)

        param_row = QHBoxLayout()
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 3600)
        self.duration_spin.setValue(60)
        self.duration_spin.setSuffix(" 秒")
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(1)
        self.interval_spin.setSuffix(" 秒")
        param_row.addWidget(QLabel("会话时长："))
        param_row.addWidget(self.duration_spin)
        param_row.addWidget(QLabel("发送间隔："))
        param_row.addWidget(self.interval_spin)
        param_row.addStretch(1)
        loc_layout.addLayout(param_row)

        root.addWidget(loc_group)

        # Credentials group
        cred_group = QGroupBox("认证材料（可选，用于配件认证）")
        cred_layout = QVBoxLayout(cred_group)
        self.cert_edit = self._make_cred_row(cred_layout, "证书 (certificate.p7b)：")
        self.key_edit = self._make_cred_row(cred_layout, "私钥 (identity.pk8)：")
        cred_note = QLabel(
            "认证材料需由使用者自行提供；本工具不内置、不分发任何 MFi 证书或私钥。"
        )
        cred_note.setObjectName("hintLabel")
        cred_note.setWordWrap(True)
        cred_layout.addWidget(cred_note)
        root.addWidget(cred_group)

        # Action row
        action_row = QHBoxLayout()
        self.start_btn = QPushButton("开始定位")
        self.start_btn.clicked.connect(self._start)
        self.stop_btn = QPushButton("停止定位")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop)
        action_row.addWidget(self.start_btn)
        action_row.addWidget(self.stop_btn)
        action_row.addStretch(1)
        root.addLayout(action_row)

        # Countdown
        self.countdown = QLabel("剩余时间：--:--")
        self.countdown.setObjectName("statusLabel")
        root.addWidget(self.countdown)
        self.progress = QProgressBar()
        self.progress.setRange(0, 1000)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        root.addWidget(self.progress)

        # Status
        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("statusLabel")
        root.addWidget(self.status_label)

        # Log
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(2000)
        root.addWidget(self.log, stretch=1)

        # Footer
        footer = QHBoxLayout()
        qr_pixmap = make_qr_pixmap(brand.QR_TARGET_URL)
        if qr_pixmap is not None and not qr_pixmap.isNull():
            qr_label = QLabel()
            qr_label.setPixmap(qr_pixmap.scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            qr_label.setToolTip("扫码访问 GitHub 仓库")
            footer.addWidget(qr_label)
        footer_text = QVBoxLayout()
        hint = QLabel(brand.TUTORIAL_HINT)
        hint.setObjectName("hintLabel")
        footer_text.addWidget(hint)
        note = QLabel(brand.FOOTER_NOTE)
        note.setObjectName("hintLabel")
        footer_text.addWidget(note)
        footer.addLayout(footer_text, stretch=1)
        root.addLayout(footer)

    def _make_coord_spin(self, minimum: float, maximum: float, suffix: str) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(minimum, maximum)
        spin.setDecimals(6)
        spin.setSingleStep(0.0001)
        spin.setSuffix(f"° {suffix}")
        return spin

    def _make_cred_row(self, layout, label_text: str) -> QLineEdit:
        row = QHBoxLayout()
        row.addWidget(QLabel(label_text))
        edit = QLineEdit()
        edit.setPlaceholderText("（未设置）")
        row.addWidget(edit, stretch=1)
        browse = QPushButton("选择…")
        browse.setObjectName("secondaryButton")
        browse.clicked.connect(lambda _=False, e=edit: self._browse_file(e))
        row.addWidget(browse)
        layout.addLayout(row)
        return edit

    # ------------------------------------------------------------ helpers

    def _log(self, text: str):
        stamp = time.strftime("%H:%M:%S")
        self.log.appendPlainText(f"[{stamp}] {text}")

    def _set_status(self, text: str, style: str | None = None):
        self.status_label.setText(text)
        if style == "error":
            self.status_label.setStyleSheet("color: #b91c1c;")
        elif style == "ok":
            self.status_label.setStyleSheet("color: #166534;")
        else:
            self.status_label.setStyleSheet("")

    def _show_banner(self, text: str, kind: str):
        self.banner.setText(text)
        self.banner.setObjectName(
            {"warn": "warnLabel", "error": "errorLabel", "ok": "okLabel"}.get(kind, "warnLabel")
        )
        self.banner.setVisible(True)
        # Re-apply stylesheet after changing objectName
        self.banner.style().unpolish(self.banner)
        self.banner.style().polish(self.banner)

    def _hide_banner(self):
        self.banner.setVisible(False)

    def _theme_label(self) -> str:
        return "主题：" + THEME_NAMES.get(self._theme, "浅色")

    def _toggle_theme(self):
        self._theme = "dark" if self._theme == "light" else "light"
        self.settings.setValue("theme", self._theme)
        app = QApplication.instance()
        if app is not None:
            apply_theme(app, self._theme)
        self.theme_btn.setText(self._theme_label())
        self._log(f"已切换为{THEME_NAMES.get(self._theme, self._theme)}主题。")

    def _check_driver(self):
        if sys.platform != "win32":
            return
        try:
            from ..platforms.windows import APPLE_DRIVER_URL, has_apple_usb_driver
        except ImportError:
            return
        result = has_apple_usb_driver()
        if result is True:
            self._log("已检测到 Apple USB 驱动。")
        elif result is False:
            self._show_banner(
                "未检测到 Apple Mobile Device USB 驱动。需先安装官方驱动（随 iTunes / "
                "Microsoft Store「Apple 设备」提供）才能识别 iPhone。",
                "warn",
            )
            # The banner is informational; installation only starts after explicit
            # user confirmation in _prompt_install_driver.
            self._prompt_install_driver()
        else:
            self._show_banner("无法读取注册表以判断 Apple USB 驱动状态。", "warn")

    def _prompt_install_driver(self):
        if sys.platform != "win32":
            return
        reply = QMessageBox.question(
            self,
            "缺少 Apple USB 驱动",
            "未检测到 Apple Mobile Device USB 驱动。是否打开 Apple 官方下载页面"
            "（安装 iTunes 或「Apple 设备」）？\n\n不会静默安装任何程序。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if reply == QMessageBox.Yes:
            import webbrowser

            from ..platforms.windows import APPLE_DRIVER_URL

            webbrowser.open(APPLE_DRIVER_URL)
            self._log("已打开 Apple 官方下载页面，请按提示安装驱动后重新检测设备。")

    # ------------------------------------------------------------ device

    def _detect_devices(self):
        self.detect_btn.setEnabled(False)
        self.device_status.setText("正在检测…")
        self._detect = _DetectWorker(self.adapter)
        self._detect.result.connect(self._on_devices)
        self._detect.start()

    def _on_devices(self, devices: list):
        self.detect_btn.setEnabled(True)
        if devices:
            self.device_status.setText(f"检测到 {len(devices)} 台设备")
            self._log(f"检测到 {len(devices)} 台 USB 设备。")
        else:
            self.device_status.setText("未检测到设备")
            self._show_banner(
                "未检测到 iPhone。请检查：USB 数据线已连接、已安装 Apple 驱动、"
                "iPhone 已解锁并点击「信任此电脑」。",
                "warn",
            )

    # ------------------------------------------------------------- preset

    def _on_preset(self, index: int):
        preset_id = self.preset_combo.itemData(index)
        if not preset_id:
            return
        from ..presets import find

        preset = find(preset_id)
        if preset:
            self.lat_spin.setValue(preset["latitude"])
            self.lon_spin.setValue(preset["longitude"])

    # ---------------------------------------------------------- credentials

    def _browse_file(self, edit: QLineEdit):
        path, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if path:
            edit.setText(path)

    def _load_credentials(self):
        self.cert_edit.setText(self.settings.value("cred/cert", "", str))
        self.key_edit.setText(self.settings.value("cred/key", "", str))

    def _save_credentials(self):
        self.settings.setValue("cred/cert", self.cert_edit.text())
        self.settings.setValue("cred/key", self.key_edit.text())

    # ------------------------------------------------------------ session

    def _start(self):
        if self._worker is not None and self._worker.isRunning():
            return
        latitude = self.lat_spin.value()
        longitude = self.lon_spin.value()
        duration = float(self.duration_spin.value())
        interval = float(self.interval_spin.value())

        confirm = DeviceConfirmDialog(self)
        if confirm.exec() != DeviceConfirmDialog.Accepted:
            self._log("已取消本次定位。")
            return

        self._save_credentials()
        self._hide_banner()
        self._needs_restore = False

        cert = self.cert_edit.text().strip() or None
        key = self.key_edit.text().strip() or None

        self._worker = EngineWorker(
            self.adapter,
            auth_helper_path=auth_helper_path(),
            cert_file=cert,
            key_file=key,
        )
        self._worker.configure(
            latitude=latitude,
            longitude=longitude,
            duration=duration,
            interval=interval,
        )
        self._worker.bridge.event.connect(self._on_event)
        self._worker.bridge.finished.connect(self._on_finished)

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.detect_btn.setEnabled(False)
        self._remaining = duration
        self.progress.setRange(0, int(duration * 10))
        self.progress.setValue(int(duration * 10))
        self._update_countdown()
        self._timer.start()
        self._log(f"开始定位：纬度 {latitude:.6f}，经度 {longitude:.6f}，时长 {duration:.0f} 秒。")
        self._worker.start()

    def _stop(self):
        if self._worker is not None and self._worker.isRunning():
            self._log("正在请求停止…")
            self._worker.request_stop()

    def _tick(self):
        self._remaining -= 1.0
        if self._remaining <= 0:
            self._remaining = 0.0
            self._timer.stop()
        self._update_countdown()
        self.progress.setValue(max(0, int(self._remaining * 10)))

    def _update_countdown(self):
        total = int(self._remaining)
        self.countdown.setText(f"剩余时间：{total // 60:02d}:{total % 60:02d}")

    def _on_finished(self):
        self._timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.detect_btn.setEnabled(True)
        self.progress.setValue(0)
        self._worker = None
        if self._needs_restore:
            RestoreConfirmDialog(self).exec()
            self._needs_restore = False

    def _on_event(self, event: EngineEvent):
        name = event.name
        if name == EVENT_DEVICE_CONNECTED:
            self._log(event.message or "设备已连接。")
        elif name == EVENT_DEVICE_TRUST_REQUIRED:
            self._show_banner(
                "请在 iPhone 上点击「信任此电脑」并输入锁屏密码，然后重新检测 / 开始定位。",
                "warn",
            )
            self._log(event.message or "需要用户信任此电脑。")
        elif name == EVENT_LINK_READY:
            self._log(event.message)
        elif name == EVENT_IDENTIFICATION_ACCEPTED:
            self._log(event.message)
        elif name == EVENT_AUTHENTICATION_REQUIRED:
            self._log(event.message or "正在进行配件认证…")
        elif name == EVENT_AUTHENTICATION_SUCCEEDED:
            self._log(event.message)
            self._set_status("配件认证成功", "ok")
        elif name == EVENT_AUTHENTICATION_FAILED:
            self._show_banner("配件认证失败：设备拒绝了该配件身份。", "error")
            self._log(event.message)
        elif name == EVENT_LOCATION_REQUESTED:
            self._log(event.message)
            self._set_status("设备已请求定位，正在发送…", "ok")
        elif name == EVENT_LOCATION_LINK_ACKNOWLEDGED:
            self._log(event.message)
        elif name == EVENT_LOCATION_STOPPED:
            self._log(event.message)
        elif name == EVENT_RESTORE_REQUIRED:
            self._needs_restore = True
            self._log(event.message)
        elif name == EVENT_RETRANSMIT:
            self._log(event.message)
        elif name == EVENT_FINISHED:
            self._log(event.message or "会话已结束。")
        elif name == EVENT_ERROR:
            self._show_banner(f"出错：{event.message}", "error")
            self._set_status("出错", "error")
            self._log(f"错误：{event.message}")
        # EVENT_MESSAGE and others are logged only when they carry a message.

        if event.phase is not None:
            self._set_status(_PHASE_TEXT.get(event.phase, event.phase.value))

    # ------------------------------------------------------------- close

    def closeEvent(self, event):  # noqa: N802
        if self._worker is not None and self._worker.isRunning():
            self._worker.request_stop()
            self._worker.wait(3000)
        if self._detect is not None and self._detect.isRunning():
            self._detect.wait(2000)
        super().closeEvent(event)
