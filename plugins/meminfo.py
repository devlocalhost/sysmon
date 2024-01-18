#!/usr/bin/env python3

"""meminfo plugin for sysmon"""

from util.util import (
    convert_bytes,
    to_bytes,
    clean_output,
    file_has,
    SHOW_SWAP,
    en_open,
)
from util.logger import setup_logger

logger = setup_logger(__name__)

logger.debug("[init] initializing")

logger.debug("[open] /proc/meminfo")
meminfo_file = en_open("/proc/meminfo")


class Meminfo:
    """
    Meminfo class - get physical and swap memory usage

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

        self.meminfo_file = en_open("/proc/meminfo")
        self.logger.debug("[open] /proc/meminfo")

        self.files_opened = [self.meminfo_file]

    def close_files(self):
        """
        closing the opened files. always call this
        when ending the program
        """

        for file in self.files_opened:
            self.logger.debug(f"[close] {file.name}")
            file.close()

    def get_data(self):
        # thanks to https://stackoverflow.com/a/28161352
        meminfo_data = dict(
            (i.split()[0].rstrip(":"), int(i.split()[1]) * 1024)
            for i in self.meminfo_file.readlines()
        )

        # NOTE: should data be returned raw? (in bytes)
        # or converted?
        phy_memory_total = meminfo_data.get("MemTotal")
        phy_memory_available = meminfo_data.get("MemAvailable")
        phy_memory_free = meminfo_data.get("MemFree")

        phy_memory_raw_cached = meminfo_data.get("Cached")
        phy_memory_sreclaimable = meminfo_data.get("SReclaimable")
        phy_memory_buffers = meminfo_data.get("Buffers")

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

        data = {
            "physical_memory": {
                "total": phy_memory_total,
                "used": phy_memory_used,
                "actual_used": phy_memory_actual_used,
                "available": phy_memory_available,
                "free": phy_memory_free,
                "cached": phy_memory_cached,
            },
            "swap_memory": {
                "total": xyz,
                "used": xyz,
                "available": xyz,
                "cached": xyz,
            },
        }

        # meminfo_data.get("")

        return meminfo_data


def main():
    """/proc/meminfo - system memory information"""

    meminfo_file.seek(0)
    logger.debug("[seek] /proc/meminfo")

    meminfo_data = meminfo_file.readlines()

    memory_total = to_bytes(int(clean_output(file_has("MemTotal", meminfo_data))))
    memory_available = to_bytes(
        int(clean_output(file_has("MemAvailable", meminfo_data)))
    )

    raw_memory_cached = to_bytes(int(clean_output(file_has("Cached", meminfo_data))))
    sreclaimable_memory = to_bytes(
        int(clean_output(file_has("SReclaimable", meminfo_data)))
    )
    memory_buffers = to_bytes(int(clean_output(file_has("Buffers", meminfo_data))))

    memory_cached = raw_memory_cached + memory_buffers + sreclaimable_memory

    memory_free = to_bytes(int(clean_output(file_has("MemFree", meminfo_data))))
    memory_used = round(memory_total - memory_available)

    memory_actual_used = round(
        memory_total
        - memory_free
        - memory_buffers
        - raw_memory_cached
        - sreclaimable_memory
    )

    memory_used_percent = round((int(memory_used) / int(memory_total)) * 100, 1)

    memory_actual_used_percent = round(
        (int(memory_actual_used) / int(memory_total)) * 100, 1
    )

    memory_available_percent = round(100 - memory_used_percent, 1)
    memory_free_percent = round((int(memory_free) / int(memory_total)) * 100, 1)

    memory_used_format = f"{convert_bytes(memory_used)} ({memory_used_percent}%)"
    memory_avail_format = (
        f"{convert_bytes(memory_available)} " f"({memory_available_percent}%)"
    )

    if (
        to_bytes(int(clean_output(file_has("SwapTotal", meminfo_data)))) != 0
        and SHOW_SWAP is not False
    ):
        logger.debug("[memory] swap stats")

        swap_total = to_bytes(int(clean_output(file_has("SwapTotal", meminfo_data))))
        swap_available = to_bytes(int(clean_output(file_has("SwapFree", meminfo_data))))
        swap_cached = to_bytes(int(clean_output(file_has("SwapCached", meminfo_data))))

        swap_used = round(swap_total - swap_available)
        swap_used_percent = round((int(swap_used) / int(swap_total)) * 100, 1)
        swap_available_percent = round(100 - swap_used_percent, 1)

        total_memory = memory_total + swap_total
        total_actual_used = memory_actual_used + swap_used
        total_used = memory_used + swap_used
        total_available = memory_available + swap_available

        used_perc = round((memory_used_percent + swap_used_percent) / 2, 1)
        available_perc = round(
            (memory_available_percent + swap_available_percent) / 2, 1
        )

        logger.debug("[data] print out")

        return (
            f"  ——— /proc/meminfo {'—' * 47}\n"
            f"     RAM: {' ' * 25}Swap:\n"
            f"         Total: {convert_bytes(memory_total)}"
            + f"{' ':<16}Total: {convert_bytes(swap_total)}\n"
            f"          Used: {memory_used_format}"
            + " " * (25 - len(memory_used_format))
            + f"Used: {convert_bytes(swap_used)} ({swap_used_percent}%)\n"
            f"   Actual Used: {convert_bytes(memory_actual_used)} ({memory_actual_used_percent}%)\n"
            f"     Available: {memory_avail_format}"
            + " " * (20 - len(memory_avail_format))
            + f"Available: {convert_bytes(swap_available)} ({swap_available_percent}%)\n"
            f"          Free: {convert_bytes(memory_free)} ({memory_free_percent}%)\n"
            f"        Cached: {convert_bytes(memory_cached)}"
            + " " * (23 - len(convert_bytes(memory_cached)))
            + f"Cached: {convert_bytes(swap_cached)}\n   — Combined: {'— ' * 26}\n"
            + f"         Total: {convert_bytes(total_memory)}{' ':<17}Used: {convert_bytes(total_used)} ({used_perc}%)\n"
            f"     Available: {convert_bytes(total_available)} ({available_perc}%){' ':<2}Actual Used: {convert_bytes(total_actual_used)}\n"
        )

    logger.debug("[data] print out")

    return (
        f"  ——— /proc/meminfo {'—' * 47}\n"
        f"   RAM: {' ' * 25}\n"
        f"        Total: {convert_bytes(memory_total)}"
        + f"{' ':<17}Cached: {convert_bytes(memory_cached)}\n"
        f"         Used: {convert_bytes(memory_used)} ({memory_used_percent}%)"
        + " " * (20 - len(str(memory_used_format)))
        + f"Actual Used: {convert_bytes(memory_actual_used)} ({memory_actual_used_percent}%)\n"
        f"    Available: {convert_bytes(memory_available)} ({memory_available_percent}%)"
        + f"{' ':<9}Free: {convert_bytes(memory_free)} ({memory_free_percent}%)\n"
    )
