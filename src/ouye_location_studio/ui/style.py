"""Application stylesheet (QSS)."""

QSS = """
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
