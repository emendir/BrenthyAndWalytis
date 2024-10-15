"""Utilities for processing blockchain version codes."""

from .utils import from_b254_no_0s1s, to_b254_no_0s1s

# pylint:disable=unused-variable


def encode_version(version: list | tuple) -> bytearray:
    """Encode tuple version identifier into a bytearray with no [0] elements.

    Args:
        version (list): a list of integers that designate a blockchain version
    Returns:
        bytearray: the encoded version identifier, with no [0]s
    """
    if not isinstance(version, (list, tuple)):
        raise TypeError

    # string together the encoded numbers separated by [1]
    data = bytearray([])
    for number in version:
        data += to_b254_no_0s1s(number) + bytearray([1])
    return data


def decode_version(data: bytearray) -> tuple:
    """Decode bytearray version identifiers encoded by encode_version().

    Parameter:
        bytearray data: the the encoded version identifier
    Returns:
    list version: the decoded version identifier (as an array of integers)
    """
    if not isinstance(data, (bytearray, bytes)):
        raise TypeError

    # split the data up into the encoded number by splitting at [1]
    numbers = []
    while len(data) > 0:
        numbers.append(data[: data.index(1)])
        data = data[data.index(1) + 1:]

    # decode the numbers
    return tuple(from_b254_no_0s1s(number) for number in numbers)


def is_version_greater(
    version_1: list | tuple, version_2: list | tuple
) -> bool:
    """Check whether or not the first is a higher version than the second.

    Returns:
        bool result: whether or not the first version is higher than the second
    """
    # trimming away leading [0]s

    while version_1[0] == 0:
        version_1 = version_1[1:]
    while version_2[0] == 0:
        version_2 = version_2[1:]

    # version array length comparison
    if len(version_1) > len(version_2):
        return True
    if len(version_2) > len(version_1):
        return False

    # at this point both version arrays have the same number of elements
    for i, _ in enumerate(version_1):
        if version_1[i] > version_2[i]:
            return True
        if version_2[i] > version_1[i]:
            return False

    # versions are the same
    return False


def version_from_string(version: str) -> tuple:
    """Convert a version string to a tuple."""
    if not isinstance(version, str):
        raise TypeError
    return tuple(int(digit) for digit in version.split("."))


def version_to_string(version: tuple | list) -> str:
    """Convert a version tuple to a string."""
    if not isinstance(version, (list, tuple)):
        raise TypeError
    return ".".join([str(digit) for digit in version])
