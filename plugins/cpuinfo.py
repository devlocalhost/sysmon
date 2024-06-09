#!/usr/bin/env python3

"""cpuinfo plugin for sysmon"""

import os
import sys
import glob
import ctypes
import platform

from util.util import (
    en_open,
    convert_bytes,
    to_bytes,
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
    """
    Cpuinfo class - get cpu details

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
        self.logger = setup_logger(__name__)

        self.logger.debug("[init] initializing")

        self.hwmon_dirs = glob.glob("/sys/class/hwmon/*")
        self.thermal_dirs = glob.glob("/sys/class/thermal/*")

        self.temperature_file = self.set_temperature_file()

        try:  # FIXME: there has to be a better way for this
            self.core_file = en_open(
                "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
            )
            self.logger.debug(f"[init] {self.core_file}")

        except FileNotFoundError:
            self.core_file = None

        self.stat_file = en_open("/proc/stat")
        self.cpu_usage_data = [
            779676,
            14374,
            251479,
            4146687,
            19745,
            109,
            12880,
            0,
            0,
            0,
        ]
        self.static_data = self.get_static_info()

        self.files_opened = [self.core_file, self.stat_file, self.temperature_file]

    def close_files(self):
        """
        closing the opened files. always call this
        when ending the program
        """

        for file in self.files_opened:
            try:
                self.logger.debug(f"[close_files] {file.name}")
                file.close()

            except:
                pass

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
            "uses_smt": "Unknown",
            "model": "Unknown",
            "architecture": "Unknown",
            "cache_type": "Unknown",
            "cache_size": "Unknown",
        }

        data_dict["architecture"] = platform.machine()

        try:  # getting cache using the c library
            buffer = ctypes.create_string_buffer(64)
            buffer_cores_phys = ctypes.c_uint
            buffer_cores_log = ctypes.c_uint

            # prioritize in-tree shared object
            if os.path.exists("util/sysmon_cpu_utils.so"):
                self.logger.debug("[get_static_info] using lib from util/")
                cpu_utils = ctypes.CDLL("util/sysmon_cpu_utils.so")

            else:
                self.logger.debug("[get_static_info] using global lib")
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

            self.logger.debug(f"[get_static_info] buffer_cores_phys: {buffer_cores_phys}")
            self.logger.debug(f"[get_static_info] buffer_cores_log: {buffer_cores_log}")

            cpu_utils.get_cache_size(buffer)
            output = buffer.value.decode().split(".")

            if output[0] != "Unknown":
                data_dict["cache_size"] = convert_bytes(int(output[0]))
                data_dict["cache_type"] = output[1]

        except OSError as exc:
            self.logger.debug(f"[get_static_info] failed, {exc}")

        try:
            with en_open("/sys/devices/system/cpu/smt/active") as smt_file:
                content = smt_file.read().strip()

                if content == "1":
                    data_dict["uses_smt"] = True

        except (FileNotFoundError, PermissionError):
            pass

        try:  # reading from cpuinfo file
            with en_open("/proc/cpuinfo") as cpuinfo_file:
                cpuinfo_file_data = {}

                for line in cpuinfo_file:
                    if line.strip():
                        key, value = [s.strip() for s in line.split(":", 1)]
                        cpuinfo_file_data[key.replace(" ", "_").lower()] = value

                # self.logger.debug(f"[cpuinfo file] {cpu_info}")

                if (
                    "arm" not in data_dict["architecture"]
                    and "aarch" not in data_dict["architecture"]
                ):
                    # this code applies only for desktop platforms

                    cache = cpuinfo_file_data.get("cache_size")
                    frequency = cpuinfo_file_data.get("cpu_mhz")

                    if data_dict["cache_size"] == "Unknown" and cache:
                        self.logger.debug("[get_static_info] fallback to /proc/cpuinfo cache")

                        data_dict["cache"] = convert_bytes(to_bytes(int(cache.split()[0])))

                    if frequency:
                        data_dict["frequency"] = round(float(frequency), 2)

                    model = clean_cpu_model(cpuinfo_file_data.get("model_name"))

                else:  # in case this is an arm system, grab hardware
                    model = clean_cpu_model(cpuinfo_file_data.get("hardware"))

            data_dict["model"] = model if len(model) < 25 else model[:22] + "..."

            return data_dict

        except FileNotFoundError:
            sys.exit("Couldnt find /proc/cpuinfo file")

        except PermissionError:
            sys.exit(
                "Couldnt read the file. Do you have read permissions for /proc/cpuinfo file?"
            )


    def cpu_freq(self):
        """get cpu frequency"""

        if self.core_file:
            self.core_file.seek(0)

            return round(int(self.core_file.read().strip()) / 1000, 2)

        return self.static_data["frequency"]

    def cpu_usage(self):
        """/proc/stat - cpu usage of the system"""

        old_cpu_usage_data = self.cpu_usage_data
        previous_data = (
            self.cpu_usage_data[0]
            + self.cpu_usage_data[1]
            + self.cpu_usage_data[2]
            + self.cpu_usage_data[5]
            + self.cpu_usage_data[6]
        )

        self.stat_file.seek(0)

        new_cpu_usage_data = [
            int(num)
            for num in self.stat_file.readline().strip("cpu").strip().split(" ")
        ]

        current_data = (
            int(new_cpu_usage_data[0])
            + int(new_cpu_usage_data[1])
            + int(new_cpu_usage_data[2])
            + int(new_cpu_usage_data[5])
            + int(new_cpu_usage_data[6])
        )

        total = sum(map(int, old_cpu_usage_data)) - sum(map(int, new_cpu_usage_data))

        self.cpu_usage_data = new_cpu_usage_data

        try:
            return abs(round(100 * ((previous_data - current_data) / total), 1))

        except ZeroDivisionError:
            return 0

        except FileNotFoundError:
            sys.exit("Couldnt find /proc/stat file")

        except PermissionError:
            sys.exit(
                "Couldnt read the file. Do you have read permissions for /proc/stat file?"
            )

    def set_temperature_file(self):
        """Get the CPU temperature from /sys/class/hwmon and /sys/class/thermal"""

        allowed_types = ("coretemp", "k10temp", "acpitz", "cpu_1_0_usr", "cpu-1-0-usr")

        combined_dirs = [*self.hwmon_dirs, *self.thermal_dirs]

        self.logger.debug(f"[set_temperature_file] {combined_dirs}")

        for temp_dir in combined_dirs:  # NEEDS TESTING
            sensor_type_file = (
                os.path.join(temp_dir, "type")
                if os.path.isfile(os.path.join(temp_dir, "type"))
                and os.path.exists(os.path.join(temp_dir, "type"))
                else os.path.join(temp_dir, "name")
            )

            try:
                with en_open(sensor_type_file) as temp_type_file:
                    sensor_type = temp_type_file.read().strip()

                    self.logger.debug(f"[set_temperature_file] {temp_dir}: {sensor_type}")

                    if sensor_type in allowed_types:
                        temperature_files = glob.glob(os.path.join(temp_dir, "temp*"))

                        if temperature_files:
                            self.logger.debug(f"[set_temperature_file] using {temperature_files[-1]} as sensor file")
                            return en_open(temperature_files[-1])

            except FileNotFoundError:
                self.logger.debug(f"[set_temperature_file] COULD NOT OPEN FILE. NO SENSOR SET")

        return None

    def get_data(self):
        """/proc/cpuinfo - cpu information"""

        data = {
            "temperature": None,
            "usage": self.cpu_usage(),
        }

        data = data | self.get_static_info()  # merge the two dicts into one

        data["frequency"] = self.cpu_freq()

        if self.temperature_file:
            self.temperature_file.seek(0)
            data["temperature"] = float(
                int(self.temperature_file.read().strip()) // 1000
            )

        return data
