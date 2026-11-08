"""Tests for ./modem.py."""

import os
import unittest

import modem


class ModemTestCase(unittest.TestCase):
    """Tests for the modem utilities."""

    def test_read_pin(self) -> None:
        """Check that the PIN is read back from a file as written."""
        path = "modem-pin.txt"
        pin = "12345678"
        with open(path, "w") as file:
            file.write(pin)
        pin2 = modem.read_pin(path)
        assert pin == pin2

    @staticmethod
    @unittest.skipIf("GITHUB_ACTIONS" in os.environ, reason="Unsupported on GitHub Actions")
    def test_modem_number() -> None:
        """Check that the modem number can be detected."""
        modem.modem_number()
