"""
Util functions
"""
import os
import struct


def read_file(filename):
    """Read file content."""
    file = open(filename, "r+", encoding="UTF-8")
    return file.read()


def save_to_file(filename, content):
    """When the content changes, save new :content to :filename."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        file = open(filename, "r+", encoding="UTF-8")
    except FileNotFoundError as _:
        file = open(filename, "a+", encoding="UTF-8")
    if file.read() == content:
        return False
    file.seek(0)
    file.write(content)
    file.truncate()
    file.close()
    return True


def ceil_div(a, b):
    """Round up division."""
    return -1 * (-a // b)


def generate_test_data(nbytes, width=0):
    """Generate test data according to element width."""
    nquads = ceil_div(nbytes, 8)
    if width == 8:
        base_list = [
            0x000103F8FFEFEFFF,
            0x0001070001000100,
        ]
    elif width == 16:
        base_list = [
            0x000000010003FFF8,
            0x0000000100070000,
            0xFFFFEFFFEFFFFFFF,
            0x0001000000010000,
        ]
    elif width == 32:
        base_list = [
            0x0000000000000001,
            0x0000000000000001,
            0x00000003FFFFFFF8,
            0x0000000700000000,
            0xFFFFFFFFEFFFFFFF,
            0x0000000100000000,
            0xEFFFFFFFFFFFFFFF,
            0x0000000100000000,
        ]
    elif width == 64:
        base_list = [
            0x0000000000000000,
            0x0000000000000000,
            0x0000000000000001,
            0x0000000000000001,
            0x0000000000000003,
            0x0000000000000007,
            0xFFFFFFFFFFFFFFF8,
            0x0000000000000000,
            0xFFFFFFFFFFFFFFFF,
            0x0000000000000001,
            0xEFFFFFFFFFFFFFFF,
            0x0000000000000000,
            0xEFFFFFFFFFFFFFFF,
            0x0000000000000001,
            0xFFFFFFFFFFFFFFFF,
            0x0000000000000000,
        ]
    else:
        base_list = [
            0xBF8003044003B0F0,
            0x40400000C0800000,
            0xDEADBEEFCAFEBABE,
            0xABAD1DEA1337D00D,
        ]

    return [e for _ in range(ceil_div(nquads, len(base_list))) for e in base_list][
        :nquads
    ]


def generate_indexed_data(nbytes, width):
    """Generate indexed data."""
    if width == 8:
        base_list = [
            0x0706050403020100,
        ]
    elif width == 16:
        base_list = [
            0x0003000200010000,
            0x0007000600050004,
        ]
    elif width == 32:
        base_list = [
            0x0000000100000000,
            0x0000000300000002,
            0x0000000500000004,
            0x0000000700000006,
        ]
    else:
        base_list = [
            0x0000000000000000,
            0x0000000000000001,
            0x0000000000000002,
            0x0000000000000003,
            0x0000000000000004,
            0x0000000000000005,
            0x0000000000000006,
            0x0000000000000007,
        ]

    nquads = ceil_div(nbytes, 8)
    return [e for _ in range(ceil_div(nquads, len(base_list))) for e in base_list][
        :nquads
    ]


def floathex(f, width):
    """Get floating point hex representation as integer"""
    if width == 32:
        return int(hex(struct.unpack("<I", struct.pack("<f", f))[0]), 0)
    elif width == 64:
        return int(hex(struct.unpack("<Q", struct.pack("<d", f))[0]), 0)
    return 0
