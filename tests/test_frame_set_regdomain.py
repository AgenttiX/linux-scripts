"""Tests for ./frame/set_regdomain.py."""

import pathlib
import tempfile
import types
import unittest

import pytest

from tests.utils import REPO_PATH, load_module

SCRIPT = REPO_PATH / "frame" / "set_regdomain.py"
set_regdomain: types.ModuleType = load_module("set_regdomain", SCRIPT)

PHY_INFO = """Wiphy phy1
	Band 1:
		Frequencies:
			* 2412.0 MHz [1] (20.0 dBm)
			* 2472.0 MHz [13] (20.0 dBm) (no IR)
			* 2484.0 MHz [14] (disabled)
	Band 2:
		Frequencies:
			* 5180.0 MHz [36] (20.0 dBm)
			* 5260.0 MHz [52] (20.0 dBm) (no IR, radar detection)
	Band 4:
		Frequencies:
			* 5955.0 MHz [1] (disabled)
			* 5975.0 MHz [5] (disabled)
"""

REG_GET_WORLD = """global
country 00: DFS-UNSET
	(2402 - 2472 @ 40), (N/A, 20), (N/A)

phy#0 (self-managed)
country FI: DFS-UNSET
	(2402 - 2437 @ 40), (6, 22), (N/A), AUTO-BW
"""


class SetRegdomainTestCase(unittest.TestCase):
    """Tests for the regulatory domain helper functions."""

    def test_channel_counts(self) -> None:
        """Check that the channels are classified by band and availability."""
        counts = set_regdomain.channel_counts(PHY_INFO)
        assert counts == {
            "2.4 GHz": set_regdomain.BandChannels(usable=1, passive=1, disabled=1),
            "5 GHz": set_regdomain.BandChannels(usable=1, passive=1, disabled=0),
            "6 GHz": set_regdomain.BandChannels(usable=0, passive=0, disabled=2),
        }

    def test_detect_country(self) -> None:
        """Check that the country is detected from the self-managed adapters, and then from the global domain."""
        reg_cls = set_regdomain.RegDomains
        assert set_regdomain.detect_country(set_regdomain.parse_reg_get(REG_GET_WORLD)) == "FI"
        assert set_regdomain.detect_country(reg_cls(global_country="SE", self_managed={})) == "SE"
        assert set_regdomain.detect_country(reg_cls(global_country="00", self_managed={})) is None
        assert set_regdomain.detect_country(reg_cls(global_country="00", self_managed={"phy0": "00"})) is None
        assert set_regdomain.detect_country(
            reg_cls(global_country="00", self_managed={"phy0": "FI", "phy2": "SE"})
        ) is None

    def test_list_wireless_interfaces(self) -> None:
        """Check that the USB IDs and drivers are read from a fake sysfs tree."""
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            net = root / "net"
            # USB adapter: the device symlink points to the USB interface below the USB device.
            usb_dev = root / "usb" / "2-2"
            usb_iface = usb_dev / "2-2:1.0"
            usb_iface.mkdir(parents=True)
            (usb_dev / "idVendor").write_text("28de\n")
            (usb_dev / "idProduct").write_text("2432\n")
            driver = root / "drivers" / "rtw89_8852cu"
            driver.mkdir(parents=True)
            (usb_iface / "driver").symlink_to(driver)
            wlx = net / "wlx0"
            (wlx / "phy80211").mkdir(parents=True)
            (wlx / "phy80211" / "name").write_text("phy1\n")
            (wlx / "device").symlink_to(usb_iface)
            # PCI adapter without USB IDs.
            pci_dev = root / "pci" / "0000:48:00.0"
            pci_dev.mkdir(parents=True)
            wlp = net / "wlp0"
            (wlp / "phy80211").mkdir(parents=True)
            (wlp / "phy80211" / "name").write_text("phy0\n")
            (wlp / "device").symlink_to(pci_dev)
            # Wired interface.
            (net / "enp0").mkdir()

            interfaces = set_regdomain.list_wireless_interfaces(net)

        assert interfaces == [
            set_regdomain.WirelessInterface(name="wlp0", phy="phy0", driver=None, usb_id=None),
            set_regdomain.WirelessInterface(name="wlx0", phy="phy1", driver="rtw89_8852cu", usb_id="28de:2432"),
        ]
        assert not interfaces[0].is_steam_frame_adapter
        assert interfaces[1].is_steam_frame_adapter

    def test_parse_reg_get(self) -> None:
        """Check that the global and self-managed domains are parsed."""
        reg = set_regdomain.parse_reg_get(REG_GET_WORLD)
        assert reg.global_country == "00"
        assert reg.self_managed == {"phy0": "FI"}

    def test_validate_country(self) -> None:
        """Check that the country codes are normalized and invalid ones rejected."""
        assert set_regdomain.validate_country(" fi ") == "FI"
        for invalid in ("00", "FIN", "F", "F1", "", "FI; rm"):
            with self.subTest(country=invalid), pytest.raises(ValueError, match="Invalid country code"):
                set_regdomain.validate_country(invalid)

    def test_write_persistent(self) -> None:
        """Check that the config is written once with the correct content and permissions."""
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "cfg80211-regdom.conf"
            assert set_regdomain.write_persistent("FI", path)
            assert "options cfg80211 ieee80211_regdom=FI\n" in path.read_text()
            assert path.stat().st_mode & 0o777 == 0o644
            assert not set_regdomain.write_persistent("FI", path)
            assert set_regdomain.write_persistent("SE", path)
            assert "ieee80211_regdom=SE" in path.read_text()
            assert sorted(p.name for p in pathlib.Path(tmp).iterdir()) == ["cfg80211-regdom.conf"]
