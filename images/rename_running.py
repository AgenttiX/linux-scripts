"""Rename images with a running numbero"""

import os.path
import shutil

import img_utils


def rename_running_number(source: str, target: str, prefix: str, start: int):
    files = sorted(img_utils.find_files_recursive(source, "*.jpg"))
    count = len(files)
    for i, path in enumerate(files):
        print(f"Copying image {i}/{count}")
        shutil.copy(path, os.path.join(target, f"{prefix}{start + i}.jpg"))
        filename, _ = os.path.splitext(path)
        shutil.copy(f"{filename}.rw2", os.path.join(target, f"{prefix}{start + i}.rw2"))


if __name__ == "__main__":
    rename_running_number(
        source="SOURCE_FOLDER_HERE",
        target="TARGET_FOLDER_HERE",
        prefix="P",
        start=1210001
    )
