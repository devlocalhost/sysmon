#!/usr/bin/env python3

"""
formatter for loadavg plugin
"""

from plugins import loadavg

loadavg_class = loadavg.Loadavg()


def main():
    """
    returns the data, but formatted.
    """

    data = loadavg_class.get_data()

    output_list = [
        f"  --- /proc/loadavg {'-' * 47}\n",
        f"     Load: {data['load_times']['1']}, {data['load_times']['5']}, {data['load_times']['15']}",
        f"\n   Uptime: {data['uptime']['uptime']}\n   Booted: {data['uptime']['since']}\n",
    ]

    output_list[1] = output_list[1] = (
        output_list[1]
        + " " * max(0, 35 - len(output_list[1]))
        + f"| Procs: {data['entities']['active']} active, {data['entities']['total']} total"
    )

    return "".join(output_list)


def end():
    """
    clean up when the program exits
    """

    loadavg_class.close_files()


if __name__ == "__main__":
    main()
