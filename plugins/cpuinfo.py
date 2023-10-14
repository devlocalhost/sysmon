#!/usr/bin/env python3

"""cpuinfo plugin for sysmon"""

import os
import sys
import glob
import ctypes
import platform

from util.util import (
    en_open,
    SAVE_DIR,
    clean_cpu_model,
    convert_bytes,
    to_bytes,
    char_padding,
    SHOW_TEMPERATURE,
)

hwmon_dirs_out = glob.glob("/sys/class/hwmon/*")

data_dict = {
    "cpu_freq": "Unknown",
    "cpu_cache": "Unknown",
    "cpu_cores_all": 0,
    "cpu_model": "Unknown",
    "cpu_arch": "Unknown",
    "cpu_cache_type": 0,
}


def get_info():
    """
    instead of repeatedly getting the information that usually doesnt change
    a lot (or even rarely changes), why not get them once?

    get 'static' information, like cpu cache, cores count, and cpu freq
    """

    data_dict["cpu_arch"] = platform.machine()

    try:
        buffer = ctypes.create_string_buffer(64)

        ctypes.CDLL("sysmon_cpu_cache.so").get_cache_size(buffer)
        output = buffer.value.decode().split(".")

        if output[0] != "Unknown":
            data_dict["cpu_cache"] = convert_bytes(int(output[0]))
            data_dict["cpu_cache_type"] = output[1]

    except OSError:
        pass

    try:
        with en_open("/proc/cpuinfo") as cpuinfo_file:
            for line in cpuinfo_file:
                if data_dict["cpu_cache"] == "Unknown":
                    if line.startswith("cache size"):
                        data_dict["cpu_cache"] = convert_bytes(
                            to_bytes(
                                int(
                                    line.split(":")[1].strip().lower().replace("kb", "")
                                )
                            )
                        )

                if line.startswith("cpu MHz"):
                    data_dict["cpu_freq"] = round(
                        float(line.split(":")[1].strip()) / 1000, 2
                    )

                if line.startswith("model name"):
                    model = clean_cpu_model(line.split(":")[1].strip())
                    data_dict["cpu_model"] = (
                        model if len(model) < 25 else model[:22] + "..."
                    )

                if line.startswith("Hardware") and data_dict["cpu_arch"] in (
                    "aarch64",
                    "armv7l",
                ):
                    data_dict["cpu_model"] = clean_cpu_model(line.split(":")[1].strip())

            # why using getconf and os.sysconf, instead of os.sysconf only?
            # because os.sysconf LEVEL2_CACHE_SIZE wont return anything on my system
            # there are better ways to handle this yeah, but for now, it is what it is

            data_dict["cpu_cores_all"] = os.sysconf(
                os.sysconf_names["SC_NPROCESSORS_CONF"]
            )

    except FileNotFoundError:
        sys.exit("Couldnt find /proc/stat file")

    except PermissionError:
        sys.exit(
            "Couldnt read the file. Do you have read permissions for /proc/stat file?"
        )


def cpu_freq():
    """get cpu frequency"""

    # if data_dict["cpu_freq"] == "Unknown":
    try:
        max_c = int(int(data_dict["cpu_cores_all"]) / 2)
        min_c = max_c - 1

        max_c_freq = 0
        min_c_freq = 0

        with en_open(f"/sys/devices/system/cpu/cpu{max_c}/cpufreq/scaling_cur_freq") as max_c_file:
            max_c_freq = int(max_c_file.read().strip())

        with en_open(f"/sys/devices/system/cpu/cpu{min_c}/cpufreq/scaling_cur_freq") as min_c_file:
            min_c_freq = int(min_c_file.read().strip())

        sum_c = max_c_freq + min_c_freq
    
        return round((sum_c / 2) / 1000, 2)

    except FileNotFoundError:
        return data_dict["cpu_freq"]

def cpu_usage():
    """/proc/stat - cpu usage of the system"""

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
    """getting the cpu temperature from /sys/class/hwmon"""

    temperature = "!?"
    allowed_types = ("coretemp", "k10temp", "acpitz", "cpu_1_0_usr")

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


get_info()

def main():
    """/proc/cpuinfo - cpu information"""

    cpu_usage_num = cpu_usage()
    cpu_temperature = str(cpu_temp(hwmon_dirs_out))

    if cpu_temperature != "!?" and SHOW_TEMPERATURE:
        cpu_temperature += " °C"
        arch_model_temp_line = f"({cpu_temperature}) | CPU: {data_dict['cpu_arch']} {data_dict['cpu_model']}"

    else:
        arch_model_temp_line = (
            f"| CPU: {data_dict['cpu_arch']} {data_dict['cpu_model']}"
        )

    output_text = (
        f"  --- /proc/cpuinfo {char_padding('-', 47)}\n"
        f"{char_padding(' ', 9)}Usage: {cpu_usage_num}% "
        + " " * (3 - len(str(cpu_usage_num)))
        + arch_model_temp_line
        + "\n"
        f"   Total Cores: {data_dict['cpu_cores_all']} | Frequency: {cpu_freq()} MHz | Cache: {data_dict['cpu_cache']}"
    )

    if data_dict["cpu_cache_type"] != 0:
        output_text += f", L{data_dict['cpu_cache_type']}\n"

    else:
        output_text += "\n"

    return output_text
