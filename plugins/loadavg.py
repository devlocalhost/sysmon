#!/usr/bin/env python3

"""loadavg plugin for sysmon"""

import time
import sys

from datetime import datetime
from util.util import en_open


def uptime_format():
    """format the uptime from seconds to a human readable format"""

    intervals = (("week", 604800), ("day", 86400), ("hour", 3600), ("minute", 60))
    result = []

    with en_open("/proc/uptime") as uptime_file:
        seconds = int(float(uptime_file.readline().split()[0]))

    original_seconds = seconds

    if seconds < 60:
        return f"{seconds} seconds", original_seconds

    for time_type, count in intervals:
        value = seconds // count

        if value:
            seconds -= value * count
            result.append(f"{value} {time_type if value == 1 else time_type + 's'}")

    if len(result) > 1:
        result[-1] = "and " + result[-1]

    return (", ".join(result), original_seconds)


def main():
    """/proc/loadavg - system load times and uptime"""

    try:
        with en_open("/proc/loadavg") as loadavg_file:
            loadavg_data = loadavg_file.read().split()
            onemin, fivemin, fiveteenmin = loadavg_data[:3]
            entities_active, entities_total = loadavg_data[3].split("/")

            uptime_func_out = uptime_format()

            up_since_fmt = datetime.fromtimestamp(
                time.time() - uptime_func_out[1]
            ).strftime("%A %B %d %Y, %I:%M:%S %p")

        return (
            f"  ——— /proc/loadavg {'—' * 47}\n"
            f"     Load: {onemin}, {fivemin}, {fiveteenmin}"
            f"{' ':<6}| Procs: {entities_active} executing, {entities_total} total"
            f"\n   Uptime: {uptime_func_out[0]}\n   Booted: {up_since_fmt}\n"
        )

    except FileNotFoundError:
        sys.exit("Couldn't find /proc/loadavg file")

    except PermissionError:
        sys.exit(
            "Couldn't read the file. Do you have read permissions for /proc/loadavg file?"
        )
