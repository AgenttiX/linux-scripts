"""Rename images by their timestamp."""

import os.path
import shutil

import exif
import img_utils


def rename_by_time(source: str, target: str) -> None:
    """Copy images to another folder and name them by their timestamp.

    Images without a timestamp are skipped.

    :param source: source folder, which is searched recursively
    :param target: target folder
    :raises FileExistsError: if there are too many images with the same timestamp
    """
    files = img_utils.find_files_recursive(source, "*.jpg") + img_utils.find_files_recursive(source, "*.rw2")
    count = len(files)

    for i, path in enumerate(files):
        with open(path, "rb") as file:
            img = exif.Image(file)
            ts = img_utils.get_timestamp(img)
            if ts is None:
                continue
            time_str = ts.strftime("%Y-%m-%d_%H-%M-%S")
            _, extension = os.path.splitext(path)
            name = f"{time_str}{extension}"
            new_path = os.path.join(target, name)
            if os.path.exists(new_path):
                print("Several images on one second! Finding a free name.")
                for j in range(2, 10):
                    name = f"{time_str}_{j}{extension}"
                    new_path = os.path.join(target, name)
                    if not os.path.exists(new_path):
                        break
                else:
                    raise FileExistsError("Too many files on the same second")
            print(f"Copying image {i}/{count}: {os.path.basename(path)} -> {name}")
            shutil.copy(path, new_path)


if __name__ == "__main__":
    rename_by_time(
        source="SOURCE_FOLDER_HERE",
        target="TARGET_FOLDER_HERE"
    )
