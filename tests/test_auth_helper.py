"""Offline tests for the local MFi-v3 authentication helper.

Generates a short-lived, self-signed P-256 test identity; no real device or
credential is used. All files are temporary.
"""

import base64
import os
from datetime import UTC, datetime, timedelta

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives.serialization import pkcs7
from cryptography.x509.oid import NameOID

from ouye_location_studio import auth_helper
from ouye_location_studio.auth_helper import CERT_ENV, KEY_ENV, LocalMfiV3, validate_identity


def make_certificate(key, ca=False):
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "UNTRUSTED TEST ONLY")])
    now = datetime.now(UTC)
    return (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(minutes=5))
        .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )


def encode_key(key):
    return key.private_bytes(
        serialization.Encoding.DER, serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )


def make_identity():
    key = ec.generate_private_key(ec.SECP256R1())
    certificate = pkcs7.serialize_certificates([make_certificate(key)], serialization.Encoding.DER)
    return key, certificate, encode_key(key)


def _write(path, data):
    with open(path, "wb") as stream:
        stream.write(data)


def test_validate_identity_accepts_matching_pair(tmp_path, monkeypatch):
    key, certificate, encoded_key = make_identity()
    assert validate_identity(certificate, encoded_key) is not None


def test_validate_identity_rejects_mismatched_key(tmp_path, monkeypatch):
    _, certificate, _ = make_identity()
    other = ec.generate_private_key(ec.SECP256R1())
    with pytest.raises(auth_helper.ProviderError):
        validate_identity(certificate, encode_key(other))


def test_full_certificate_and_sign_roundtrip(tmp_path, monkeypatch):
    key, certificate, encoded_key = make_identity()
    cert_path = tmp_path / "certificate.p7b"
    key_path = tmp_path / "identity.pk8"
    _write(cert_path, certificate)
    _write(key_path, encoded_key)
    monkeypatch.setenv(CERT_ENV, str(cert_path))
    monkeypatch.setenv(KEY_ENV, str(key_path))

    provider = LocalMfiV3()
    response = provider.handle({"op": "certificate"})
    assert response["type"] == "mfi"
    assert base64.b64decode(response["certificate"]) == certificate

    challenge = bytes(range(32))
    signature = provider.handle({"op": "sign", "challenge": base64.b64encode(challenge).decode()})
    raw = base64.b64decode(signature["signature"])
    assert len(raw) == 64
    r, s = int.from_bytes(raw[:32], "big"), int.from_bytes(raw[32:], "big")
    der = utils.encode_dss_signature(r, s)
    key.public_key().verify(der, challenge, ec.ECDSA(utils.Prehashed(hashes.SHA256())))


def test_sign_requires_certificate_first(tmp_path, monkeypatch):
    key, certificate, encoded_key = make_identity()
    monkeypatch.setenv(CERT_ENV, str(tmp_path / "c.p7b"))
    monkeypatch.setenv(KEY_ENV, str(tmp_path / "k.pk8"))
    _write(tmp_path / "c.p7b", certificate)
    _write(tmp_path / "k.pk8", encoded_key)
    provider = LocalMfiV3()
    with pytest.raises(auth_helper.ProviderError):
        provider.handle({"op": "sign", "challenge": base64.b64encode(b"\x00" * 32).decode()})
