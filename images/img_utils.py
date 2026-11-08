"""Utilities for the image scripts."""

import datetime
import pathlib

import exif


def find_files_recursive(path: str, regex: str = "*.jpg") -> list[pathlib.Path]:
    """Find files recursively.

    :param path: folder to search
    :param regex: glob pattern of the file names
    :return: paths of the found files
    """
    return list(pathlib.Path(path).rglob(regex))


def get_timestamp(img: exif.Image) -> datetime.datetime | None:
    """Get the timestamp of an image from its EXIF data.

    :param img: image
    :return: timestamp, or None if the image has no timestamp
    """
    if not img.has_exif:
        return None
    if "datetime" not in img.list_all():
        return None
    return datetime.datetime.strptime(img.datetime, "%Y:%m:%d %H:%M:%S")
