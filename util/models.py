#!/usr/bin/env python3

"""class models file for sysmon"""

import time

from dataclasses import dataclass
from datetime import datetime


# loadavg dataclasses


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


# meminfo dataclasses

@dataclass
class MeminfoDataVirtualValues:
    """
    dataclass containing virtual memory values
    part of MeminfoData class
    """

    total: int
    used: int
    available: int
    cached: int


@dataclass
class MeminfoDataVirtualPercentage:
    """
    dataclass containing virtual memory percentage data
    part of MeminfoData class
    """

    used: int
    available: int


@dataclass
class MeminfoDataPyhsicalValues(MeminfoDataVirtualValues):
    """
    dataclass containing physical memory values
    part of MeminfoData class
    """

    actual_used: int
    free: int


@dataclass
class MeminfoDataPyhsicalPercentage(MeminfoDataVirtualPercentage):
    """
    dataclass containing physical memory percentage data
    part of MeminfoData class
    """

    free: int
    actual_used: int


@dataclass
class MeminfoDataPyhsical:
    """
    dataclass containing physical memory data
    part of MeminfoData class
    """

    values: MeminfoDataPyhsicalValues
    percentage: MeminfoDataPyhsicalPercentage


@dataclass
class MeminfoDataVirtual:
    """
    dataclass containing virtual memory data
    part of MeminfoData class
    """

    values: MeminfoDataVirtualValues
    percentage: MeminfoDataVirtualPercentage


class MeminfoData:
    """
    MeminfoData class - get physical and virtual memory data
    using /proc/meminfo
    """

    def __init__(self, meminfo_data: dict):
        phy_memory_total = meminfo_data.get("MemTotal", 0)
        phy_memory_available = meminfo_data.get("MemAvailable", 0)
        phy_memory_free = meminfo_data.get("MemFree", 0)

        phy_memory_raw_cached = meminfo_data.get("Cached", 0)
        phy_memory_sreclaimable = meminfo_data.get("SReclaimable", 0)
        phy_memory_buffers = meminfo_data.get("Buffers", 0)

        phy_memory_cached = (
            phy_memory_raw_cached + phy_memory_buffers + phy_memory_sreclaimable
        )
        phy_memory_actual_used = round(
            phy_memory_total
            - phy_memory_free
            - phy_memory_buffers
            - phy_memory_raw_cached
            - phy_memory_sreclaimable
        )
        phy_memory_used = round(phy_memory_total - phy_memory_available)
        phy_memory_used_percent = round(
            (int(phy_memory_used) / int(phy_memory_total)) * 100, 1
        )

        swap_memory_total = meminfo_data.get("SwapTotal", 0)
        swap_memory_available = meminfo_data.get("SwapFree", 0)
        # NOTE: Swap available (in output) = this.
        # NOTE: Rename to Free instead?

        swap_memory_cached = meminfo_data.get("SwapCached", 0)
        swap_memory_used = round(swap_memory_total - swap_memory_available)

        swap_memory_used_percent = round(
            (int(swap_memory_used) / int(swap_memory_total)) * 100, 1
        )

        self.physical = MeminfoDataPyhsical(
            values=MeminfoDataPyhsicalValues(
                total=phy_memory_total,
                used=phy_memory_used,
                actual_used=phy_memory_actual_used,
                available=phy_memory_available,
                free=phy_memory_free,
                cached=phy_memory_cached,
            ),
            percentage=MeminfoDataPyhsicalPercentage(
                used=phy_memory_used_percent,
                actual_used=round(
                    (int(phy_memory_actual_used) / int(phy_memory_total)) * 100, 1
                ),
                available=round(100 - phy_memory_used_percent, 1),
                free=round(
                    (int(phy_memory_free) / int(phy_memory_total)) * 100, 1
                ),
            ),
        )

        self.virtual = MeminfoDataVirtual(
            values=MeminfoDataVirtualValues(
                total=swap_memory_total,
                used=swap_memory_used,
                available=swap_memory_available,
                cached=swap_memory_cached,
            ),
            percentage=MeminfoDataVirtualPercentage(
                used=swap_memory_used_percent,
                available=round(100 - swap_memory_used_percent, 1),
            ),
        )
