#!/usr/bin/env python3

"""
formatter for block plugin
"""

from util.util import convert_bytes
from plugins import block

block_class = block.Block()


def main():
    """
    returns the data, but formatted.
    """

    data = block_class.get_data()
    old_sectors_data = data["sectors"]

    sectors_read_diff = data["sectors"]["read"] - old_sectors_data["read"]
    sectors_write_diff = data["sectors"]["write"] - old_sectors_data["write"]

    sectors_read_speed = convert_bytes(data["sectors"]["speed"]["read"])
    sectors_read_data = convert_bytes(data["sectors"]["read"] * 512)

    output_list = [
        "  --- /sys/block --------------------------------------------------\n"
        f"    Device: {data['drive']['name'].split('/')[-1]} | Model: {data['drive']['model']}\n",
        f"   Sectors: Read: {data['sectors']['read']} | Write: {data['sectors']['write']} \ \n",
        f"     Human: Read: {sectors_read_data}{' ' * (13 - len(sectors_read_data))} | Write: {convert_bytes(data['sectors']['write'] * 512)} \ \n"
        f"     Speed: Read: {sectors_read_speed}{' ' * (13 - len(sectors_read_speed))} | Write: {convert_bytes(data['sectors']['speed']['write'])}\n"
        f"       I/O: Read: {data['io']['read']} | Write: {data['io']['write']}\n",
        # f"   Sectors speed: Read: {} | Write: {}\n",
    ]

    return "".join(output_list)


def end():
    """
    clean up when the program exits
    """

    block_class.close_files()


if __name__ == "__main__":
    main()
