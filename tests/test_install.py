"""Tests for the scripts in ./install."""

import dataclasses
import http.client
import io
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock
import urllib.error
import urllib.request

import pytest

from install import apt_packages, apt_sources, asdf, dpkg, flatpak, install, install_sudo
from install import utils as install_utils
from tests.utils import REPO_PATH

HEADLESS_VM: install_utils.SystemInfo = install_utils.SystemInfo(
    arch="amd64",
    chassis="vm",
    desktop_env="",
    has_intel_cpu=False,
    has_nvidia_gpu=False,
    is_physical=False,
    os_release={"NAME": "Ubuntu", "VERSION_CODENAME": "resolute", "VERSION_ID": "26.04"},
)
KDE_LAPTOP: install_utils.SystemInfo = dataclasses.replace(
    HEADLESS_VM, chassis="laptop", desktop_env="KDE", has_intel_cpu=True, is_physical=True,
)


class AptPackagesTestCase(unittest.TestCase):
    """Tests for selecting the apt packages to install."""

    def test_headless_vm(self) -> None:
        """Check that a headless VM gets base packages without desktop, laptop or debug packages."""
        packages = apt_packages.get_packages(HEADLESS_VM, installed={"kwin-wayland"})
        assert "git" in packages
        assert "vlc" not in packages
        assert "tlp" not in packages
        assert "lm-sensors" not in packages
        assert "intel-microcode" not in packages
        assert not any(package.endswith("-dbgsym") for package in packages)

    def test_kde_laptop(self) -> None:
        """Check that a KDE laptop gets its packages, only installed debug symbols and no duplicates."""
        packages = apt_packages.get_packages(KDE_LAPTOP, installed={"kwin-wayland"})
        for package in ("vlc", "kde-config-flatpak", "tlp", "touchegg", "obs-studio", "intel-microcode"):
            assert package in packages
        assert "kwin-wayland-dbgsym" in packages
        assert "kscreen-dbgsym" not in packages
        assert "boinc-client-nvidia-cuda" not in packages
        assert len(packages) == len(set(packages)), "Duplicate packages"

    def test_nvidia(self) -> None:
        """Check that an Nvidia GPU adds the CUDA BOINC client."""
        info = dataclasses.replace(HEADLESS_VM, has_nvidia_gpu=True)
        assert "boinc-client-nvidia-cuda" in apt_packages.get_packages(info, installed=set())

    def test_external_debs(self) -> None:
        """Check that external .deb packages are desktop-only, amd64-only and use HTTPS."""
        assert apt_packages.get_external_debs(HEADLESS_VM, installed=set()) == []
        debs = apt_packages.get_external_debs(KDE_LAPTOP, installed={"zoom"})
        assert [package for package, _ in debs] == ["google-chrome-stable"]
        assert all(url.startswith("https://") for _, url in debs)
        arm = dataclasses.replace(KDE_LAPTOP, arch="arm64")
        assert apt_packages.get_external_debs(arm, installed=set()) == []


class AptSourcesTestCase(unittest.TestCase):
    """Tests for the apt source definitions."""

    def test_render(self) -> None:
        """Check that a source is rendered in the deb822 format to the correct path."""
        source = apt_sources.AptSource(
            name="test",
            uris="https://example.com/apt",
            suites="stable",
            components="main",
            signed_by=pathlib.Path("/etc/apt/keyrings/test.gpg"),
            architectures="amd64",
        )
        assert source.render() == (
            "Types: deb\n"
            "URIs: https://example.com/apt\n"
            "Suites: stable\n"
            "Components: main\n"
            "Signed-By: /etc/apt/keyrings/test.gpg\n"
            "Architectures: amd64\n"
        )
        assert source.path == pathlib.Path("/etc/apt/sources.list.d/test.sources")

    def test_sources(self) -> None:
        """Check that desktops get a strict superset of the headless sources."""
        headless = {source.name for source in apt_sources.get_sources(HEADLESS_VM)}
        desktop = {source.name for source in apt_sources.get_sources(KDE_LAPTOP)}
        assert "docker" in headless
        assert "signal-xenial" not in headless
        assert headless < desktop
        assert "signal-xenial" in desktop

    def test_sources_secure(self) -> None:
        """Check that all sources have an absolute keyring path and HTTPS key URLs."""
        for source in apt_sources.get_sources(KDE_LAPTOP):
            assert source.signed_by.is_absolute()
            if source.key_url is not None:
                assert source.key_url.startswith("https://"), source.key_url

    def test_ppas(self) -> None:
        """Check that PPAs are added only on desktops."""
        assert apt_sources.get_ppas(HEADLESS_VM) == []
        assert "ppa:linrunner/tlp" in apt_sources.get_ppas(KDE_LAPTOP)
        assert "ppa:touchegg/stable" in apt_sources.get_ppas(KDE_LAPTOP)


class AsdfTestCase(unittest.TestCase):
    """Tests for selecting the asdf plugins."""

    def test_plugins(self) -> None:
        """Check that headless systems get only the basic plugins and desktops get more."""
        assert asdf.get_plugins(HEADLESS_VM) == ["actionlint"]
        assert "protonge" in asdf.get_plugins(KDE_LAPTOP)


class DpkgTestCase(unittest.TestCase):
    """Tests for the dpkg helpers."""

    def test_installed_packages(self) -> None:
        """Check that only fully installed packages are parsed from a dpkg status file."""
        status = textwrap.dedent("""\
            Package: foo
            Status: install ok installed
            Description: Foo
             Status: install ok installed

            Package: bar
            Status: deinstall ok config-files

            Package: baz
            Architecture: i386
            Status: install ok installed
            """)
        assert dpkg.get_installed_packages(status) == {"foo", "baz"}

    def test_installed_packages_system(self) -> None:
        """Check that the installed packages of the running system include dpkg."""
        if not dpkg.STATUS_PATH.exists():
            self.skipTest("dpkg is not installed")
        assert "dpkg" in dpkg.get_installed_packages()

    def test_enable_i386(self) -> None:
        """Check that the i386 architecture is added only on amd64 when it is missing."""
        with (
            mock.patch.object(dpkg, "get_foreign_architectures", return_value=[]),
            mock.patch.object(dpkg, "add_architecture") as add_architecture,
        ):
            dpkg.enable_i386(dataclasses.replace(HEADLESS_VM, arch="arm64"))
            add_architecture.assert_not_called()
            dpkg.enable_i386(HEADLESS_VM)
            add_architecture.assert_called_once_with("i386")
        with (
            mock.patch.object(dpkg, "get_foreign_architectures", return_value=["i386"]),
            mock.patch.object(dpkg, "add_architecture") as add_architecture,
        ):
            dpkg.enable_i386(HEADLESS_VM)
            add_architecture.assert_not_called()


class FlatpakTestCase(unittest.TestCase):
    """Tests for selecting the Flatpak packages."""

    def test_headless(self) -> None:
        """Check that headless systems get no Flatpak packages."""
        assert flatpak.get_packages(HEADLESS_VM) == []

    def test_desktop(self) -> None:
        """Check that desktops get the desktop Flatpak packages."""
        packages = flatpak.get_packages(KDE_LAPTOP)
        assert "org.zotero.Zotero" in packages
        assert "com.slack.Slack" in packages
        assert "org.telegram.desktop" in packages

    def test_steamos(self) -> None:
        """Check that SteamOS gets its own package selection."""
        info = dataclasses.replace(KDE_LAPTOP, os_release={"NAME": "SteamOS"})
        packages = flatpak.get_packages(info)
        assert "org.keepassxc.KeePassXC" in packages
        assert "org.zotero.Zotero" in packages
        assert "com.slack.Slack" not in packages


class InstallTestCase(unittest.TestCase):
    """Tests for the unprivileged install script."""

    def _main(self, *args: str) -> mock.MagicMock:
        with (
            mock.patch.object(sys, "argv", ["install.py", "--desktop-env=KDE", *args]),
            mock.patch.object(install_utils, "require_not_root"),
            mock.patch.object(install_utils, "setup_logging"),
            mock.patch.object(install_utils, "run") as run,
            mock.patch.object(flatpak, "install_packages"),
            mock.patch.object(asdf, "install_plugins"),
        ):
            install.main()
        return run

    def test_sources_not_passed_by_default(self) -> None:
        """Check that the sudo script is run without "--sources" by default."""
        command = self._main().call_args.args[0]
        assert command[:2] == ["sudo", install.SYSTEM_PYTHON]
        assert "--desktop-env=KDE" in command
        assert "--sources" not in command

    def test_sources_passed(self) -> None:
        """Check that "--sources" is passed on to the sudo script."""
        assert "--sources" in self._main("--sources").call_args.args[0]

    def test_sources_with_skip_sudo(self) -> None:
        """Check that "--sources" cannot be combined with "--skip-sudo"."""
        with pytest.raises(SystemExit), mock.patch("sys.stderr"):
            self._main("--sources", "--skip-sudo")


class InstallMainTestCase(unittest.TestCase):
    """Tests for running the install package as a program."""

    def test_arguments_are_passed(self) -> None:
        """Check that both "python -m install" and the directory pass their arguments on."""
        # This combination fails in argument parsing, so nothing gets installed.
        for command in (["-m", "install"], [str(REPO_PATH / "install")]):
            with self.subTest(command=command):
                result = subprocess.run(
                    [sys.executable, *command, "--skip-sudo", "--sources"],
                    capture_output=True, check=False, cwd=REPO_PATH, text=True,
                )
                assert result.returncode == 2
                assert "cannot be used with --skip-sudo" in result.stderr


class InstallSudoTestCase(unittest.TestCase):
    """Tests for the privileged install script."""

    def _main(self, *args: str) -> mock.MagicMock:
        with (
            mock.patch.object(sys, "argv", ["install_sudo.py", "--desktop-env=", *args]),
            mock.patch.object(install_utils, "require_root"),
            mock.patch.object(install_utils, "setup_logging"),
            mock.patch.object(install_utils, "command_exists", return_value=True),
            mock.patch.object(apt_sources, "setup_sources") as setup_sources,
            mock.patch.object(apt_packages, "install_packages") as install_packages,
            mock.patch.object(install_sudo, "install_snaps"),
            mock.patch.object(install_sudo, "fix_bwrap_apparmor"),
        ):
            install_sudo.main()
        install_packages.assert_called_once()
        return setup_sources

    def test_sources_skipped_by_default(self) -> None:
        """Check that the apt sources are not configured by default."""
        self._main().assert_not_called()

    def test_sources(self) -> None:
        """Check that "--sources" configures the apt sources."""
        self._main("--sources").assert_called_once()

    def test_bwrap_not_needed(self) -> None:
        """Check that no AppArmor profile is installed when user namespaces are not restricted."""
        with tempfile.TemporaryDirectory() as temp_dir:
            sysctl = pathlib.Path(temp_dir) / "sysctl"
            sysctl.write_text("0\n")
            with (
                mock.patch.object(install_sudo, "APPARMOR_USERNS_SYSCTL", sysctl),
                mock.patch.object(install_utils, "run") as run,
            ):
                install_sudo.fix_bwrap_apparmor()
            run.assert_not_called()

    def test_bwrap_fix(self) -> None:
        """Check that the bwrap AppArmor profile is written once with the correct mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            sysctl = pathlib.Path(temp_dir) / "sysctl"
            sysctl.write_text("1\n")
            profile = pathlib.Path(temp_dir) / "apparmor.d" / "bwrap"
            with (
                mock.patch.object(install_sudo, "APPARMOR_USERNS_SYSCTL", sysctl),
                mock.patch.object(install_sudo, "BWRAP_APPARMOR_PROFILE_PATH", profile),
                mock.patch.object(install_utils, "run") as run,
            ):
                install_sudo.fix_bwrap_apparmor()
                assert profile.read_text() == install_sudo.BWRAP_APPARMOR_PROFILE
                assert profile.stat().st_mode & 511 == 420
                run.assert_called_once_with(["systemctl", "reload", "apparmor"])
                # The profile is not rewritten if it's already up to date.
                install_sudo.fix_bwrap_apparmor()
                run.assert_called_once()


class InstallUtilsTestCase(unittest.TestCase):
    """Tests for the shared install utilities."""

    def test_detect_chassis(self) -> None:
        """Check the chassis detection from machine-info and DMI data."""
        assert install_utils.detect_chassis("", "10\n", is_physical=True) == "laptop"
        assert install_utils.detect_chassis("", "3\n", is_physical=True) == "desktop"
        assert install_utils.detect_chassis("", "", is_physical=True) == ""
        assert install_utils.detect_chassis("", "10\n", is_physical=False) == "vm"
        assert install_utils.detect_chassis('CHASSIS="server"\n', "10\n", is_physical=True) == "server"

    def test_parse_os_release(self) -> None:
        """Check that os-release is parsed with comments, quotes and blank lines."""
        text = '# Comment\nNAME="Ubuntu"\nVERSION_ID="26.04"\nVERSION_CODENAME=resolute\nID_LIKE=\'debian\'\n\n'
        assert install_utils.parse_os_release(text) == {
            "NAME": "Ubuntu", "VERSION_ID": "26.04", "VERSION_CODENAME": "resolute", "ID_LIKE": "debian",
        }

    def test_download_requires_https(self) -> None:
        """Check that downloads over plain HTTP are refused."""
        with pytest.raises(ValueError, match="insecure connection"):
            install_utils.download("http://example.com/key.gpg")

    def test_insecure_redirect(self) -> None:
        """Check that redirects to HTTP are refused and redirects to HTTPS are followed."""
        handler = install_utils._HTTPSOnlyRedirectHandler()
        request = urllib.request.Request("https://example.com/key.gpg")
        headers = http.client.HTTPMessage()
        with pytest.raises(urllib.error.HTTPError):
            handler.redirect_request(request, io.BytesIO(), 302, "Found", headers, "http://example.com/key.gpg")
        redirected = handler.redirect_request(request, io.BytesIO(), 302, "Found", headers, "https://example.org/key.gpg")
        assert redirected is not None
        assert redirected.full_url == "https://example.org/key.gpg"

    def test_write_file(self) -> None:
        """Check that files are written atomically with the given mode and without leftovers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            path = pathlib.Path(temp_dir) / "sub" / "file"
            install_utils.write_file(path, "test", mode=0o600)
            assert path.read_text() == "test"
            assert path.stat().st_mode & 511 == 384
            install_utils.write_file(path, b"new")
            assert path.read_bytes() == b"new"
            assert list(path.parent.iterdir()) == [path]

    def test_system_info_desktop(self) -> None:
        """Check the desktop and laptop properties of the system info."""
        assert not HEADLESS_VM.is_desktop
        assert not HEADLESS_VM.is_laptop
        assert KDE_LAPTOP.is_desktop
        assert KDE_LAPTOP.is_laptop

    def test_system_info_detect(self) -> None:
        """Check that the system info of the running system can be detected."""
        info = install_utils.SystemInfo.detect(desktop_env="")
        assert not info.is_desktop
        assert info.arch
