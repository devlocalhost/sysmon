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
class PhysicalPercentages:
    Used: int = 0
    ActualUsed: int = 0
    Available: int = 0
    Free: int = 0
    Cached: int = 0

@dataclass
class VirtualPercentages:
    Used: int = 0
    Free: int = 0

@dataclass
class MeminfoData:
    physical_values: PhysicalValues = None
    virtual_values: VirtualValues = None
    physical_percentages: PhysicalPercentages = None
    virtual_percentages: VirtualPercentages = None
    

class MeminfoPlugin(BasePlugin):
    def __init__(self):
        super().__init__()

        self.logger.debug("initialize plugin")

        try:
            self.meminfo_file = en_open("/proc/meminfo")
            self.opened_files.append(self.meminfo_file)

            self.logger.debug(f"opened file {self.meminfo_file.name}")

        except Exception as exc:
            self.logger.error(f"error opening file: {exc}")

    def get_data(self):
        self.seek_files()
            
        meminfo_file_data = dict(
            (i.split()[0].rstrip(":"), int(i.split()[1]) * 1024)
            for i in self.meminfo_file.readlines()
        )

        # raw values section: physical
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

        # raw values sectio: virtual
        swap_memory_total = meminfo_file_data.get("SwapTotal", 0)
        swap_memory_free = meminfo_file_data.get("SwapFree", 0)

        swap_memory_cached = meminfo_file_data.get("SwapCached", 0)
        swap_memory_used = round(swap_memory_total - swap_memory_free)

        # percentages value section: physical
        phy_memory_used_percent = round(
            (int(phy_memory_used) / int(phy_memory_total)) * 100, 1
        )
        phy_memory_actual_used_percent = round(
            (int(phy_memory_actual_used) / int(phy_memory_total)) * 100, 1
        )
        phy_memory_available_percent = round(100 - phy_memory_used_percent, 1)
        phy_memory_free_percent = round(
            (int(phy_memory_free) / int(phy_memory_total)) * 100, 1
        )
        phy_memory_cached_percent = round((phy_memory_cached / phy_memory_total) * 100, 1)

        # percentages value section: virtual
        try:
            swap_memory_used_percent = round((int(swap_memory_used) / int(swap_memory_total)) * 100, 1) if swap_memory_total > 0 else 0

        except ZeroDivisionError:
            swap_memory_used_percent = 0

        swap_memory_free_percent = round(100 - swap_memory_used_percent, 1)

        data = MeminfoData(
            physical_values=PhysicalValues(
                MemTotal=phy_memory_total,
                MemAvailable=phy_memory_available,
                MemFree=phy_memory_free,
                Cached=phy_memory_raw_cached,
                AltCached=phy_memory_cached,
                SReclaimable=phy_memory_sreclaimable,
                Buffers=phy_memory_buffers,
                Used=phy_memory_used,
                ActualUsed=phy_memory_actual_used,
            ),
            virtual_values=VirtualValues(
                SwapTotal=swap_memory_total,
                SwapFree=swap_memory_free,
                SwapCached=swap_memory_cached,
                Used=swap_memory_used,
            ),
            physical_percentages=PhysicalPercentages(
                Used=phy_memory_used_percent,
                ActualUsed=phy_memory_actual_used_percent,
                Available=phy_memory_available_percent,
                Free=phy_memory_free_percent,
                Cached=phy_memory_cached_percent,
            ),
            virtual_percentages=VirtualPercentages(
                Used=swap_memory_used_percent,
                Free=swap_memory_free_percent,
            ),
        )
        
        return data
