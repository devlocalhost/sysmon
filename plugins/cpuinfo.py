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
    convert_bytes,
    to_bytes,
    SHOW_TEMPERATURE,
    open_readonly,
)
from util.logger import setup_logger

logger = setup_logger(__name__)

core_file = open_readonly("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")
logger.info("[open ->] core file")

proc_stat_file = open_readonly("/proc/stat")
logger.info("[open ->] /proc/stat")

hwmon_dirs_out = glob.glob("/sys/class/hwmon/*")

data_dict = {
    "cpu_freq": "Unknown",
    "cpu_cache": "Unknown",
    "cpu_cores_phys": 0,
    "cpu_cores_logical": 0,
    "cpu_uses_smt": False,
    "cpu_model": "Unknown",
    "cpu_arch": "Unknown",
    "cpu_cache_type": 0,
}


def clean_cpu_model(model):
    """cleaning cpu model"""

    replace_stuff = [
        "(R)",
        "(TM)",
        "(tm)",
        "Processor",
        "processor",
        '"AuthenticAMD"',
        "Chip Revision",
        "Technologies, Inc",
        "CPU",
        "with Radeon HD Graphics",
        "with Radeon Graphics",
    ]

    for text in replace_stuff:
        model = model.replace(text, "")

    return " ".join(model.split()).split("@", maxsplit=1)[0].rstrip(" ")


def get_info():
    """
    instead of repeatedly getting the information that usually doesnt change
    a lot (or even rarely changes), why not get them once?

    get 'static' information, like cpu cache, cores count, and cpu freq
    """

    data_dict["cpu_arch"] = platform.machine()

    try:
        buffer = ctypes.create_string_buffer(64)
        buffer_cores_phys = ctypes.c_uint
        buffer_cores_log = ctypes.c_uint

        # prioritize in-tree shared object
        if os.path.exists("util/sysmon_cpu_utils.so"):
            cpu_utils = ctypes.CDLL(
                os.path.dirname(os.path.abspath("util/sysmon_cpu_utils.so"))
                + os.path.sep
                + "sysmon_cpu_utils.so"
            )
        else:
            cpu_utils = ctypes.CDLL("sysmon_cpu_utils.so")

        buffer_cores_phys = cpu_utils.get_cores(1)
        buffer_cores_log = cpu_utils.get_cores(0)

        if (
            buffer_cores_phys < buffer_cores_log
            and buffer_cores_log != 0
            and buffer_cores_phys != 0
        ):
            data_dict["cpu_cores_phys"] = buffer_cores_phys
            data_dict["cpu_cores_logical"] = buffer_cores_log

        cpu_utils.get_cache_size(buffer)
        output = buffer.value.decode().split(".")

        if output[0] != "Unknown":
            data_dict["cpu_cache"] = convert_bytes(int(output[0]))
            data_dict["cpu_cache_type"] = output[1]

    except OSError:
        pass

    try:
        with en_open("/sys/devices/system/cpu/smt/active") as smt_file:
            content = smt_file.read().strip()

            if content == "1":
                data_dict["cpu_uses_smt"] = True

    except (FileNotFoundError, PermissionError):
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
                    data_dict["cpu_freq"] = round(float(line.split(":")[1].strip()), 2)

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

            if data_dict["cpu_cores_logical"] == 0:
                data_dict["cpu_cores_logical"] = os.sysconf(
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

    try:
        logger.info("[read <-] core")

        core_file.seek(0)
        return round(int(core_file.read().strip()) / 1000, 2)

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

        proc_stat_file.seek(0)
        new_stats = proc_stat_file.readline().replace("cpu ", "cpu").strip().split(" ")
        logger.info("[read <-] /proc/stat")

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
            logger.info("[ out >>] /proc/stat")
            return str(round(100 * ((previous_data - current_data) / total), 1)) + "%"

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
        arch_model_temp_line = f"{cpu_temperature:>6} | CPU: {data_dict['cpu_arch']} {data_dict['cpu_model']}"

    else:
        arch_model_temp_line = (
            f"| CPU: {data_dict['cpu_arch']} {data_dict['cpu_model']}"
        )

    cpu_cores_phys = data_dict["cpu_cores_phys"]

    if cpu_cores_phys == 0:
        if data_dict["cpu_uses_smt"] is True:
            cpu_cores_phys = data_dict["cpu_cores_logical"] / 2

        cpu_cores_phys = data_dict["cpu_cores_logical"]

    output_text = (
        f"  ——— /proc/cpuinfo {'—' * 47}\n"
        f"   Usage: {cpu_usage_num:>6}, {arch_model_temp_line}" + "\n"
        f"   Cores: {cpu_cores_phys}c/{data_dict['cpu_cores_logical']}t | Frequency: {cpu_freq():>7} MHz | Cache: {data_dict['cpu_cache']}"
    )

    if data_dict["cpu_cache_type"] != 0:
        output_text += f", L{data_dict['cpu_cache_type']}\n"

    else:
        output_text += "\n"

    return output_text
