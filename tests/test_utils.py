"""Tests for ./misc_utils.py."""

import unittest

import misc_utils as utils


class UtilsTestCase(unittest.TestCase):
    """Smoke tests for the miscellaneous utilities."""

    @staticmethod
    def test_print_info() -> None:
        """Check that printing info does not fail."""
        utils.print_info("test")

    @staticmethod
    def test_run() -> None:
        """Check that running a command does not fail."""
        utils.run(["echo", "test"])

    @staticmethod
    def test_run_output() -> None:
        """Check that running a command and capturing its output does not fail."""
        utils.run(["echo", "test"], get_output=True)

    # @staticmethod
    # def test_disk():
    #     mount_info = utils.MountInfo("/")
    #     device = mount_info.device
    #     disk_info = utils.DiskInfo(device)
    #     disk_info.print()
    #     disk_info.lsblk()
