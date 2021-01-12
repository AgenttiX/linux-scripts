import unittest

import modem


class ModemTestCase(unittest.TestCase):
    def test_read_pin(self):
        path = "modem-pin.txt"
        pin = "12345678"
        with open(path, "w") as file:
            file.write(pin)
        pin2 = modem.read_pin(path)
        self.assertEqual(pin, pin2)

    @staticmethod
    def test_modem_number():
        try:
            modem.modem_number()
        except ValueError:
            pass
