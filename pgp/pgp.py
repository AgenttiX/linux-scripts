"""Utilities for OpenPGP data.

Only the Python standard library is used, so that this can be used by scripts that are run as root.
"""

import base64

ARMOR_BEGIN = "-----BEGIN PGP PUBLIC KEY BLOCK-----"
ARMOR_END = "-----END PGP PUBLIC KEY BLOCK-----"
CRC24_INIT = 0xB704CE
CRC24_POLY = 0x1864CFB


def crc24(data: bytes) -> int:
    """Compute the CRC-24 checksum used in OpenPGP ASCII armor (RFC 9580, section 6.1).

    :param data: data to compute the checksum of
    :return: checksum
    """
    crc = CRC24_INIT
    for byte in data:
        crc ^= byte << 16
        for _ in range(8):
            crc <<= 1
            if crc & 0x1000000:
                crc ^= CRC24_POLY
    return crc & 0xFFFFFF


def dearmor(data: bytes) -> bytes:
    """Convert ASCII-armored OpenPGP public keys to the binary format, like ``gpg --dearmor``.

    :param data: ASCII-armored key data
    :return: binary key data
    :raises ValueError: if the data is not valid ASCII armor
    """
    lines = [line.strip() for line in data.decode("ascii").splitlines()]
    result = b""
    while ARMOR_BEGIN in lines:
        start = lines.index(ARMOR_BEGIN)
        try:
            end = lines.index(ARMOR_END, start)
        except ValueError as e:
            raise ValueError("The ASCII armor has no end line.") from e
        body = lines[start + 1:end]
        lines = lines[end + 1:]
        # Skip the armor headers, which are separated from the data by an empty line.
        if "" in body:
            body = body[body.index("") + 1:]
        checksum = None
        if body and body[-1].startswith("="):
            checksum = body.pop()[1:]
        decoded = base64.b64decode("".join(body), validate=True)
        if checksum is not None and base64.b64decode(checksum, validate=True) != crc24(decoded).to_bytes(3):
            raise ValueError("The ASCII armor checksum does not match.")
        result += decoded
    if not result:
        raise ValueError("No ASCII-armored public key block was found.")
    return result


def is_armored(data: bytes) -> bool:
    """Check whether the data contains an ASCII-armored OpenPGP public key block.

    :param data: key data
    :return: whether the data is ASCII-armored
    """
    return ARMOR_BEGIN.encode() in data
