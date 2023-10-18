#!/usr/bin/env python3

"""meminfo plugin for sysmon"""

import sys

from util.util import (
    en_open,
    convert_bytes,
    to_bytes,
    clean_output,
    file_has,
    SHOW_SWAP,
)


def main():
    """/proc/meminfo - system memory information"""

    try:
        with en_open("/proc/meminfo") as meminfo_file:
            meminfo_data = meminfo_file.readlines()

            memory_total = to_bytes(
                int(clean_output(file_has("MemTotal", meminfo_data)))
            )
            memory_available = to_bytes(
                int(clean_output(file_has("MemAvailable", meminfo_data)))
            )

            raw_memory_cached = to_bytes(
                int(clean_output(file_has("Cached", meminfo_data)))
            )
            sreclaimable_memory = to_bytes(
                int(clean_output(file_has("SReclaimable", meminfo_data)))
            )
            memory_buffers = to_bytes(
                int(clean_output(file_has("Buffers", meminfo_data)))
            )

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

            memory_used_format = (
                f"{convert_bytes(memory_used)} ({memory_used_percent}%)"
            )
            memory_avail_format = (
                f"{convert_bytes(memory_available)} " f"({memory_available_percent}%)"
            )

            if (
                to_bytes(int(clean_output(file_has("SwapTotal", meminfo_data)))) != 0
                and SHOW_SWAP is not False
            ):
                swap_total = to_bytes(
                    int(clean_output(file_has("SwapTotal", meminfo_data)))
                )
                swap_available = to_bytes(
                    int(clean_output(file_has("SwapFree", meminfo_data)))
                )
                swap_cached = to_bytes(
                    int(clean_output(file_has("SwapCached", meminfo_data)))
                )

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

            return (
                f"  ——— /proc/meminfo {'—' * 47}\n"
                f"   RAM: {' ' * 25}\n"
                f"        Total: {convert_bytes(memory_total)}"
                + f"{' ':<17}Cached: {convert_bytes(memory_cached)}\n"
                f"         Used: {convert_bytes(memory_used)} ({memory_used_percent}%)"
                + " " * (20 - len(str(memory_used_format)))
                + f"Actual Used: {convert_bytes(memory_actual_used)} ({memory_actual_used_percent}%)\n"
                f"    Available: {convert_bytes(memory_available)} ({memory_available_percent}%)"
                + f"{' ':<11}Free: {convert_bytes(memory_free)} ({memory_free_percent}%)\n"
            )

    except FileNotFoundError:
        sys.exit("Couldnt find /proc/meminfo file")

    except PermissionError:
        sys.exit(
            "Couldnt read the file. Do you have read permissions for /proc/meminfo file?"
        )
