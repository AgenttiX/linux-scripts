"""Utilities for the image scripts"""

import datetime
import pathlib
import typing as tp

import exif


def find_files_recursive(path: str, regex: str = "*.jpg") -> tp.List[pathlib.Path]:
    return list(pathlib.Path(path).rglob(regex))


def get_timestamp(img: exif.Image) -> tp.Optional[datetime.datetime]:
    if not img.has_exif:
        return None
    if "datetime" not in img.list_all():
        return None
    return datetime.datetime.strptime(img.datetime, "%Y:%m:%d %H:%M:%S")
