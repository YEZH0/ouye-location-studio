"""Resolve the bundled authentication executable for the shared UI."""

import sys
from pathlib import Path

from ouye_location_studio.app import main
from ouye_location_studio.ui import main_window


def bundled_auth_helper() -> str:
    return str(Path(sys.executable).resolve().with_name("ouye-auth-helper"))


if __name__ == "__main__":
    main_window.auth_helper_path = bundled_auth_helper
    raise SystemExit(main())
