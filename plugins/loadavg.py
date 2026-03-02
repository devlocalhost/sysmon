#!/usr/bin/env python3

"""loadavg plugin for sysmon"""

import time

from datetime import datetime

from dataclasses import dataclass

from plugins.base import BasePlugin
from utils.util import en_open

@dataclass
class LoadTimes:
    OneMin: int = 0
    FiveMin: int = 0
    FifteenMin: int = 0

@dataclass
class Entities:
    Active: int = 0
    Total: int = 0

@dataclass
class Uptime:
    Timestamp: int = 0
    Seconds: int = 0

@dataclass
class LoadavgData:
    load_times: LoadTimes = None
    entities: Entities = None
    uptime: Uptime = None


class LoadavgPlugin(BasePlugin):
    def __init__(self):
        super().__init__()

        self.logger.debug("initialize plugin")

        try:
            self.loadavg_file = en_open("/proc/loadavg")
            self.logger.debug("opened file /proc/loadavg")
            self.opened_files.append(self.loadavg_file)

            self.uptime_file = en_open("/proc/uptime")
            self.logger.debug("opened file /proc/uptime")
            self.opened_files.append(self.uptime_file)

        except Exception as exc:
            self.logger.error(f"error opening file: {exc}")

    def get_data(self):
        self.seek_files()

        loadavg_file_data = self.loadavg_file.read().split()

        uptime_seconds = int(float(self.uptime_file.readline().split()[0]))
        uptime_timestamp = time.time() - uptime_seconds

        data = LoadavgData(
            load_times=LoadTimes(
                OneMin=float(loadavg_file_data[0]),
                FiveMin=float(loadavg_file_data[1]),
                FifteenMin=float(loadavg_file_data[2])
            ),
            entities=Entities(
                Active=int(loadavg_file_data[3].split("/")[0]),
                Total=int(loadavg_file_data[3].split("/")[1])
            ),
            uptime=Uptime(
                Timestamp=uptime_timestamp,
                Seconds=uptime_seconds
            ),
        )

        return data
