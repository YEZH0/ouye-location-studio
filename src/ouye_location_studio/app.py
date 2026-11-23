"""Application entry point."""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    from PySide6.QtCore import QSettings
    from PySide6.QtWidgets import QApplication

    app = QApplication(list(argv) if argv is not None else sys.argv)
    app.setApplicationName("OUYE Location Studio")
    app.setOrganizationName("OUYE")

    from .ui.style import apply_theme

    settings = QSettings("OUYE", "LocationStudio")
    apply_theme(app, settings.value("theme", "light", str))

    if not settings.value("first_run_done", False, bool):
        from .ui.dialogs import FirstRunDialog

        dialog = FirstRunDialog()
        if dialog.exec() != dialog.Accepted:
            return 0
        settings.setValue("first_run_done", True)

    from .ui.main_window import MainWindow

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
