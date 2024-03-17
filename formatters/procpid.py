#!/usr/bin/env python3

"""
formatter for procpid plugin
"""

from util.util import convert_bytes
from plugins import procpid

procpid_class = procpid.Procpid()


def main():
    """
    returns the data, but formatted.
    """

    data = procpid_class.get_data()

    formatted_data = [
        f"  ——— /proc/pid/status {'—' * 44}\n   Name            PID         RSS            State"
    ]

    for proc in data["processes"]:
        vmrss_human_format = convert_bytes(proc["vmrss"])
        formatted_data.append(
            f"   {proc['name'] or '!?!?'}{' ' * (15 - len(proc['name'] or '!?!?'))}"
            f" {proc['pid']}{' ' * (11 - len(str(proc['pid'])))}"
            f" {vmrss_human_format}{' ' * (14 - len(vmrss_human_format))} {proc['state'] or '!?!?'}"
        )

    return "\n".join(formatted_data) + "\n"


if __name__ == "__main__":
    main()
