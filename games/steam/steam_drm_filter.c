/*
 * LD_PRELOAD library that hides GPUs of the given PCI vendors from libdrm device enumeration.
 *
 * Steam's PipeWire desktop capture uses the first device returned by drmGetDevices2().
 * On multi-GPU systems this may be a GPU that is not running the desktop,
 * which breaks DMA-BUF capture and forces a slow CPU copy of every frame.
 *
 * Steam loads libdrm with dlopen("libdrm.so.2") and resolves the functions with dlsym().
 * Therefore this library also intercepts dlopen() for libdrm and returns a handle to itself.
 * dlsym() on that handle finds the filtered functions here, and all other libdrm functions
 * from libdrm, which this library depends on.
 *
 * Usage:
 *   AGX_DRM_HIDE_VENDORS=0x1002 LD_PRELOAD=/path/to/libagx-drm-filter.so steam
 *
 * AGX_DRM_HIDE_VENDORS is a comma-separated list of PCI vendor IDs, e.g. 0x1002 (AMD), 0x8086 (Intel).
 * If it is unset or empty, this library does nothing.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <xf86drm.h>

#define ENV_HIDE_VENDORS "AGX_DRM_HIDE_VENDORS"
#define MAX_HIDDEN_VENDORS 16

typedef void *(*dlopen_fn)(const char *, int);
typedef int (*get_devices2_fn)(uint32_t, drmDevicePtr[], int);

static int is_hidden(const drmDevicePtr device) {
    const char *env = getenv(ENV_HIDE_VENDORS);
    if (env == NULL || device == NULL || device->bustype != DRM_BUS_PCI || device->deviceinfo.pci == NULL) {
        return 0;
    }
    const char *pos = env;
    for (int i = 0; i < MAX_HIDDEN_VENDORS && *pos != '\0'; ++i) {
        char *end = NULL;
        const unsigned long vendor = strtoul(pos, &end, 16);
        if (end == pos) {
            break;
        }
        if (vendor == device->deviceinfo.pci->vendor_id) {
            return 1;
        }
        pos = (*end == ',') ? end + 1 : end;
    }
    return 0;
}

static int hiding_enabled(void) {
    const char *env = getenv(ENV_HIDE_VENDORS);
    return env != NULL && *env != '\0';
}

static int is_libdrm(const char *filename) {
    if (filename == NULL) {
        return 0;
    }
    const char *base = strrchr(filename, '/');
    base = (base == NULL) ? filename : base + 1;
    return strcmp(base, "libdrm.so.2") == 0 || strcmp(base, "libdrm.so") == 0;
}

void *dlopen(const char *filename, int flags) {
    static dlopen_fn real_dlopen = NULL;
    if (real_dlopen == NULL) {
        real_dlopen = (dlopen_fn)dlsym(RTLD_NEXT, "dlopen");
        if (real_dlopen == NULL) {
            return NULL;
        }
    }
    if (hiding_enabled() && is_libdrm(filename)) {
        Dl_info info;
        if (dladdr((void *)&drmGetDevices2, &info) != 0 && info.dli_fname != NULL) {
            void *self = real_dlopen(info.dli_fname, flags);
            if (self != NULL) {
                return self;
            }
        }
    }
    return real_dlopen(filename, flags);
}

int drmGetDevices2(uint32_t flags, drmDevicePtr devices[], int max_devices) {
    static get_devices2_fn real_get_devices2 = NULL;
    if (real_get_devices2 == NULL) {
        real_get_devices2 = (get_devices2_fn)dlsym(RTLD_NEXT, "drmGetDevices2");
        if (real_get_devices2 == NULL) {
            return -1;
        }
    }
    if (!hiding_enabled()) {
        return real_get_devices2(flags, devices, max_devices);
    }

    const int total = real_get_devices2(flags, NULL, 0);
    if (total <= 0) {
        return total;
    }
    drmDevicePtr *all = calloc((size_t)total, sizeof(drmDevicePtr));
    if (all == NULL) {
        return -1;
    }
    const int found = real_get_devices2(flags, all, total);
    if (found < 0) {
        free(all);
        return found;
    }

    int kept = 0;
    for (int i = 0; i < found; ++i) {
        if (is_hidden(all[i])) {
            drmFreeDevice(&all[i]);
            continue;
        }
        if (devices != NULL && kept < max_devices) {
            devices[kept] = all[i];
        } else {
            drmFreeDevice(&all[i]);
        }
        ++kept;
    }
    free(all);
    if (devices != NULL && kept > max_devices) {
        return max_devices;
    }
    return kept;
}

int drmGetDevices(drmDevicePtr devices[], int max_devices) {
    return drmGetDevices2(DRM_DEVICE_GET_PCI_REVISION, devices, max_devices);
}
