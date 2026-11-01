"""Test the Steam DRM device filter"""

import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from tests.utils import REPO_PATH

FILTER_SOURCE = REPO_PATH / "games" / "steam" / "steam_drm_filter.c"

# Prints the PCI vendor IDs returned by drmGetDevices2,
# first when linked directly and then when resolved with dlopen() and dlsym() like Steam does.
PROBE_SOURCE = r"""
#include <dlfcn.h>
#include <stdio.h>
#include <xf86drm.h>

typedef int (*get_devices2_fn)(uint32_t, drmDevicePtr[], int);
typedef void (*free_devices_fn)(drmDevicePtr[], int);

static void print_devices(const char *label, get_devices2_fn get, free_devices_fn free_devices) {
    drmDevicePtr devices[64];
    const int count = get(0, devices, 64);
    const int count_only = get(0, NULL, 0);
    printf("%s %d %d", label, count, count_only);
    for (int i = 0; i < count; ++i) {
        if (devices[i]->bustype == DRM_BUS_PCI) {
            printf(" %04x", devices[i]->deviceinfo.pci->vendor_id);
        }
    }
    printf("\n");
    if (count > 0) {
        free_devices(devices, count);
    }
}

int main(void) {
    print_devices("direct", drmGetDevices2, drmFreeDevices);
    void *handle = dlopen("libdrm.so.2", RTLD_NOW);
    if (handle == NULL) {
        return 1;
    }
    print_devices("dlopen", (get_devices2_fn)dlsym(handle, "drmGetDevices2"),
                  (free_devices_fn)dlsym(handle, "drmFreeDevices"));
    return 0;
}
"""


def _parse(output: str) -> dict[str, tuple[int, int, list[str]]]:
    result = {}
    for line in output.splitlines():
        label, count, count_only, *vendors = line.split()
        result[label] = (int(count), int(count_only), vendors)
    return result


@unittest.skipUnless(shutil.which("gcc"), "gcc is not installed")
@unittest.skipUnless(pathlib.Path("/usr/include/xf86drm.h").exists(), "libdrm headers are not installed")
class SteamDrmFilterTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = pathlib.Path(self.tmp.name)
        self.lib = self.tmp_path / "libagx-drm-filter.so"
        self.probe = self.tmp_path / "probe"
        probe_source = self.tmp_path / "probe.c"
        probe_source.write_text(PROBE_SOURCE)
        cflags = ["-Wall", "-Wextra", "-Werror", "-I/usr/include/libdrm"]
        subprocess.run(
            ["gcc", "-shared", "-fPIC", *cflags, "-o", str(self.lib), str(FILTER_SOURCE), "-ldl", "-l:libdrm.so.2"],
            check=True,
        )
        subprocess.run(
            ["gcc", *cflags, "-o", str(self.probe), str(probe_source), "-ldl", "-l:libdrm.so.2"],
            check=True,
        )

    def tearDown(self):
        self.tmp.cleanup()

    def run_probe(self, hide_vendors: str | None) -> dict[str, tuple[int, int, list[str]]]:
        env = os.environ.copy()
        env["LD_PRELOAD"] = str(self.lib)
        env.pop("AGX_DRM_HIDE_VENDORS", None)
        if hide_vendors is not None:
            env["AGX_DRM_HIDE_VENDORS"] = hide_vendors
        res = subprocess.run([str(self.probe)], env=env, capture_output=True, text=True, check=True)
        return _parse(res.stdout)

    def test_no_filter(self):
        result = self.run_probe(None)
        self.assertEqual(result["direct"], result["dlopen"])
        self.assertEqual(result["direct"][0], result["direct"][1])

    def test_hide_unknown_vendor(self):
        self.assertEqual(self.run_probe("0xffff"), self.run_probe(None))

    def test_hide_vendors(self):
        unfiltered = self.run_probe(None)["direct"]
        vendors = unfiltered[2]
        if not vendors:
            self.skipTest("No PCI DRM devices available")
        hidden = vendors[0]
        result = self.run_probe(f"0x{hidden},0xffff")
        expected = [vendor for vendor in vendors if vendor != hidden]
        for label in ("direct", "dlopen"):
            with self.subTest(label=label):
                count, count_only, result_vendors = result[label]
                self.assertEqual(result_vendors, expected)
                self.assertEqual(count, len(expected))
                self.assertEqual(count_only, len(expected))

    def test_hide_all_vendors(self):
        vendors = self.run_probe(None)["direct"][2]
        if not vendors:
            self.skipTest("No PCI DRM devices available")
        result = self.run_probe(",".join(f"0x{vendor}" for vendor in set(vendors)))
        self.assertEqual(result["direct"][:2], (0, 0))
        self.assertEqual(result["dlopen"][:2], (0, 0))


if __name__ == "__main__":
    unittest.main()
