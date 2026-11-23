"""Launch the shared UI with macOS-specific authentication settings."""

import json
import os
from pathlib import Path
import subprocess
import sys

from PySide6.QtWidgets import QDialog, QMessageBox, QPushButton

from ouye_location_studio.app import main
from ouye_location_studio.auth_helper import CERT_ENV, KEY_ENV, ProviderError
from ouye_location_studio.platforms.macos_identity import APP_SUPPORT, local_pair
from ouye_location_studio.ui import main_window
from ouye_location_studio.ui.dialogs import DeviceConfirmDialog, FirstRunDialog

IDENTITY_SETTING = "macos/local_identity"


def bundled_auth_helper() -> str:
    return str(Path(sys.executable).resolve().with_name("ouye-auth-helper"))


class MacMainWindow(main_window.MainWindow):
    def __init__(self):
        super().__init__()
        layout = self.cert_edit.parentWidget().layout()
        for label, action in (
            ("导入并保存本机认证配置", self._import_local_identity),
            ("重新检测本机配置", self._recheck_local_identity),
            ("清除本机配置引用", self._clear_local_identity),
        ):
            button = QPushButton(label)
            button.clicked.connect(action)
            layout.addWidget(button)

    def _load_credentials(self):
        super()._load_credentials()
        if self.settings.value(IDENTITY_SETTING, "", str):
            self._recheck_local_identity(validate=False)

    def _run_identity_helper(self, operation: str, certificate: str, key: str) -> dict:
        try:
            result = subprocess.run(
                [bundled_auth_helper(), operation],
                env={**os.environ, CERT_ENV: certificate, KEY_ENV: key},
                capture_output=True, text=True, timeout=8,
            )
            response = json.loads(result.stdout)
        except (OSError, ValueError, subprocess.TimeoutExpired):
            raise ProviderError("无法运行本机认证助手") from None
        if result.returncode:
            raise ProviderError(response.get("error", "本机认证助手执行失败"))
        return response

    def _import_local_identity(self):
        certificate, key = self.cert_edit.text().strip(), self.key_edit.text().strip()
        if not certificate or not key:
            self._show_banner("请先选择你有权使用的证书和配套私钥", "warn")
            return
        answer = QMessageBox.question(
            self, "导入本机认证材料",
            "请确认你有权使用这份 MFi 配件身份。APP 将把文件复制到仅当前用户"
            "可访问的本机 Application Support 目录，并在下次启动时自动加载。",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            response = self._run_identity_helper("--import-local", certificate, key)
            name = response["identity"]
            local_pair(APP_SUPPORT, name)
        except (ProviderError, OSError, KeyError) as error:
            self._identity_error(error)
            return
        self.settings.setValue(IDENTITY_SETTING, name)
        self.settings.sync()
        self._recheck_local_identity(validate=False)

    def _recheck_local_identity(self, *, validate=True):
        name = self.settings.value(IDENTITY_SETTING, "", str)
        if not name:
            self._show_banner("尚未保存本机认证配置，可手动选择材料", "warn")
            return
        try:
            certificate, key = map(str, local_pair(APP_SUPPORT, name))
            if validate:
                self._run_identity_helper("--validate-local", certificate, key)
        except (ProviderError, OSError) as error:
            self.cert_edit.clear()
            self.key_edit.clear()
            self._identity_error(error)
            return
        self.cert_edit.setText(certificate)
        self.key_edit.setText(key)
        self._show_banner("已加载本机认证配置。设备是否接受将在连接时确认。", "ok")

    def _identity_error(self, error):
        message = str(error) if isinstance(error, ProviderError) else "本机认证配置缺失或无法读取"
        self._show_banner(message, "error")

    def _clear_local_identity(self):
        self.settings.remove(IDENTITY_SETTING)
        self.settings.remove("cred/cert")
        self.settings.remove("cred/key")
        self.settings.sync()
        self.cert_edit.clear()
        self.key_edit.clear()
        self._show_banner("已清除自动加载配置。认证文件仍保留在本机。", "ok")

    def _save_credentials(self):
        # The worker sets selected paths after confirmation. Do not reuse a
        # previous run's environment when the fields have since been cleared.
        for variable in (CERT_ENV, KEY_ENV):
            os.environ.pop(variable, None)
        super()._save_credentials()


def launch() -> int:
    # The shared UI uses the old unscoped name when checking both dialogs.
    FirstRunDialog.Accepted = QDialog.DialogCode.Accepted
    DeviceConfirmDialog.Accepted = QDialog.DialogCode.Accepted
    main_window.auth_helper_path = bundled_auth_helper
    main_window.MainWindow = MacMainWindow
    return main()


if __name__ == "__main__":
    raise SystemExit(launch())
