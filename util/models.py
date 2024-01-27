#!/usr/bin/env python3

"""class models file for sysmon"""

import time

from dataclasses import dataclass
from datetime import datetime


@dataclass
class LoadavgDataLoadTimes:
    """
    dataclass containing load times of LoadavgData
    part of LoadavgData class
    """

    one: float
    five: float
    fifteen: float


@dataclass
class LoadavgDataEntities:
    """
    dataclass containing entities of LoadavgData
    part of LoadavgData class
    """

    active: int
    total: int


@dataclass
class LoadavgDataUptime:
    """
    dataclass containing uptimes of LoadavgData
    part of LoadavgData class
    """

    since: str
    uptime: int


class LoadavgData:
    """
    LoadavgData class - get load times, entities and uptime
    using /proc/loadavg and /proc/uptime
    """

    def __init__(self, loadavg_data, uptime_data):

        self.load_times = LoadavgDataLoadTimes(
            one=float(loadavg_data[0]),
            five=float(loadavg_data[1]),
            fifteen=float(loadavg_data[2])
        )

        self.entities = LoadavgDataEntities(
            active=int(loadavg_data[3].split("/")[0]),
            total=int(loadavg_data[3].split("/")[1])
        )

        self.uptime = LoadavgDataUptime(
            since=datetime.fromtimestamp(time.time() - uptime_data[1]).strftime(
                "%A %B %d %Y, %I:%M:%S %p"
            ),
            uptime=uptime_data[0]
        )
