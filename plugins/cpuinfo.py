#!/usr/bin/env python3

"""
cpuinfo plugin for sysmon
"""

import os
import sys
import glob
import platform
import multiprocessing

from .extra import (
    en_open,
    SAVE_DIR,
    clean_cpu_model,
    convert_bytes,
    to_bytes,
    char_padding,
)

hwmon_dirs_out = glob.glob("/sys/class/hwmon/*")
SHOW_TEMPERATURE = True


def cpu_usage():
    """
    /proc/stat - cpu usage of the system
    """

    try:
        if not os.path.exists(SAVE_DIR + "/cpu_old_data"):
            with en_open(SAVE_DIR + "/cpu_old_data", "a") as temp_file:
                temp_file.write("cpu.758102.17.259220.2395399.122421.3.1284")

        with en_open(SAVE_DIR + "/cpu_old_data") as old_stats:
            old_stats = old_stats.readline().split(".")
            previous_data = (
                int(old_stats[1])
                + int(old_stats[2])
                + int(old_stats[3])
                + int(old_stats[6])
                + int(old_stats[7])
            )

        with en_open("/proc/stat") as new_stats:
            new_stats = new_stats.readline().replace("cpu ", "cpu").strip().split(" ")

            current_data = (
                int(new_stats[1])
                + int(new_stats[2])
                + int(new_stats[3])
                + int(new_stats[6])
                + int(new_stats[7])
            )

        total = sum(map(int, old_stats[1:])) - sum(map(int, new_stats[1:]))

        with en_open(SAVE_DIR + "/cpu_old_data", "w") as update_data:
            update_data.write(".".join(new_stats))

        try:
            return round(100 * ((previous_data - current_data) / total))

        except (
            ZeroDivisionError
        ):  # there should be a better way (or maybe thats the only way)
            return 0

    except FileNotFoundError:
        sys.exit("Couldnt find /proc/stat file")

    except PermissionError:
        sys.exit(
            "Couldnt read the file. Do you have read permissions for /proc/stat file?"
        )


def cpu_temp(hwmon_dirs):
    """
    getting the cpu temperature from /sys/class/hwmon
    """

    temperature = "!?"
    allowed_types = ("coretemp", "fam15h_power", "k10temp", "acpitz")

    for temp_dir in hwmon_dirs:
        with en_open(temp_dir + "/name") as temp_type:
            if temp_type.read().strip() in allowed_types:
                try:
                    with en_open(temp_dir + "/temp1_input") as temp_value:
                        temperature = int(temp_value.readline().strip()) // 1000
                        break

                except (FileNotFoundError, OSError):
                    pass

    return temperature


def main():
    """
    /proc/cpuinfo - cpu information
    """

    try:
        with en_open("/proc/cpuinfo") as cpuinfo_file:
            cpu_freq = "Unknown"
            model = "Unknown"
            cache_size = "0"
            architecture = platform.machine()

            for line in cpuinfo_file:
                if line.startswith("cpu MHz"):
                    cpu_freq = line.split(":")[1].strip()

                elif line.startswith("model name"):
                    model = clean_cpu_model(line.split(":")[1].strip())
                    model = model if len(model) < 25 else model[:25] + "..."

                elif line.startswith("cache size"):
                    cache_size = line.split(":")[1].strip().replace("KB", "")

                elif line.startswith("Hardware") and architecture in (
                    "aarch64",
                    "armv7l",
                ):
                    model = clean_cpu_model(line.split(":")[1].strip())

            total_cores = os.cpu_count() or "Unknown"
            total_threads = multiprocessing.cpu_count()

            cpu_usage_num = cpu_usage()
            cpu_temperature = str(cpu_temp(hwmon_dirs_out))

            if cpu_temperature != "!?" and SHOW_TEMPERATURE:
                cpu_temperature += " °C"
                arch_model_temp_line = f"({cpu_temperature}) | {architecture} {model}"

            else:
                arch_model_temp_line = f"| {architecture} {model}"

            cache_memory = convert_bytes(to_bytes(int(cache_size))) + " cache memory"

        return (
            f"  --- /proc/cpuinfo {char_padding('-', 47)}\n"
            f"{char_padding(' ', 11)}Usage: {cpu_usage_num}% "
            + " " * (3 - len(str(cpu_usage_num)))
            + arch_model_temp_line
            + "\n"
            f"   Cores/Threads: {total_cores}/{total_threads} @ {cpu_freq} MHz"
            f" with {cache_memory}\n"
        )

    except FileNotFoundError:
        sys.exit("Couldnt find /proc/cpuinfo file")

    except PermissionError:
        sys.exit(
            "Couldnt read the file. Do you have read permissions for /proc/meminfo file?"
        )
