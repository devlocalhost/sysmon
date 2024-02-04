#!/usr/bin/env python3

"""meminfo plugin for sysmon"""

from util.util import (
    convert_bytes,
    SHOW_SWAP,
    en_open,
)
from util.logger import setup_logger


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
        """
        returns a json dict with data
        """

        for file in self.files_opened:
            self.logger.debug(f"[seek] {file.name}")
            file.seek(0)

        # thanks to https://stackoverflow.com/a/28161352
        meminfo_data = dict(
            (i.split()[0].rstrip(":"), int(i.split()[1]) * 1024)
            for i in self.meminfo_file.readlines()
        )

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

        data = {
            "physical": {
                "values": {
                    "total": phy_memory_total,
                    "used": phy_memory_used,
                    "actual_used": phy_memory_actual_used,
                    "available": phy_memory_available,
                    "free": phy_memory_free,
                    "cached": phy_memory_cached,
                },
                "percentage": {
                    "used": phy_memory_used_percent,
                    "actual_used": round(
                        (int(phy_memory_actual_used) / int(phy_memory_total)) * 100, 1
                    ),
                    "available": round(100 - phy_memory_used_percent, 1),
                    "free": round(
                        (int(phy_memory_free) / int(phy_memory_total)) * 100, 1
                    ),
                },
            },
            "virtual": {
                "values": {
                    "total": swap_memory_total,
                    "used": swap_memory_used,
                    "available": swap_memory_available,
                    "cached": swap_memory_cached,
                },
                "percentage": {
                    "used": round(
                        (int(swap_memory_used) / int(swap_memory_total)) * 100, 1
                    ),
                    "available": round(100 - swap_memory_used_percent, 1),
                },
            },
        }

        return data

    def print_data(self):
        """
        returns the data, but formatted.
        not intended to be used, please
        use get_data() instead
        """

        data = self.get_data()

        phys_memory_used_format = f"{convert_bytes(data['physical']['values']['used'])} ({data['physical']['percentage']['used']}%)"
        phys_memory_avail_format = f"{convert_bytes(data['physical']['values']['available'])} ({data['physical']['percentage']['available']}%)"

        if data["virtual"]["values"]["total"] != 0 and SHOW_SWAP is not False:
            combined_total_memory = (
                data["physical"]["values"]["total"] + data["virtual"]["values"]["total"]
            )
            combined_total_actual_used = (
                data["physical"]["values"]["actual_used"]
                + data["virtual"]["values"]["used"]
            )
            combined_total_used = (
                data["physical"]["values"]["used"] + data["virtual"]["values"]["used"]
            )
            combined_total_available = (
                data["physical"]["values"]["available"]
                + data["virtual"]["values"]["available"]
            )

            combined_used_percent = round(
                (
                    data["physical"]["percentage"]["used"]
                    + data["virtual"]["percentage"]["used"]
                )
                / 2,
                1,
            )
            combined_available_percent = round(
                (
                    data["physical"]["percentage"]["available"]
                    + data["virtual"]["percentage"]["available"]
                )
                / 2,
                1,
            )

            return (
                f"  ——— /proc/meminfo {'—' * 47}\n"
                f"     RAM: {' ' * 25}Swap:\n"
                f"         Total: {convert_bytes(data['physical']['values']['total'])}"
                + f"{' ':<16}Total: {convert_bytes(data['virtual']['values']['total'])}\n"
                f"          Used: {phys_memory_used_format}"
                + " " * (25 - len(phys_memory_used_format))
                + f"Used: {convert_bytes(data['virtual']['values']['used'])} ({data['virtual']['percentage']['used']}%)\n"
                f"   Actual Used: {convert_bytes(data['physical']['values']['actual_used'])} ({data['physical']['percentage']['actual_used']}%)\n"
                f"     Available: {phys_memory_avail_format}"
                + " " * (20 - len(phys_memory_avail_format))
                + f"Available: {convert_bytes(data['virtual']['values']['available'])} ({data['virtual']['percentage']['available']}%)\n"
                f"          Free: {convert_bytes(data['physical']['values']['free'])} ({data['physical']['percentage']['free']}%)\n"
                f"        Cached: {convert_bytes(data['physical']['values']['cached'])}"
                + " " * (23 - len(convert_bytes(data["physical"]["values"]["cached"])))
                + f"Cached: {convert_bytes(data['virtual']['values']['cached'])}\n   — Combined: {'— ' * 26}\n"
                + f"         Total: {convert_bytes(combined_total_memory)}{' ':<17}Used: {convert_bytes(combined_total_used)} ({combined_used_percent}%)\n"
                f"     Available: {convert_bytes(combined_total_available)} ({combined_available_percent}%){' ':<2}Actual Used: {convert_bytes(combined_total_actual_used)}\n"
            )

        return (
            f"  ——— /proc/meminfo {'—' * 47}\n"
            f"   RAM: {' ' * 25}\n"
            f"        Total: {convert_bytes(data['physical']['values']['total'])}"
            + f"{' ':<17}Cached: {convert_bytes(data['physical']['values']['cached'])}\n"
            f"         Used: {convert_bytes(data['physical']['values']['used'])} ({data['physical']['percentage']['used']}%)"
            + " " * (20 - len(str(phys_memory_used_format)))
            + f"Actual Used: {convert_bytes(data['physical']['values']['actual_used'])} ({data['physical']['percentage']['actual_used']}%)\n"
            f"    Available: {convert_bytes(data['physical']['values']['available'])} ({data['physical']['percentage']['available']}%)"
            + f"{' ':<9}Free: {convert_bytes(data['physical']['values']['free'])} ({data['physical']['percentage']['free']}%)\n"
        )
