"""Tests for the scripts in ./install."""

import dataclasses
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock

from install import apt_packages, apt_sources, asdf, dpkg, flatpak, install, install_sudo
from install import utils as install_utils
from tests.utils import REPO_PATH

HEADLESS_VM = install_utils.SystemInfo(
    arch="amd64",
    chassis="vm",
    desktop_env="",
    has_intel_cpu=False,
    has_nvidia_gpu=False,
    is_physical=False,
    os_release={"NAME": "Ubuntu", "VERSION_CODENAME": "resolute", "VERSION_ID": "26.04"},
)
KDE_LAPTOP = dataclasses.replace(
    HEADLESS_VM, chassis="laptop", desktop_env="KDE", has_intel_cpu=True, is_physical=True,
)


class AptPackagesTestCase(unittest.TestCase):
    def test_headless_vm(self):
        packages = apt_packages.get_packages(HEADLESS_VM, installed={"kwin-wayland"})
        self.assertIn("git", packages)
        self.assertNotIn("vlc", packages)
        self.assertNotIn("tlp", packages)
        self.assertNotIn("lm-sensors", packages)
        self.assertNotIn("intel-microcode", packages)
        self.assertFalse(any(package.endswith("-dbgsym") for package in packages))

    def test_kde_laptop(self):
        packages = apt_packages.get_packages(KDE_LAPTOP, installed={"kwin-wayland"})
        for package in ("vlc", "kde-config-flatpak", "tlp", "touchegg", "obs-studio", "intel-microcode"):
            self.assertIn(package, packages)
        self.assertIn("kwin-wayland-dbgsym", packages)
        self.assertNotIn("kscreen-dbgsym", packages)
        self.assertNotIn("boinc-client-nvidia-cuda", packages)
        self.assertEqual(len(packages), len(set(packages)), "Duplicate packages")

    def test_nvidia(self):
        info = dataclasses.replace(HEADLESS_VM, has_nvidia_gpu=True)
        self.assertIn("boinc-client-nvidia-cuda", apt_packages.get_packages(info, installed=set()))

    def test_external_debs(self):
        self.assertEqual(apt_packages.get_external_debs(HEADLESS_VM, installed=set()), [])
        debs = apt_packages.get_external_debs(KDE_LAPTOP, installed={"zoom"})
        self.assertEqual([package for package, _ in debs], ["google-chrome-stable"])
        self.assertTrue(all(url.startswith("https://") for _, url in debs))
        arm = dataclasses.replace(KDE_LAPTOP, arch="arm64")
        self.assertEqual(apt_packages.get_external_debs(arm, installed=set()), [])


class AptSourcesTestCase(unittest.TestCase):
    def test_render(self):
        source = apt_sources.AptSource(
            name="test",
            uris="https://example.com/apt",
            suites="stable",
            components="main",
            signed_by=pathlib.Path("/etc/apt/keyrings/test.gpg"),
            architectures="amd64",
        )
        self.assertEqual(
            source.render(),
            "Types: deb\n"
            "URIs: https://example.com/apt\n"
            "Suites: stable\n"
            "Components: main\n"
            "Signed-By: /etc/apt/keyrings/test.gpg\n"
            "Architectures: amd64\n",
        )
        self.assertEqual(source.path, pathlib.Path("/etc/apt/sources.list.d/test.sources"))

    def test_sources(self):
        headless = {source.name for source in apt_sources.get_sources(HEADLESS_VM)}
        desktop = {source.name for source in apt_sources.get_sources(KDE_LAPTOP)}
        self.assertIn("docker", headless)
        self.assertNotIn("signal-xenial", headless)
        self.assertTrue(headless < desktop)
        self.assertIn("signal-xenial", desktop)

    def test_sources_secure(self):
        for source in apt_sources.get_sources(KDE_LAPTOP):
            self.assertTrue(source.signed_by.is_absolute())
            if source.key_url is not None:
                self.assertTrue(source.key_url.startswith("https://"), source.key_url)

    def test_ppas(self):
        self.assertEqual(apt_sources.get_ppas(HEADLESS_VM), [])
        self.assertIn("ppa:linrunner/tlp", apt_sources.get_ppas(KDE_LAPTOP))
        self.assertIn("ppa:touchegg/stable", apt_sources.get_ppas(KDE_LAPTOP))


class AsdfTestCase(unittest.TestCase):
    def test_plugins(self):
        self.assertEqual(asdf.get_plugins(HEADLESS_VM), ["actionlint"])
        self.assertIn("protonge", asdf.get_plugins(KDE_LAPTOP))


class DpkgTestCase(unittest.TestCase):
    def test_installed_packages(self):
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
        self.assertEqual(dpkg.get_installed_packages(status), {"foo", "baz"})

    def test_installed_packages_system(self):
        if not dpkg.STATUS_PATH.exists():
            self.skipTest("dpkg is not installed")
        self.assertIn("dpkg", dpkg.get_installed_packages())

    def test_enable_i386(self):
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
    def test_headless(self):
        self.assertEqual(flatpak.get_packages(HEADLESS_VM), [])

    def test_desktop(self):
        packages = flatpak.get_packages(KDE_LAPTOP)
        self.assertIn("org.zotero.Zotero", packages)
        self.assertIn("com.slack.Slack", packages)
        self.assertIn("org.telegram.desktop", packages)

    def test_steamos(self):
        info = dataclasses.replace(KDE_LAPTOP, os_release={"NAME": "SteamOS"})
        packages = flatpak.get_packages(info)
        self.assertIn("org.keepassxc.KeePassXC", packages)
        self.assertIn("org.zotero.Zotero", packages)
        self.assertNotIn("com.slack.Slack", packages)


class InstallTestCase(unittest.TestCase):
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

    def test_sources_not_passed_by_default(self):
        command = self._main().call_args.args[0]
        self.assertEqual(command[:2], ["sudo", install.SYSTEM_PYTHON])
        self.assertIn("--desktop-env=KDE", command)
        self.assertNotIn("--sources", command)

    def test_sources_passed(self):
        self.assertIn("--sources", self._main("--sources").call_args.args[0])

    def test_sources_with_skip_sudo(self):
        with self.assertRaises(SystemExit), mock.patch("sys.stderr"):
            self._main("--sources", "--skip-sudo")


class InstallMainTestCase(unittest.TestCase):
    def test_arguments_are_passed(self):
        # This combination fails in argument parsing, so nothing gets installed.
        for command in (["-m", "install"], [str(REPO_PATH / "install")]):
            with self.subTest(command=command):
                result = subprocess.run(
                    [sys.executable, *command, "--skip-sudo", "--sources"],
                    capture_output=True, check=False, cwd=REPO_PATH, text=True,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("cannot be used with --skip-sudo", result.stderr)


class InstallSudoTestCase(unittest.TestCase):
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

    def test_sources_skipped_by_default(self):
        self._main().assert_not_called()

    def test_sources(self):
        self._main("--sources").assert_called_once()

    def test_bwrap_not_needed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            sysctl = pathlib.Path(temp_dir) / "sysctl"
            sysctl.write_text("0\n")
            with (
                mock.patch.object(install_sudo, "APPARMOR_USERNS_SYSCTL", sysctl),
                mock.patch.object(install_utils, "run") as run,
            ):
                install_sudo.fix_bwrap_apparmor()
            run.assert_not_called()

    def test_bwrap_fix(self):
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
                self.assertEqual(profile.read_text(), install_sudo.BWRAP_APPARMOR_PROFILE)
                self.assertEqual(profile.stat().st_mode & 0o777, 0o644)
                run.assert_called_once_with(["systemctl", "reload", "apparmor"])
                # The profile is not rewritten if it's already up to date.
                install_sudo.fix_bwrap_apparmor()
                run.assert_called_once()


class InstallUtilsTestCase(unittest.TestCase):
    def test_detect_chassis(self):
        self.assertEqual(install_utils.detect_chassis("", "10\n", is_physical=True), "laptop")
        self.assertEqual(install_utils.detect_chassis("", "3\n", is_physical=True), "desktop")
        self.assertEqual(install_utils.detect_chassis("", "", is_physical=True), "")
        self.assertEqual(install_utils.detect_chassis("", "10\n", is_physical=False), "vm")
        self.assertEqual(install_utils.detect_chassis('CHASSIS="server"\n', "10\n", is_physical=True), "server")

    def test_parse_os_release(self):
        text = '# Comment\nNAME="Ubuntu"\nVERSION_ID="26.04"\nVERSION_CODENAME=resolute\nID_LIKE=\'debian\'\n\n'
        self.assertEqual(
            install_utils.parse_os_release(text),
            {"NAME": "Ubuntu", "VERSION_ID": "26.04", "VERSION_CODENAME": "resolute", "ID_LIKE": "debian"},
        )

    def test_download_requires_https(self):
        with self.assertRaises(ValueError):
            install_utils.download("http://example.com/key.gpg")

    def test_insecure_redirect(self):
        handler = install_utils._HTTPSOnlyRedirectHandler()
        request = install_utils.urllib.request.Request("https://example.com/key.gpg")
        with self.assertRaises(install_utils.urllib.error.HTTPError):
            handler.redirect_request(request, None, 302, "Found", {}, "http://example.com/key.gpg")
        redirected = handler.redirect_request(request, None, 302, "Found", {}, "https://example.org/key.gpg")
        self.assertEqual(redirected.full_url, "https://example.org/key.gpg")

    def test_write_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = pathlib.Path(temp_dir) / "sub" / "file"
            install_utils.write_file(path, "test", mode=0o600)
            self.assertEqual(path.read_text(), "test")
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            install_utils.write_file(path, b"new")
            self.assertEqual(path.read_bytes(), b"new")
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_system_info_desktop(self):
        self.assertFalse(HEADLESS_VM.is_desktop)
        self.assertFalse(HEADLESS_VM.is_laptop)
        self.assertTrue(KDE_LAPTOP.is_desktop)
        self.assertTrue(KDE_LAPTOP.is_laptop)

    def test_system_info_detect(self):
        info = install_utils.SystemInfo.detect(desktop_env="")
        self.assertFalse(info.is_desktop)
        self.assertTrue(info.arch)
