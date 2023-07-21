#!/usr/bin/env python3

"""
meminfo plugin for sysmon
"""

import sys

from .extra import (
    en_open,
    convert_bytes,
    to_bytes,
    char_padding,
    clean_output,
    file_has,
    SHOW_SWAP,
)


def main():
    """
    /proc/meminfo - system memory information
    """

    try:
        with en_open("/proc/meminfo") as meminfo_file:
            meminfo_data = meminfo_file.readlines()

            memory_total = to_bytes(
                int(clean_output(file_has("MemTotal", meminfo_data)))
            )
            memory_available = to_bytes(
                int(clean_output(file_has("MemAvailable", meminfo_data)))
            )
            memory_cached = (
                to_bytes(int(clean_output(file_has("Cached", meminfo_data))))
                + to_bytes(int(clean_output(file_has("Buffers", meminfo_data))))
                + to_bytes(int(clean_output(file_has("SReclaimable", meminfo_data))))
            )

            memory_free = to_bytes(int(clean_output(file_has("MemFree", meminfo_data))))

            memory_buffers = to_bytes(int(clean_output(file_has("Buffers", meminfo_data))))

            memory_used = round(memory_total - memory_available)
            memory_actual_used = round(
                memory_total
                - to_bytes(int(clean_output(file_has("MemFree", meminfo_data))))
                - to_bytes(int(clean_output(file_has("Buffers", meminfo_data))))
                - to_bytes(int(clean_output(file_has("Cached", meminfo_data))))
                - to_bytes(int(clean_output(file_has("SReclaimable", meminfo_data))))
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

                spaces_swap = (
                    25
                    if str(convert_bytes(swap_total)).split(" ")[1] == "GiB"
                    else 23
                    if str(convert_bytes(swap_total)).split(" ")[1] == "TiB"
                    and str(convert_bytes(memory_total)).split(" ")[1] == "TiB"
                    else 22
                    if str(convert_bytes(swap_total)).split(" ")[1] == "TiB"
                    else 25
                )

                return (
                    f"  --- /proc/meminfo {char_padding('-', 47)}\n"
                    f"     RAM: {char_padding(' ', 25)}Swap:\n"
                    f"         Total: {convert_bytes(memory_total)}"
                    + char_padding(
                        " ", (spaces_swap - len(convert_bytes(swap_total)))
                    )
                    + f"Total: {convert_bytes(swap_total)}\n"
                    f"          Used: {memory_used_format}"
                    + char_padding(" ", (25 - len(memory_used_format)))
                    + f"Used: {convert_bytes(swap_used)} ({swap_used_percent}%)\n"
                    f"   Actual Used: {convert_bytes(memory_actual_used)} ({memory_actual_used_percent}%)\n"
                    f"     Available: {memory_avail_format}"
                    + char_padding(" ", (20 - len(memory_avail_format)))
                    + f"Available: {convert_bytes(swap_available)} ({swap_available_percent}%)\n"
                    f"          Free: {convert_bytes(memory_free)} ({memory_free_percent}%)\n"
                    f"        Cached: {convert_bytes(memory_cached)}"
                    + char_padding(" ", (23 - len(convert_bytes(memory_cached))))
                    + f"Cached: {convert_bytes(swap_cached)}\n"
                    + f"       Buffers: {convert_bytes(memory_buffers)}\n"
                )

            return (
                f"  --- /proc/meminfo {char_padding('-', 47)}\n"
                f"   RAM: {char_padding(' ', 25)}\n"
                f"        Total: {convert_bytes(memory_total)}"
                + char_padding(" ", (24 - len(str(memory_cached))))
                + f"Cached: {convert_bytes(memory_cached)}\n"
                f"         Used: {convert_bytes(memory_used)} ({memory_used_percent}%)"
                + char_padding(" ", (20 - len(str(memory_used_format))))
                + f"Actual Used: {convert_bytes(memory_actual_used)} ({memory_actual_used_percent}%)\n"
                f"    Available: {convert_bytes(memory_available)} ({memory_available_percent}%)"
                + char_padding(" ", (18 - len(str(memory_cached))))
                + f"Free: {convert_bytes(memory_free)} ({memory_free_percent}%)\n"
                + f"      Buffers: {convert_bytes(memory_buffers)}\n"
            )

    except FileNotFoundError:
        sys.exit("Couldnt find /proc/meminfo file")

    except PermissionError:
        sys.exit(
            "Couldnt read the file. Do you have read permissions for /proc/meminfo file?"
        )
