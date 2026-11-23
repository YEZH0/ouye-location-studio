"""Application stylesheet (QSS): light and dark themes."""

from __future__ import annotations

LIGHT_QSS = """
* {
    font-family: "Microsoft YaHei UI", "PingFang SC", "Segoe UI", sans-serif;
    font-size: 13px;
}
QMainWindow, QDialog {
    background-color: #f5f7f6;
}
QWidget {
    color: #1f2933;
}
QLabel#titleLabel {
    font-size: 20px;
    font-weight: 700;
    color: #14532d;
}
QLabel#brandLabel {
    font-size: 12px;
    color: #6b7280;
}
QLabel#hintLabel {
    color: #6b7280;
    font-size: 11px;
}
QLabel#statusLabel {
    font-weight: 600;
}
QLabel#warnLabel {
    color: #b45309;
    background-color: #fef3c7;
    border: 1px solid #fcd34d;
    border-radius: 6px;
    padding: 8px 10px;
}
QLabel#errorLabel {
    color: #b91c1c;
    background-color: #fee2e2;
    border: 1px solid #fca5a5;
    border-radius: 6px;
    padding: 8px 10px;
}
QLabel#okLabel {
    color: #166534;
    background-color: #dcfce7;
    border: 1px solid #86efac;
    border-radius: 6px;
    padding: 8px 10px;
}
QGroupBox {
    border: 1px solid #d1d5db;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 6px;
    background-color: #ffffff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #14532d;
    font-weight: 600;
}
QPushButton {
    background-color: #16a34a;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #15803d;
}
QPushButton:disabled {
    background-color: #9ca3af;
    color: #f3f4f6;
}
QPushButton#stopButton {
    background-color: #dc2626;
}
QPushButton#stopButton:hover {
    background-color: #b91c1c;
}
QPushButton#stopButton:disabled {
    background-color: #9ca3af;
}
QPushButton#secondaryButton {
    background-color: #e5e7eb;
    color: #1f2933;
}
QPushButton#secondaryButton:hover {
    background-color: #d1d5db;
}
QPushButton#linkButton {
    background-color: transparent;
    color: #2563eb;
    text-decoration: underline;
    padding: 2px;
}
QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 5px 8px;
}
QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #16a34a;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1f2933;
    selection-background-color: #16a34a;
    selection-color: #ffffff;
}
QPlainTextEdit {
    background-color: #0f172a;
    color: #d1fae5;
    border: 1px solid #1e293b;
    border-radius: 6px;
    font-family: "Consolas", "Microsoft YaHei UI", monospace;
    font-size: 12px;
}
QProgressBar {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    text-align: center;
    background-color: #ffffff;
}
QProgressBar::chunk {
    background-color: #16a34a;
    border-radius: 5px;
}
"""

DARK_QSS = """
* {
    font-family: "Microsoft YaHei UI", "PingFang SC", "Segoe UI", sans-serif;
    font-size: 13px;
}
QMainWindow, QDialog {
    background-color: #171a21;
}
QWidget {
    color: #e2e8f0;
}
QLabel#titleLabel {
    font-size: 20px;
    font-weight: 700;
    color: #4ade80;
}
QLabel#brandLabel {
    font-size: 12px;
    color: #94a3b8;
}
QLabel#hintLabel {
    color: #94a3b8;
    font-size: 11px;
}
QLabel#statusLabel {
    font-weight: 600;
}
QLabel#warnLabel {
    color: #fcd34d;
    background-color: #3a2f08;
    border: 1px solid #92600a;
    border-radius: 6px;
    padding: 8px 10px;
}
QLabel#errorLabel {
    color: #fca5a5;
    background-color: #3a1414;
    border: 1px solid #991b1b;
    border-radius: 6px;
    padding: 8px 10px;
}
QLabel#okLabel {
    color: #86efac;
    background-color: #0f2b18;
    border: 1px solid #166534;
    border-radius: 6px;
    padding: 8px 10px;
}
QGroupBox {
    border: 1px solid #374151;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 6px;
    background-color: #1f242c;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #4ade80;
    font-weight: 600;
}
QPushButton {
    background-color: #16a34a;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #15803d;
}
QPushButton:disabled {
    background-color: #4b5563;
    color: #9ca3af;
}
QPushButton#stopButton {
    background-color: #dc2626;
}
QPushButton#stopButton:hover {
    background-color: #b91c1c;
}
QPushButton#stopButton:disabled {
    background-color: #4b5563;
}
QPushButton#secondaryButton {
    background-color: #374151;
    color: #e2e8f0;
}
QPushButton#secondaryButton:hover {
    background-color: #4b5563;
}
QPushButton#linkButton {
    background-color: transparent;
    color: #60a5fa;
    text-decoration: underline;
    padding: 2px;
}
QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #1f242c;
    color: #e2e8f0;
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 5px 8px;
}
QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #16a34a;
}
QComboBox QAbstractItemView {
    background-color: #1f242c;
    color: #e2e8f0;
    selection-background-color: #16a34a;
    selection-color: #ffffff;
}
QPlainTextEdit {
    background-color: #0f172a;
    color: #d1fae5;
    border: 1px solid #1e293b;
    border-radius: 6px;
    font-family: "Consolas", "Microsoft YaHei UI", monospace;
    font-size: 12px;
}
QProgressBar {
    border: 1px solid #374151;
    border-radius: 6px;
    text-align: center;
    background-color: #1f242c;
}
QProgressBar::chunk {
    background-color: #16a34a;
    border-radius: 5px;
}
"""

# Backwards-compatible alias: the light theme remains the default export.
QSS = LIGHT_QSS

STYLESHEETS: dict[str, str] = {"light": LIGHT_QSS, "dark": DARK_QSS}

THEME_NAMES = {"light": "浅色", "dark": "深色"}


def apply_theme(app, name: str) -> None:
    """Apply a named theme (``light`` / ``dark``) to the given QApplication."""
    app.setStyleSheet(STYLESHEETS.get(name, LIGHT_QSS))
