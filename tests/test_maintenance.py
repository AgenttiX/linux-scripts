import unittest

import maintenance as mnt


class MaintenanceTestCase(unittest.TestCase):
    # Running Apt from Python does not work on the GitHub runner, but results in several errors of the form:
    # 13: Permission denied
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

    # Trimming on the GitHub runner results in
    # FITRIM ioctl failed: Operation not permitted
    # @staticmethod
    # def test_trim():
    #     mnt.trim()
