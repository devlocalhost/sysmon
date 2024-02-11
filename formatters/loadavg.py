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

    return (
        f"  ——— /proc/loadavg {'—' * 47}\n"
        f"     Load: {data['load_times']['1']}, {data['load_times']['5']}, {data['load_times']['15']}"
        f"{' ':<6}| Procs: {data['entities']['active']} active, {data['entities']['total']} total"
        f"\n   Uptime: {data['uptime']['uptime']}\n   Booted: {data['uptime']['since']}\n"
    )


if __name__ == "__main__":
    main()
