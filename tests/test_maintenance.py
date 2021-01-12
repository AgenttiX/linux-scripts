import unittest

import maintenance as mnt


class MaintenanceTestCase(unittest.TestCase):
    # This takes too long on GitHub runners
    # @staticmethod
    # def test_apt():
    #     mnt.apt()

    @staticmethod
    def test_bleachbit():
        mnt.bleachbit()

    @staticmethod
    def test_docker():
        mnt.docker()

    @staticmethod
    def test_fwupdmgr():
        mnt.fwupdmgr()

    @staticmethod
    def test_security():
        mnt.security()

    @staticmethod
    def test_trim():
        mnt.trim()
