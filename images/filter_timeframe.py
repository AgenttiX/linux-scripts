"""Copy images from a certain time range to another folder"""

import datetime
import shutil

import exif

import img_utils


def filter_by_timeframe(files: list, start: datetime.datetime, end: datetime.datetime) -> list:
    filtered = []
    count = len(files)
    for i, path in enumerate(files):
        with open(path, "rb") as file:
            img = exif.Image(file)
            dt = img_utils.get_timestamp(img)
            if start < dt < end:
                print(f"Match ({i}/{count}):", path)
                filtered.append(path)
    return filtered


def copy_timeframe(source: str, target: str, start: datetime.datetime, end: datetime.datetime):
    files = img_utils.find_files_recursive(source, "*.jpg") + img_utils.find_files_recursive(source, "*.rw2")
    filtered = filter_by_timeframe(files, start, end)
    count = len(filtered)
    for i, path in enumerate(filtered):
        print(f"Copying {i}/{count}:", path)
        shutil.copy(path, target)


def main():
    copy_timeframe(
        source="SOURCE_FOLDER_HERE",
        target="TARGET_FOLDER_HERE",
        start=datetime.datetime(year=2022, month=7, day=1, hour=0, minute=0, second=0),
        end=datetime.datetime(year=2022, month=7, day=10, hour=0, minute=0, second=0)
    )


if __name__ == "__main__":
    main()
