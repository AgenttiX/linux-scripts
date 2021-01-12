import unittest

import maintenance as mnt


class MaintenanceTestCase(unittest.TestCase):
    @staticmethod
    def test_bleachbit():
        mnt.bleachbit()

    @staticmethod
    def test_docker():
        mnt.docker()

    @staticmethod
    def test_security():
        mnt.security()

    @staticmethod
    def test_trim():
        mnt.trim()
