"""Various functions used by Brenthy Core and `brenthy_api`."""

import pathspec
from pathlib import Path
import shutil
import platform
import stat
import importlib
import importlib.util
import os
import sys
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime, timezone
from types import ModuleType

# pylint:disable=unused-variable


TIME_FORMAT = "%Y.%m.%d_%H.%M.%S.%f"


def are_elements_unique(array: list) -> bool:
    """Check if the provided array only has unique elements."""
    # going through each element in the array
    # and comparing each to all alements in the array that follow it
    i = 0
    while i < len(array):  # for each element in the array
        j = i + 1
        while j < len(array):  # for each element in the array after array[i]
            if array[i] == array[j]:
                return False
            j = j + 1
        i = i + 1
    return True


def encode_timestamp(date_time: datetime) -> bytearray:
    """Get a timestamp encoded in bytes without [0]s."""
    if not date_time.tzinfo == timezone.utc:
        raise ValueError(
            "Ensure your datetime is time-zone aware and set to UTC"
        )
    return (
        to_b254_no_0s1s(date_time.year)
        + bytearray([1])
        + to_b254_no_0s1s(date_time.month)
        + bytearray([1])
        + to_b254_no_0s1s(date_time.day)
        + bytearray([1])
        + to_b254_no_0s1s(date_time.hour)
        + bytearray([1])
        + to_b254_no_0s1s(date_time.minute)
        + bytearray([1])
        + to_b254_no_0s1s(date_time.second)
        + bytearray([1])
        + to_b254_no_0s1s(date_time.microsecond)
    )


def decode_timestamp(array: bytearray) -> datetime:
    """Decode a bytearray timestamp back into a datetime."""
    # remove leading and trailing [0]s
    while array[0] == bytearray([0]):
        array = array[1:]
    if array[:-1] == bytearray([0]):
        array = array[:-1]

    # extract the year, month, day, hour, minute, second, and microsecond
    # from the inpur array using the [0] separators
    numbers = [from_b254_no_0s1s(n) for n in array.split(bytearray([1]))]

    return datetime(
        year=numbers[0],
        month=numbers[1],
        day=numbers[2],
        hour=numbers[3],
        minute=numbers[4],
        second=numbers[5],
        microsecond=numbers[6],
        tzinfo=timezone.utc,
    )


def time_to_string(date_time: datetime) -> str:
    """Get a string representation of a datetime."""
    if not date_time.tzinfo == timezone.utc:
        raise ValueError(
            "Ensure your datetime is time-zone aware and set to UTC"
        )
    return date_time.strftime(TIME_FORMAT)


def string_to_time(string: str) -> datetime:
    """Convert a timestamp string back to a datetime."""
    result = datetime.strptime(string, TIME_FORMAT)
    result = result.replace(tzinfo=timezone.utc)
    return result


def to_b255_no_0s(number: int) -> bytearray:
    """Encode an integer into bytearray that doesn't have any [0]s.

    E.g 0 is encoded to [1], 1 is encoded to [2], 255 is encoded to [2,1]

    Args:
        number(int): the integer value to encode
    Returns:
        bytearray: the input number encoded as a bytearray without 0s or 1s
    """
    if not isinstance(number, int):
        raise TypeError(f"number must be of type int, not {type(number)}")
    if number == 0:
        return bytearray([1])
    array = bytearray([])
    while number > 0:
        # modulus + 1 in order to get a range of possible values from 1-256
        # instead of 0-255
        array.insert(0, int(number % 255 + 1))
        number -= number % 255
        number = number // 255
    return array


def from_b255_no_0s(array: bytearray | bytes) -> int:
    """Decode data encoded with to_b255_no_0s back to the original integer.

    Args:
        array (bytearray): the encoded data to decode
    Returns:
        int: the decoded value
    """
    if not isinstance(array, (bytearray | bytes)):
        raise TypeError(f"array must be of type array, not {type(array)}")
    number = 0
    order = 1
    # for loop backwards through th ebytes in array
    i = len(array) - 1  # th eindex of the last byte in the array
    while i >= 0:
        # byte - 1 to change the range from 1-266 to 0-255
        number = number + (array[i] - 1) * order
        order = order * 255
        i = i - 1
    return number


def to_b254_no_0s1s(number: int) -> bytearray:
    """Encode the input integer into a bytearray without any [0] or [1]s.

    E.g 0 is encoded to [2], 1 is encoded to [3], 254 is encoded to [3,2]

    Args:
        number (int): the integer value to encode
    Returns:
        bytearray: the input number encoded as a bytearray without 0s or 1s
    """
    if number == 0:
        return bytearray([2])
    data = bytearray([])
    while number > 0:
        # modulus + 2 in order to get a range of possible values
        # from 2-256 instead of 0-254
        data.insert(0, int(number % 254 + 2))
        number -= number % 254
        number = number // 254
    return data


def from_b254_no_0s1s(data: bytearray) -> int:
    """Decode an integer encoded with to_b254_no_0s1s.

    Args:
        data (bytearray): the encoded data to decode
    Returns:
        int: the decoded value
    """
    number = 0
    order = 1
    # for loop backwards through th ebytes in data
    i = len(data) - 1  # th eindex of the last byte in the data
    while i >= 0:
        # byte - 1 to change the range from 1-266 to 0-254
        number = number + (data[i] - 2) * order
        order = order * 254
        i = i - 1
    return number


def bytes_to_b255_no_0s(data: bytearray | bytes) -> bytearray:
    """Encode a bytearray into a bytearray without [0]s."""
    number = int.from_bytes(data, byteorder="little")  # convert to int
    result = to_b255_no_0s(number)
    return result


def bytes_from_b255_no_0s(data: bytearray | bytes) -> bytearray:
    """Decode a byetarray encoded with bytes_to_b255_no_0s."""
    number = from_b255_no_0s(data)
    byte_length = (number.bit_length() + 7) // 8
    result = bytearray(number.to_bytes(byte_length, byteorder="little"))
    return result


def print_bytearray(data: bytearray) -> None:
    """Print a bytearray as a list of each integer."""
    print(printable_bytearray(data))


def printable_bytearray(data: bytearray | bytes) -> str:
    """Convert a bytearray into a string listing each integer in the array."""
    return str(list(data))


def string_to_bytes(data: str) -> bytearray:
    """Decode URL-Safe multibase encoded bytes.

    Required by some functions (since IFPS v0.11.0).
    """
    if not isinstance(data, str):
        raise ValueError(
            f"Parameter data must be of type str, not {type(data)}"
        )
    if data == "":
        return bytearray([])
    data_b = data.encode()
    missing_padding = (len(data_b)) % 4
    if missing_padding:
        data_b += b"=" * (4 - missing_padding)
    return bytearray(urlsafe_b64decode(data_b))


def bytes_to_string(data: bytearray) -> str:
    """Encode bytes into string using URL-Safe multibase encoding with padding.

    Required by some functions (since IFPS v0.11.0).
    """
    if not isinstance(data, (bytearray, bytes)):
        raise ValueError(
            "Parameter data must be of type bytearray or bytes, not "
            f"{type(data)}"
        )
    if len(data) == 0:
        return ""
    data_str = urlsafe_b64encode(data)
    while data_str[-1] == 61 and data_str[-1]:
        data_str = data_str[:-1]
    return data_str.decode()


def load_module_from_path(path: str) -> ModuleType:
    """Load a python module given its path."""
    module_name = os.path.basename(path).strip(".py")
    if os.path.isdir(path):
        path = os.path.join(path, "__init__.py")
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def function_name(parents: int = 0) -> str:
    """Get the name of the calling function."""
    # pylint:disable=protected-access
    return sys._getframe(1 + parents).f_code.co_name


def make_file_readable(file_path: str) -> None:
    """Make a file readable to all the operating system's users."""
    if platform.system() in ["Linux", "Darwin"]:  # Unix-based systems
        os.chmod(file_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    elif platform.system() == "Windows":
        os.chmod(file_path, 0o444)
    else:
        raise NotImplementedError(f"Unsupported platform: {platform.system()}")


def make_directory_readable(directory_path: str) -> None:
    """Make a directory readable to all the operating system's users."""
    if platform.system() in ["Linux", "Darwin"]:  # Unix-based systems
        os.chmod(
            directory_path,
            stat.S_IRUSR
            | stat.S_IXUSR
            | stat.S_IRGRP
            | stat.S_IXGRP
            | stat.S_IROTH
            | stat.S_IXOTH,
        )
    elif platform.system() == "Windows":
        os.chmod(directory_path, 0o555)
    else:
        raise NotImplementedError(f"Unsupported platform: {platform.system()}")


def _find_tree_matches(spec: pathspec.GitIgnoreSpec, dir: str):
    """Recursively traverse a file tree finding files or folders that match the spec.

    Doesn't traverse already ignored folders.
    """
    ignored_paths = []
    for name in os.listdir(dir):
        full_path = os.path.join(dir, name)
        if spec.match_file(name):
            ignored_paths.append(full_path)
        else:
            if os.path.isdir(full_path):
                ignored_paths += _find_tree_matches(spec, full_path)
    return ignored_paths


def clean_directory(
    root_dir: str,
    patterns: list[str],
):
    """
    Given a directory and gitignore-style patterns, find and delete matches.
    """
    root = Path(root_dir).resolve()
    spec = pathspec.GitIgnoreSpec.from_lines(patterns)

    root = root.resolve()
    matches = _find_tree_matches(spec, root)
    matches = [root.joinpath(p).resolve() for p in matches]

    for p in matches:
        if p.is_dir() and not p.is_symlink():
            shutil.rmtree(p)
        else:
            p.unlink(missing_ok=True)
