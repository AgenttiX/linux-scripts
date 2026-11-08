"""Copy images from a certain time range to another folder."""

import datetime
import pathlib
import shutil

import exif
import img_utils


def filter_by_timeframe(
        files: list[pathlib.Path],
        start: datetime.datetime,
        end: datetime.datetime) -> list[pathlib.Path]:
    """Filter images by their EXIF timestamp.

    Images without a timestamp are skipped.

    :param files: paths of the images
    :param start: start of the time range (exclusive)
    :param end: end of the time range (exclusive)
    :return: paths of the images within the time range
    """
    filtered: list[pathlib.Path] = []
    count = len(files)
    for i, path in enumerate(files):
        with open(path, "rb") as file:
            img = exif.Image(file)
            dt = img_utils.get_timestamp(img)
            if dt is not None and start < dt < end:
                print(f"Match ({i}/{count}):", path)
                filtered.append(path)
    return filtered


def copy_timeframe(source: str, target: str, start: datetime.datetime, end: datetime.datetime) -> None:
    """Copy images within a time range to another folder.

    :param source: source folder, which is searched recursively
    :param target: target folder
    :param start: start of the time range (exclusive)
    :param end: end of the time range (exclusive)
    """
    files = img_utils.find_files_recursive(source, "*.jpg") + img_utils.find_files_recursive(source, "*.rw2")
    filtered = filter_by_timeframe(files, start, end)
    count = len(filtered)
    for i, path in enumerate(filtered):
        print(f"Copying {i}/{count}:", path)
        shutil.copy(path, target)


def main() -> None:
    """Copy the images of the configured time range."""
    copy_timeframe(
        source="SOURCE_FOLDER_HERE",
        target="TARGET_FOLDER_HERE",
        start=datetime.datetime(year=2022, month=7, day=1, hour=0, minute=0, second=0),
        end=datetime.datetime(year=2022, month=7, day=10, hour=0, minute=0, second=0)
    )


if __name__ == "__main__":
    main()
