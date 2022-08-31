"""Edit the file extensions of images"""

import os.path
import shutil

import img_utils


def rename_extension(source: str):
    files = img_utils.find_files_recursive(source, "*.jpg") + img_utils.find_files_recursive(source, "*.rw2")
    for path in files:
        filename, extension = os.path.splitext(path)
        new_path = f"{filename}{extension.upper()}"
        print(f"{path} -> {new_path}")
        shutil.move(path, new_path)


if __name__ == "__main__":
    rename_extension("SOURCE_FOLDER_HERE")
