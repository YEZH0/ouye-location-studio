"""Unit tests for coordinate presets and branding."""

import math

from ouye_location_studio import brand
from ouye_location_studio.presets import PRESETS, find, label


def test_all_presets_valid_coordinates():
    for preset in PRESETS:
        assert -90 <= preset["latitude"] <= 90
        assert -180 <= preset["longitude"] <= 180
        assert math.isfinite(preset["latitude"])
        assert math.isfinite(preset["longitude"])


def test_preset_ids_unique():
    ids = [p["id"] for p in PRESETS]
    assert len(ids) == len(set(ids))


def test_find_and_label():
    assert find("nyc")["name"] == "Times Square"
    assert find("does-not-exist") is None
    assert "时代广场" in label(find("nyc"))


def test_brand_has_no_unverifiable_urls():
    # Only the repository URL is present; channels carry search hints, not URLs.
    for channel in brand.CHANNELS:
        assert "url" not in channel
        assert channel["handle"] == brand.TUTORIAL_KEYWORD
    assert brand.QR_TARGET_URL.startswith("https://github.com/YEZH0/")
    assert brand.AUTHOR == "YEZH0"
