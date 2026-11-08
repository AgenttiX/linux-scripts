"""Tests for ./maintenance.py."""

import unittest

import maintenance as mnt


class MaintenanceTestCase(unittest.TestCase):
    """Smoke tests for the maintenance tasks."""

    # This takes too long on GitHub runners
    # @staticmethod
    # def test_apt():
    #     mnt.apt()

    @staticmethod
    def test_bleachbit() -> None:
        """Check that the BleachBit cleanup runs without errors."""
        mnt.bleachbit()

    @staticmethod
    def test_docker() -> None:
        """Check that the Docker cleanup runs without errors."""
        mnt.docker()

    @staticmethod
    def test_fwupdmgr() -> None:
        """Check that the firmware update check runs without errors."""
        mnt.fwupdmgr()

    @staticmethod
    def test_security() -> None:
        """Check that the security scanners run without errors."""
        mnt.security()

    @staticmethod
    def test_trim() -> None:
        """Check that trimming the file systems runs without errors."""
        mnt.trim()
