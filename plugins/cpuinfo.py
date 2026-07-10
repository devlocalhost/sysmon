import os
import re
import glob
import platform

from dataclasses import dataclass

from plugins.base import BasePlugin


@dataclass
class ProcessorDetails:
    model: str = "!?!?"
    utilization: int = 0
    average_frequency: int = 0
    frequency_min: float = 0.0
    frequency_max: float = 0.0
    physical_cores: int = 0
    logical_cores: int = 0
    temperature: float = 0
    # cache_type: str = "!?!?"
    # cache_size: float = 0.0
    # is cpu cache information even needed
    architecture: str = "!?!?"


def _clean_processor_model_string(model_string):
    replace_stuff = [
        r"\(R\)",
        r"\(TM\)",
        r"\(tm\)",
        r"Processor",
        r"processor",
        r'"AuthenticAMD"',
        r"Chip Revision",
        r"Technologies, Inc",
        r"CPU",
        r"with Radeon HD Graphics",
        r"with Radeon Graphics",
        r"with Radeon Vega Mobile Gfx",
        r"\d+-Core",
        r"\b\d{1,2}(?:st|nd|rd|th)?\s*(?:Gen|Generation)\b",
    ]

    for pattern in replace_stuff:
        model_string = re.sub(pattern, "", model_string, flags=re.IGNORECASE)

    return " ".join(model_string.split()).split("@", maxsplit=1)[0].strip()


class Plugin(BasePlugin):
    def __init__(self):
        super().__init__()

        self.logger.debug("initialize plugin")
        self._old_user_time, self._old_system_time, self._old_idle = 0, 0, 0
        self._temperature_sensor = self._get_temperature_file()

        try:
            self._stat_file = self._open_file("/proc/stat")
            self._opened_files.append(self._stat_file)

            self.logger.debug(f"opened file /proc/stat")

        except Exception as exc:
            self.logger.error(f"error opening file: {exc}")

        frequency_ranges = sorted(self._get_frequency_ranges())
        cores_count = self._get_cores_count()  # physical,logical

        self._processor_details = ProcessorDetails(
            model=self._get_processor_model(),
            frequency_min=frequency_ranges[0],
            frequency_max=frequency_ranges[1],
            physical_cores=cores_count[0],
            logical_cores=cores_count[1],
            architecture=platform.machine(),
        )

        self.logger.debug(
            f"initialize static processor details: {self._processor_details}"
        )

    def _get_temperature_file(self):
        """Get the CPU temperature from /sys/class/hwmon and /sys/class/thermal"""

        allowed_types = ("coretemp", "k10temp", "acpitz", "cpu_1_0_usr", "cpu-1-0-usr", "cpu_thermal", "cpu-thermal")
        combined_dirs = [
            *glob.glob("/sys/class/hwmon/*"),
            *glob.glob("/sys/class/thermal/*"),
        ]

        for temp_dir in combined_dirs:
            sensor_type_file = (
                os.path.join(temp_dir, "type")
                if os.path.isfile(os.path.join(temp_dir, "type"))
                and os.path.exists(os.path.join(temp_dir, "type"))
                else os.path.join(temp_dir, "name")
            )

            try:
                with self._open_file(sensor_type_file) as temp_type_file:
                    sensor_type = temp_type_file.read().strip()

                    self.logger.debug(f"[set_temperature_file] {temp_dir}: {sensor_type}")

                    if sensor_type in allowed_types:
                        temperature_files = glob.glob(
                            os.path.join(temp_dir, "temp*_input*")
                        ) or glob.glob(os.path.join(temp_dir, "temp"))

                        if temperature_files:
                            self.logger.debug(f"[set_temperature_file] using {temperature_files[-1]} as sensor file")
                            return temperature_files[-1]

            except FileNotFoundError:
                self.logger.debug(f"[set_temperature_file] FileNotFoundError, does {sensor_type_file} exist?")

        return None

    def _get_processor_utilization(self):
        # credit: https://beta.stackoverflow.com/q/58257596

        stat_file = self._stat_file.readlines()
        # cpuN user-time nice-time system-time idle-time io-wait ireq   softirq steal guest guest_nice
        # cpu  2432102   96139     671184      40452630  28234   141491 43214   0     0     0

        f_cpu = stat_file[0].strip().split(" ")
        # calculating the overall cpu utilization

        current_user_time = int(f_cpu[2])
        current_system_time = int(f_cpu[4])
        current_idle = int(f_cpu[5])

        calculation = (current_user_time + current_system_time) - (self._old_user_time + self._old_system_time)

        try:
            utilization = (calculation / (calculation + (current_idle - self._old_idle)) * 100)

        except ZeroDivisionError:
            utilization = 0

        # updating old_vars
        self._old_user_time, self._old_system_time, self._old_idle = (
            current_user_time,
            current_system_time,
            current_idle,
        )

        return round(utilization, 1)

    def _get_cores_frequency(self, pattern="m*"):
        # credit: https://beta.stackoverflow.com/q/12483399

        frequencies = []

        for scaling_file in glob.glob( f"/sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_{pattern}_freq"):
            try:
                with self._open_file(scaling_file) as f:
                    frequencies.append(int(f.read()))

            except FileNotFoundError as exc:
                self.logger.debug(f"failed to open file: {exc}")

        return frequencies

    def _get_frequency_ranges(self):
        freqs_sorted = sorted(self._get_cores_frequency())

        return (freqs_sorted[0], freqs_sorted[-1])

    def _get_average_frequency(self):
        freqs = self._get_cores_frequency("cur")

        return sum(freqs) / len(freqs)

    def _get_cores_count(self):
        # this might be highly inaccurate, testing needed
        # credit: https://beta.stackoverflow.com/q/73489422

        # physical cores part
        siblings = []

        for file in glob.glob("/sys/devices/system/cpu/cpu[0-9]*/topology/thread_siblings_list" ):
            try:
                with self._open_file(file) as f:
                    siblings.append(f.read().strip())

            except FileNotFoundError as exc:
                self.logger.debug(f"failed to open file: {exc}")
                return 0

        physical_cores = len(list(set(siblings)))

        # logical cores part
        with self._open_file("/sys/devices/system/cpu/present") as _present_cores:
            logical_cores = int(_present_cores.read().strip().split("-")[1]) + 1

        return (physical_cores, logical_cores)

    def _get_processor_model(self):
        model_name = None

        try:
            if platform.machine() in ("aarch64", "aarch", "arm", "arm64"):
                # we need to read a different file on arm platforms
                with self._open_file("/proc/device-tree/compatible", "rb", encoding=None) as f:
                    return f.read().replace(b"\x00", b"").decode().split(",")[-1].upper()
                    # yes, return it instead of model_name = blabla
                    # because the string is usally clean

            else:  # we are not on arm, proceed "normally"
                with self._open_file("/proc/cpuinfo") as f:
                    lines = f.readlines()

                    for line in lines:
                        if line.startswith("model name"):
                            model_name = line
                            break

        except Exception as exc:
            self.logger.debug(f"could not open file: {exc}")

        return _clean_processor_model_string("".join(model_name.split(":")[1:]))

    def get_data(self):
        self._seek_files()

        self._processor_details.utilization = self._get_processor_utilization()
        self._processor_details.average_frequency = self._get_average_frequency()

        if self._temperature_sensor:
            self._processor_details.temperature = float(int(self._open_file(self._temperature_sensor).read().strip()) // 1000)

        self.logger.debug("data out")

        return self._processor_details
