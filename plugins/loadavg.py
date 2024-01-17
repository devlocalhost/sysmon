#!/usr/bin/env python3

"""loadavg plugin for sysmon"""

import logging
import time
import sys

from datetime import datetime
from util.util import en_open
from util.logger import setup_logger


# TODO: put function in the class maybe?
def get_uptime(file):
    """format the uptime from seconds to a human readable format"""

    intervals = (("week", 604800), ("day", 86400), ("hour", 3600), ("minute", 60))
    result = []

    file.seek(0)

    seconds = int(float(file.readline().split()[0]))
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


class Loadavg:
    def __init__(self):
        """
        initializing important stuff
        """

        self.logger = setup_logger(__name__)

        self.logger.debug("[init] initializing")

        self.loadavg_file = en_open("/proc/loadavg")
        self.logger.debug("[open] /proc/loadavg")

        self.uptime_file = en_open("/proc/uptime")
        self.logger.debug("[open] /proc/uptime")

        self.files_opened = [self.loadavg_file, self.uptime_file]

    def close_files(self):
        """
        closing the opened files. always call this
        when ending the program
        """

        for file in self.files_opened:
            self.logger.debug(f"[close] {file.name}")
            file.close()

    def get_data(self):
        """
        returns a json dict with data
        """

        for file in self.files_opened:
            file.seek(0)

        loadavg_data = self.loadavg_file.read().split()
        uptime_data = get_uptime(self.uptime_file)

        data = {
            "load_times": {
                "1": loadavg_data[0],
                "5": loadavg_data[1],
                "15": loadavg_data[2],
            },
            "entities": {
                "active": loadavg_data[3].split("/")[0],
                "total": loadavg_data[3].split("/")[1],
            },
            "uptime": {
                "since": datetime.fromtimestamp(time.time() - uptime_data[1]).strftime("%A %B %d %Y, %I:%M:%S %p"),
                "uptime": uptime_data[0],
            },
        }

        self.logger.debug("[get_data] return data")

        return data

    def print_data(self):
        """
        returns the data, but formatted.
        not intended to be used, please
        use get_data() instead
        """

        self.logger.debug("[data] print out")
        data = self.get_data()

        return (
            f"  ——— /proc/loadavg {'—' * 47}\n"
            f"     Load: {data['load_times']['1']}, {data['load_times']['5']}, {data['load_times']['15']}"
            f"{' ':<6}| Procs: {data['entities']['active']} active, {data['entities']['total']} total"
            f"\n   Uptime: {data['uptime']['uptime']}\n   Booted: {data['uptime']['since']}\n"
        )

def main():
    """/proc/loadavg - system load times and uptime"""

    loadavg_data = file.read().split()
    onemin, fivemin, fiveteenmin = loadavg_data[:3]
    entities_active, entities_total = loadavg_data[3].split("/")

    uptime_func_out = uptime_format()

    up_since_fmt = datetime.fromtimestamp(time.time() - uptime_func_out[1]).strftime("%A %B %d %Y, %I:%M:%S %p")

    file.seek(0)
    logger.debug("[seek] /proc/loadavv")

    logger.debug("[data] print out")

    return (
        f"  ——— /proc/loadavg {'—' * 47}\n"
        f"     Load: {onemin}, {fivemin}, {fiveteenmin}"
        f"{' ':<6}| Procs: {entities_active} executing, {entities_total} total"
        f"\n   Uptime: {uptime_func_out[0]}\n   Booted: {up_since_fmt}\n"
    )
