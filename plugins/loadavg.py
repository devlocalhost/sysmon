#!/usr/bin/env python3

"""loadavg plugin for sysmon"""

import time

from datetime import datetime
from util.util import en_open
from util.logger import setup_logger


# TODO: put function in the class maybe?
def get_uptime(file):
    """format the uptime from seconds to a human readable format"""

    intervals = (("week", 604800), ("day", 86400), ("hour", 3600), ("minute", 60))
    result = []

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
    """
    Loadavg class - get load times and uptime

    Usage:
        call get_data() to get data
            returns dict

    DO:
        NOT CALL print_data(). That function
    is intended to be used by sysmon. (might change in the future...?)
        CALL close_files() when your program ends
        to avoid opened files
    """

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
            try:
                self.logger.debug(f"[close] {file.name}")
                file.close()

            except:
                pass

    def get_data(self):
        """
        returns a json dict with data
        """

        for file in self.files_opened:
            self.logger.debug(f"[seek] {file.name}")
            file.seek(0)

        loadavg_data = self.loadavg_file.read().split()
        uptime_data = get_uptime(self.uptime_file)

        data = {
            "load_times": {
                "1": float(loadavg_data[0]),
                "5": float(loadavg_data[1]),
                "15": float(loadavg_data[2]),
            },
            "entities": {
                "active": int(loadavg_data[3].split("/")[0]),
                "total": int(loadavg_data[3].split("/")[1]),
            },
            "uptime": {
                "since": datetime.fromtimestamp(time.time() - uptime_data[1]).strftime(
                    "%A %B %d %Y, %I:%M:%S %p"
                ),
                "uptime": uptime_data[0],
            },
        }

        self.logger.debug("[get_data] return data")

        return data
