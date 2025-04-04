#!/usr/bin/env python3

"""loadavg plugin for sysmon"""

import time

from datetime import datetime
from nsysmon.util.util import en_open
from nsysmon.util.logger import setup_logger


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
        self.logger.debug("[init] /proc/loadavg")

        self.uptime_file = en_open("/proc/uptime")
        self.logger.debug("[init] /proc/uptime")

        self.files_opened = [self.loadavg_file, self.uptime_file]

    def close_files(self):
        """
        closing the opened files. always call this
        when ending the program
        """

        for file in self.files_opened:
            try:
                self.logger.debug(f"[close_files] {file.name}")
                file.close()

            except:
                pass

    def get_data(self):
        """
        returns a json dict with data
        """

        for file in self.files_opened:
            self.logger.debug(f"[get_data] {file.name}")
            file.seek(0)

        loadavg_data = self.loadavg_file.read().split()

        uptime_seconds = int(float(self.uptime_file.readline().split()[0]))
        uptime_timestamp = time.time() - uptime_seconds

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
                "timestamp": uptime_timestamp,
                "seconds": uptime_seconds,
            },
        }

        self.logger.debug("[get_data] return data")

        return data
