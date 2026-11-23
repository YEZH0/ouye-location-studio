"""Tests with ephemeral self-signed credentials and isolated settings."""

import stat
import sys

import pytest

from ouye_location_studio.auth_helper import CERT_ENV, KEY_ENV, ProviderError
from ouye_location_studio.platforms.macos_identity import import_identity, local_pair
from test_auth_helper import make_identity

pytestmark = pytest.mark.skipif(sys.platform != "darwin", reason="macOS credential store")


@pytest.fixture
def inputs(tmp_path, monkeypatch):
    _, certificate, key = make_identity()
    paths = tmp_path / "test-certificate", tmp_path / "test-key"
    for path, data, variable in zip(paths, (certificate, key), (CERT_ENV, KEY_ENV), strict=True):
        path.write_bytes(data)
        monkeypatch.setenv(variable, str(path))
    return paths


def test_import_and_rediscover_private_copy(tmp_path, inputs):
    root = tmp_path / "support"
    name = import_identity(root)
    pair = local_pair(root, name)
    for dest, source in zip(pair, inputs, strict=True):
        assert dest.read_bytes() == source.read_bytes()
        assert stat.S_IMODE(dest.stat().st_mode) == 0o600
    for directory in (root, root / name):
        assert stat.S_IMODE(directory.stat().st_mode) == 0o700


def test_invalid_pair_preserves_existing_import(tmp_path, inputs):
    root = tmp_path / "support"
    previous = import_identity(root)
    _, _, different_key = make_identity()
    inputs[1].write_bytes(different_key)
    with pytest.raises(ProviderError):
        import_identity(root)
    assert [item.name for item in root.iterdir()] == [previous]
    assert all(path.is_file() for path in local_pair(root, previous))


def test_insecure_permissions_or_symlink_rejected(tmp_path, inputs):
    root = tmp_path / "support"
    name = import_identity(root)
    _, key = local_pair(root, name)
    key.chmod(0o644)
    with pytest.raises(ProviderError, match="权限"):
        local_pair(root, name)
    key.unlink()
    key.symlink_to(inputs[1])
    with pytest.raises(ProviderError, match="文件类型"):
        local_pair(root, name)


def test_rejects_directory_traversal(tmp_path):
    with pytest.raises(ProviderError, match="标识"):
        local_pair(tmp_path, "identity-abc/../identity-other")
