"""Allow `python -m ouye_location_studio` to launch the GUI."""

from .app import main

if __name__ == "__main__":
    raise SystemExit(main())
