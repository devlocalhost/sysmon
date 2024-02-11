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
)

from util.logger import setup_logger

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


class Cpuinfo:
    def __init__(self):
        self.logger = setup_logger(__name__)

        self.logger.debug("[init] initializing")

        self.hwmon_dirs = glob.glob("/sys/class/hwmon/*")
        self.temperature_file = None

        try:
            self.core_file = en_open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")

        except FileNotFoundError:
            self.core_file = None

        self.stat_file = en_open("/proc/stat")

        self.files_opened = [self.core_file, self.stat_file, self.temperature_file]

    def get_static_info(self):
        """
        get 'static' information, like cpu cache, cores count, etc
        """

        data_dict = {
            "frequency": "Unknown",
            "cores": {
                "physical": 0,
                "logical": 0,
            },
            "uses_smt": False,
            "model": "Unknown",
            "architecture": "Unknown",
            "cache_type": "Unknown",
            "cache_size": "Unknown",
        }

        data_dict["architecture"] = platform.machine()

        try:
            buffer = ctypes.create_string_buffer(64)
            buffer_cores_phys = ctypes.c_uint
            buffer_cores_log = ctypes.c_uint

            # prioritize in-tree shared object
            if os.path.exists("util/sysmon_cpu_utils.so"):
                logger.debug("[cache lib] using lib from util/")
                cpu_utils = ctypes.CDLL("util/sysmon_cpu_utils.so")

            else:
                logger.debug("[cache lib] using global lib")
                cpu_utils = ctypes.CDLL("sysmon_cpu_utils.so")

            buffer_cores_phys = cpu_utils.get_cores(1)
            buffer_cores_log = cpu_utils.get_cores(0)

            if (
                buffer_cores_phys < buffer_cores_log
                and buffer_cores_log != 0
                and buffer_cores_phys != 0
            ):
                data_dict["cores"]["physical"] = buffer_cores_phys
                data_dict["cores"]["logical"] = buffer_cores_log

            cpu_utils.get_cache_size(buffer)
            output = buffer.value.decode().split(".")

            if output[0] != "Unknown":
                data_dict["cache_size"] = convert_bytes(int(output[0]))
                data_dict["cache_type"] = output[1]

        except OSError as exc:
            logger.debug(f"[cache lib] failed, {exc}")
            pass

        try:
            with en_open("/sys/devices/system/cpu/smt/active") as smt_file:
                content = smt_file.read().strip()

                if content == "1":
                    data_dict["uses_smt"] = True

        except (FileNotFoundError, PermissionError):
            pass

        try:
            with en_open("/proc/cpuinfo") as cpuinfo_file:
            # FIXME: this needs to be rewriten
            # FIXME: in a similar way as meminfo
                for line in cpuinfo_file:
                    if data_dict["cache_size"] == "Unknown":
                        logger.debug("[cache] fallback to /proc/cpuinfo cache")

                        if line.startswith("cache size"):
                            data_dict["cache"] = convert_bytes(
                                to_bytes(
                                    int(
                                        line.split(":")[1].strip().lower().replace("kb", "")
                                    )
                                )
                            )

                    if line.startswith("cpu MHz"):
                        data_dict["frequency"] = round(float(line.split(":")[1].strip()), 2)

                    if line.startswith("model name"):
                        model = clean_cpu_model(line.split(":")[1].strip())
                        data_dict["model"] = (
                            model if len(model) < 25 else model[:22] + "..."
                        )

                    if line.startswith("Hardware") and data_dict["cpu_arch"] in (
                        "aarch64",
                        "armv7l",
                    ):
                        data_dict["model"] = clean_cpu_model(line.split(":")[1].strip())

                # why using getconf and os.sysconf, instead of os.sysconf only?
                # because os.sysconf LEVEL2_CACHE_SIZE wont return anything on my system
                # there are better ways to handle this yeah, but for now, it is what it is

                if data_dict["cores"]["logical"] == 0:
                    data_dict["cores"]["logical"] = os.sysconf(
                        os.sysconf_names["SC_NPROCESSORS_CONF"]
                    )

        except FileNotFoundError:
            sys.exit("Couldnt find /proc/stat file")

        except PermissionError:
            sys.exit(
                "Couldnt read the file. Do you have read permissions for /proc/stat file?"
            )

        return data_dict

    def cpu_freq(self):
        """get cpu frequency"""

        if self.core_file:
            self.core_file.seek(0)

            return round(int(self.core_file.read().strip()) / 1000, 2)

        return data_dict["cpu_freq"]

    def cpu_usage(self):
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

            self.stat_file.seek(0)

            new_stats = self.stat_file.readline().replace("cpu ", "cpu").strip().split(" ")

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
                return abs(round(100 * ((previous_data - current_data) / total), 1))

            except (
                ZeroDivisionError
            ):  # there should be a better way (or maybe thats the only way)
                return 0

        except FileNotFoundError:
            sys.exit("Couldnt find /proc/stat file") # FIXME: this has to be moved, possibly in __init__

        except PermissionError:
            sys.exit(
                "Couldnt read the file. Do you have read permissions for /proc/stat file?"
            ) # FIXME: this has to be moved, possibly in __init__


    def get_temperature_file(self): # get_cpu_temp_file()
        """getting the cpu temperature from /sys/class/hwmon"""

        allowed_types = ("coretemp", "k10temp", "acpitz", "cpu_1_0_usr")
        temperature_file = None

        for temp_dir in self.hwmon_dirs:
            with en_open(temp_dir + "/name") as temp_type:
                sensor_type = temp_type.read().strip()

                logger.debug(f"[sensors] {temp_dir}: {sensor_type}")

                if sensor_type in allowed_types:
                    self.temperature_file = en_open(glob.glob(f"{temp_dir}/temp*_input")[-1])
                    logger.debug(f"[temp file] cpu temp sensor: {temperature_file}")
                    break


    def get_data(self):
        """/proc/cpuinfo - cpu information"""
        
        self.get_temperature_file()

        data = {
            "static": self.get_static_info(),
            "temperature": None,
            "usage": self.cpu_usage(),
        }

        if self.temperature_file:  # 2 ifs...?
            self.temperature_file.seek(0)
            data["temperature"] = str(int(self.temperature_file.read().strip()) // 1000)
            
        return data

        # if cpu_temperature != "!?" and SHOW_TEMPERATURE:
        #     cpu_temperature += " °C"
        #     arch_model_temp_line = f"{cpu_temperature:>6} | CPU: {data_dict['architecture']} {data_dict['model']}"

        # else:
        #     arch_model_temp_line = (
        #         f"| CPU: {data_dict['architecture']} {data_dict['model']}"
        #     )

        # cpu_cores_phys = data_dict["cores"]["physical"]

        # if cpu_cores_phys == 0:
        #     if data_dict["uses_smt"] is True:
        #         cpu_cores_phys = data_dict["cores"]["logical"] / 2

        #     cpu_cores_phys = data_dict["cores"]["logical"] # um, what the fuck?

        # output_text = (
        #     f"  ——— /proc/cpuinfo {'—' * 47}\n"
        #     f"   Usage: {cpu_usage_num:>6} {arch_model_temp_line}" + "\n"
        #     f"   Cores: {cpu_cores_phys}c/{data_dict['cores']['logical']}t | Frequency: {self.cpu_freq():>7} MHz | Cache: {data_dict['cache_size']}"
        # )

        # if data_dict["cache_type"] != 0:
        #     output_text += f", L{data_dict['cache_type']}\n"

        # else:
        #     output_text += "\n"

        # logger.debug("[data] print out")
        # return output_text
