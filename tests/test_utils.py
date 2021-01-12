import unittest

import utils


class UtilsTestCase(unittest.TestCase):
    @staticmethod
    def test_print_info():
        utils.print_info("test")

    @staticmethod
    def test_run():
        utils.run(["echo", "test"])

    # @staticmethod
    # def test_disk():
    #     mount_info = utils.MountInfo("/")
    #     device = mount_info.device
    #     disk_info = utils.DiskInfo(device)
    #     disk_info.print()
    #     disk_info.lsblk()
