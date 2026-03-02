from dataclasses import dataclass

from plugins.base import BasePlugin
from utils.util import en_open

@dataclass
class PhysicalValues:
    MemTotal: int = 0
    MemAvailable: int = 0
    MemFree: int = 0
    Cached: int = 0
    AltCached: int = 0
    SReclaimable: int = 0
    Buffers: int = 0
    Used: int = 0
    ActualUsed: int = 0

@dataclass
class VirtualValues:
    SwapTotal: int = 0
    SwapFree: int = 0
    SwapCached: int = 0
    Used: int = 0

@dataclass
class PercentageValues:
    Used: int = 0
    ActualUsed: int = 0
    Available: int = 0
    Free: int = 0
    Cached: int = 0

@dataclass
class MeminfoData:
    physical: PhysicalValues = None
    virtual: VirtualValues = None
    percentages: PercentageValues = None
    

class MeminfoPlugin(BasePlugin):
    def __init__(self):
        super().__init__()

        self.logger.debug("initialize plugin")

        try:
            self.meminfo_file = en_open("/proc/meminfo")
            self.opened_files.append(meminfo_file)

            self.logger.debug(f"opened file {meminfo_file.name}")

        except Exception as exc:
            self.logger.error(f"error opening file: {exc}")

    def get_data(self):
        for file in self.opened_files:
            self.logger.debug(f"seeking {file.name}")
            file.seek(0)

            
        meminfo_file_data = dict(
            (i.split()[0].rstrip(":"), int(i.split()[1]) * 1024)
            for i in self.meminfo_file.readlines()
        )

        phy_memory_total = meminfo_file_data.get("MemTotal", 0)
        phy_memory_available = meminfo_file_data.get("MemAvailable", 0)
        phy_memory_free = meminfo_file_data.get("MemFree", 0)

        phy_memory_raw_cached = meminfo_file_data.get("Cached", 0)
        phy_memory_sreclaimable = meminfo_file_data.get("SReclaimable", 0)
        phy_memory_buffers = meminfo_file_data.get("Buffers", 0)

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
        # phy_memory_used_percent = round(
        #     (int(phy_memory_used) / int(phy_memory_total)) * 100, 1
        # )

        # swap_memory_total = meminfo_file_data.get("SwapTotal", 0)
        # swap_memory_free = meminfo_file_data.get("SwapFree", 0)

        # swap_memory_cached = meminfo_file_data.get("SwapCached", 0)
        # swap_memory_used = round(swap_memory_total - swap_memory_free)

        # try:
        #     swap_memory_used_percent = round(
        #         (int(swap_memory_used) / int(swap_memory_total)) * 100, 1
        #     )  # TODO: fix ZeroDivisionError

        # except ZeroDivisionError:
        #     swap_memory_used_percent = 0

        data = MeminfoData(
            physical=PhysicalValues(
                MemTotal=phy_memory_total,
                MemAvailable=phy_memory_available,
                MemFree=phy_memory_free,
                Cached=phy_memory_raw_cached,
                AltCached=phy_memory_cached,
                SReclaimable=phy_memory_sreclaimable,
                Buffers=phy_memory_buffers,
                Used=phy_memory_used,
                ActualUsed=phy_memory_actual_used,
            )
        )
        
        return data
