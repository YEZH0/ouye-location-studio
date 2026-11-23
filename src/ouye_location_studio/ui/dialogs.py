"""Modal dialogs: first-run notice, per-location device confirmation,
restore confirmation, about, and license."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
)

from .. import brand
from .qr import make_qr_pixmap


def _resource_path(name: str) -> str | None:
    """Locate a bundled text file (LICENSE, notices) in source or frozen mode."""
    if getattr(sys, "frozen", False):
        root = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    else:
        root = Path(__file__).resolve().parents[2]
    candidate = root / name
    return str(candidate) if candidate.is_file() else None


class FirstRunDialog(QDialog):
    """First-use notice: disclaimer and acceptance."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("首次使用须知 · OUYE Location Studio")
        self.setMinimumWidth(520)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(brand.DISCLAIMER_TITLE + " · " + brand.DISCLAIMER_SHORT))
        for paragraph in brand.DISCLAIMER:
            label = QLabel(paragraph)
            label.setWordWrap(True)
            layout.addWidget(label)

        self.agree = QCheckBox("我已阅读并同意以上须知，仅用于合法技术研究")
        layout.addWidget(self.agree)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttons.button(QDialogButtonBox.Ok).setText("进入")
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)
        self.agree.toggled.connect(
            lambda checked: self.buttons.button(QDialogButtonBox.Ok).setEnabled(checked)
        )
        self.buttons.accepted.connect(self.accept)
        layout.addWidget(self.buttons)


class DeviceConfirmDialog(QDialog):
    """Shown before every location session: forces the user to confirm the
    three manual steps on the phone that the app cannot perform or verify."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("开始定位前，请确认")
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)

        intro = QLabel(
            "以下步骤只能由你本人在 iPhone 上完成，本工具无法代劳，也无法自动验证："
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        self.trust = QCheckBox("已在 iPhone 上点击「信任此电脑」并输入锁屏密码")
        self.map = QCheckBox("已在 iPhone 地图 / 目标 App 中确认目标位置")
        self.health = QCheckBox("已确认健康 App 及定位相关设置状态")
        for box in (self.trust, self.map, self.health):
            layout.addWidget(box)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Ok).setText("开始定位")
        self.buttons.button(QDialogButtonBox.Cancel).setText("取消")
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        for box in (self.trust, self.map, self.health):
            box.toggled.connect(self._update)
        layout.addWidget(self.buttons)

    def _update(self):
        enabled = self.trust.isChecked() and self.map.isChecked() and self.health.isChecked()
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(enabled)


class RestoreConfirmDialog(QDialog):
    """Shown after a session stops so the user verifies the phone has restored
    its real location. The app never asserts the location was restored."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("定位恢复确认")
        self.setMinimumWidth(480)
        layout = QVBoxLayout(self)

        title = QLabel("会话已结束，请确认 iPhone 位置已恢复真实定位")
        title.setWordWrap(True)
        layout.addWidget(title)

        tip = QLabel(
            "提示：可打开 iPhone 地图查看蓝点是否回到真实位置；"
            "若未恢复，请稍等或重新插拔设备 / 关闭再开启定位。"
        )
        tip.setWordWrap(True)
        layout.addWidget(tip)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttons.button(QDialogButtonBox.Ok).setText("已恢复")
        self.buttons.accepted.connect(self.accept)
        layout.addWidget(self.buttons)


class AboutDialog(QDialog):
    """Brand, author, tutorial channels, and QR code area."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于作者 · OUYE Location Studio")
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)

        title = QLabel(f"{brand.BRAND}")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        author = QLabel(f"作者：{brand.AUTHOR}（{brand.AUTHOR_NAME}）\nGitHub：{brand.HOMEPAGE}")
        author.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(author)

        channels = QLabel(brand.TUTORIAL_LONG)
        channels.setWordWrap(True)
        layout.addWidget(channels)

        qr_row = QHBoxLayout()
        pixmap = make_qr_pixmap(brand.QR_TARGET_URL)
        if pixmap is not None and not pixmap.isNull():
            qr_label = QLabel()
            qr_label.setPixmap(pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            qr_row.addWidget(qr_label)
        caption = QLabel("扫码访问 GitHub 仓库\n" + brand.QR_TARGET_URL)
        caption.setTextInteractionFlags(Qt.TextSelectableByMouse)
        qr_row.addWidget(caption, stretch=1)
        layout.addLayout(qr_row)

        footer = QLabel(brand.FOOTER_NOTE)
        footer.setObjectName("hintLabel")
        layout.addWidget(footer)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttons.rejected.connect(self.reject)
        self.buttons.button(QDialogButtonBox.Close).clicked.connect(self.accept)
        layout.addWidget(self.buttons)


class LicenseDialog(QDialog):
    """Open-source license page: GPL-3.0 text and third-party notices."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("开源许可 · OUYE Location Studio")
        self.resize(640, 560)
        layout = QVBoxLayout(self)

        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttons.button(QDialogButtonBox.Close).clicked.connect(self.accept)
        layout.addWidget(self.buttons)

        self._load()

    def _load(self):
        parts = []
        license_path = _resource_path("LICENSE")
        notices_path = _resource_path("THIRD_PARTY_NOTICES.md")
        parts.append("本项目基于 GPL-3.0-only 许可。\n")
        parts.append("仓库地址：" + brand.HOMEPAGE + "\n")
        if license_path:
            parts.append("=== GPL-3.0 许可证全文 ===\n")
            parts.append(Path(license_path).read_text(encoding="utf-8", errors="replace"))
        else:
            parts.append("（未找到捆绑的 LICENSE 文件，请访问仓库查看 GPL-3.0 全文。）")
        if notices_path:
            parts.append("\n\n=== 第三方声明（THIRD_PARTY_NOTICES） ===\n")
            parts.append(Path(notices_path).read_text(encoding="utf-8", errors="replace"))
        self.text.setPlainText("".join(parts))
