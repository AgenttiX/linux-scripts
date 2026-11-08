"""Tests for ./pgp/pgp.py."""

import base64
import shutil
import subprocess
import unittest

import pytest

from pgp import pgp


def armor(data: bytes, checksum: bytes | None = None) -> bytes:
    """Create an ASCII-armored public key block of arbitrary data."""
    encoded = base64.b64encode(data).decode()
    lines = [encoded[i:i + 64] for i in range(0, len(encoded), 64)]
    if checksum is None:
        checksum = pgp.crc24(data).to_bytes(3)
    return "\n".join([
        pgp.ARMOR_BEGIN,
        "Comment: test",
        "",
        *lines,
        "=" + base64.b64encode(checksum).decode(),
        pgp.ARMOR_END,
        "",
    ]).encode()


class PGPTestCase(unittest.TestCase):
    """Tests for the OpenPGP key utilities."""

    def test_crc24(self) -> None:
        """Check that the CRC-24 of empty data is the initial value."""
        assert pgp.crc24(b"") == pgp.CRC24_INIT

    def test_dearmor(self) -> None:
        """Check that armored data is detected and decoded back to the original."""
        data = bytes(range(256)) * 3
        armored = armor(data)
        assert pgp.is_armored(armored)
        assert pgp.dearmor(armored) == data

    @unittest.skipIf(shutil.which("gpg") is None, "gpg is not installed")
    def test_dearmor_matches_gpg(self) -> None:
        """Check that the decoded key is identical to the output of "gpg --dearmor"."""
        armored = armor(bytes(range(256)) * 3)
        reference = subprocess.run(["gpg", "--dearmor"], input=armored, capture_output=True, check=True).stdout
        assert pgp.dearmor(armored) == reference

    def test_dearmor_multiple_blocks(self) -> None:
        """Check that consecutive armor blocks are concatenated."""
        assert pgp.dearmor(armor(b"first") + armor(b"second")) == b"firstsecond"

    def test_dearmor_invalid(self) -> None:
        """Check that a bad checksum, missing armor and a missing end line are rejected."""
        with pytest.raises(ValueError, match="checksum does not match"):
            pgp.dearmor(armor(b"test", checksum=b"abc"))
        with pytest.raises(ValueError, match="No ASCII-armored public key block"):
            pgp.dearmor(b"not a key")
        with pytest.raises(ValueError, match="no end line"):
            pgp.dearmor(f"{pgp.ARMOR_BEGIN}\n\nAAAA\n".encode())

    def test_is_armored(self) -> None:
        """Check that binary keys are not detected as armored."""
        assert not pgp.is_armored(b"\x99\x01binary key")
