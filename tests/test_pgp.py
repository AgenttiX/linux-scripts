"""Tests for ./pgp/pgp.py."""

import base64
import shutil
import subprocess
import unittest

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
    def test_crc24(self):
        self.assertEqual(pgp.crc24(b""), pgp.CRC24_INIT)

    def test_dearmor(self):
        data = bytes(range(256)) * 3
        armored = armor(data)
        self.assertTrue(pgp.is_armored(armored))
        self.assertEqual(pgp.dearmor(armored), data)

    @unittest.skipIf(shutil.which("gpg") is None, "gpg is not installed")
    def test_dearmor_matches_gpg(self):
        armored = armor(bytes(range(256)) * 3)
        reference = subprocess.run(["gpg", "--dearmor"], input=armored, capture_output=True, check=True).stdout
        self.assertEqual(pgp.dearmor(armored), reference)

    def test_dearmor_multiple_blocks(self):
        self.assertEqual(pgp.dearmor(armor(b"first") + armor(b"second")), b"firstsecond")

    def test_dearmor_invalid(self):
        with self.assertRaises(ValueError):
            pgp.dearmor(armor(b"test", checksum=b"abc"))
        with self.assertRaises(ValueError):
            pgp.dearmor(b"not a key")
        with self.assertRaises(ValueError):
            pgp.dearmor(f"{pgp.ARMOR_BEGIN}\n\nAAAA\n".encode())

    def test_is_armored(self):
        self.assertFalse(pgp.is_armored(b"\x99\x01binary key"))
