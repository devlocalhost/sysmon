#!/usr/bin/env python3

"""loadavg plugin for sysmon"""

import time
import sys

from datetime import datetime
from util.util import en_open, uptime_format


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
            f"  --- /proc/loadavg {'-' * 47}\n"
            f"   System load: {onemin}, {fivemin}, {fiveteenmin} (1, 5, 15 mins)\n"
            f"      Entities: {entities_active} executing, {entities_total} total"
            f"\n\n   System up for {uptime_func_out[0]}\n    Since {up_since_fmt}\n"
        )

    except FileNotFoundError:
        sys.exit("Couldn't find /proc/loadavg file")

    except PermissionError:
        sys.exit(
            "Couldn't read the file. Do you have read permissions for /proc/loadavg file?"
        )
