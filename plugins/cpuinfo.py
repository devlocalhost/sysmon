import re
import glob
import platform

from dataclasses import dataclass

from plugins.base import BasePlugin

from utils.util import en_open


@dataclass
class ProcessorDetails:
    model: str = "!?!?"
    utilization: int = 0
    frequency_min: float = 0.0
    frequency_max: float = 0.0
    physical_cores: int = 0
    logical_cores: int = 0
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


class CpuinfoPlugin(BasePlugin):
    def __init__(self):
        super().__init__()

        self.logger.debug("initialize plugin")
        self._old_user_time, self._old_system_time, self._old_idle = 0, 0, 0

        try:
            self._stat_file = en_open("/proc/stat")
            self._opened_files.append(self._stat_file)

            self.logger.debug(f"opened file {self._stat_file.name}")

        except Exception as exc:
            self.logger.error(f"error opening file: {exc}")

    def _get_processor_utilization(self):
        stat_file = self._stat_file.readlines()
        # cpuN user-time nice-time system-time idle-time io-wait ireq   softirq steal guest guest_nice
        # cpu  2432102   96139     671184      40452630  28234   141491 43214   0     0     0

        f_cpu = stat_file[0].strip().split(" ")
        # calculating the overall cpu utilization

        current_user_time = int(f_cpu[2])
        current_system_time = int(f_cpu[4])
        current_idle = int(f_cpu[5])

        calculation = (current_user_time + current_system_time) - (
            self._old_user_time + self._old_system_time
        )
        utilization = (
            calculation / (calculation + (current_idle - self._old_idle)) * 100
        )

        # updating old_vars
        self._old_user_time, self._old_system_time, self._old_idle = (
            current_user_time,
            current_system_time,
            current_idle,
        )

        return round(utilization, 2)

    def _get_frequency_ranges(self):
        frequencies = []

        for cpu in glob.glob("/sys/devices/system/cpu/cpu[0-9]*"):
            # glob.glob("/sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_m*_freq")
            # maybe the thing above is a better alternative?
            for scaling in ("scaling_min_freq", "scaling_max_freq"):
                try:
                    with en_open(f"{cpu}/cpufreq/{scaling}") as scaling_file:
                        frequencies.append(int(scaling_file.read()))

                except FileNotFoundError as exc:
                    self.logger.debug(f"failed to open file: {exc}")

        return frequencies

    def _get_physical_cores_count(self):
        # this might be highly inaccurate, testing needed

        siblings = []

        for file in glob.glob(
            "/sys/devices/system/cpu/cpu[0-9]*/topology/thread_siblings_list"
        ):
            try:
                with en_open(file) as f:
                    siblings.append(f.read().strip())

            except FileNotFoundError as exc:
                self.logger.debug(f"failed to open file: {exc}")
                return 0

        return len(list(set(siblings)))

    def _get_processor_model(self):
        model_name = None

        try:
            # TODO: remove the if else block below. read the comments in the get_data function
            # TODO: after making the static details static/available, test if the below line works (has data)
            # TODO: if it works, then replace the below if else block, by checking the architecture
            # TODO: using the data from ProcessorDetails
            self.logger.debug(ProcessorDetails())

            with en_open("/proc/cpuinfo") as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith("model name"):
                        model_name = line
                        break

                if model_name:
                    # x86 platform
                    return _clean_processor_model_string(
                        "".join(model_name.split(":")[1:])
                    )

                else:
                    # arm platform
                    with en_open("/proc/device-tree/compatible", "rb") as f:
                        model_name = (
                            f.read()
                            .replace(b"\x00", b"")
                            .decode()
                            .split(",")[-1]
                            .upper()
                        )

        except Exception as exc:
            self.logger.debug(f"could not open file: {exc}")

    def get_data(self):
        self._seek_files()

        with en_open("/sys/devices/system/cpu/present") as _present_cores:
            logical_cores = int(_present_cores.read().strip().split("-")[1]) + 1
            # maybe this could be merged (and renamed) with _get_physical_cores_count?

        sorted_freqs = sorted(self._get_frequency_ranges())
        freq_min_range, freq_max_range = sorted_freqs[0], sorted_freqs[-1]

        return ProcessorDetails(
            model=self._get_processor_model(),  # static!
            utilization=self._get_processor_utilization(),
            frequency_min=freq_min_range,  # static!
            frequency_max=freq_max_range,  # static!
            physical_cores=self._get_physical_cores_count(),  # static!
            logical_cores=logical_cores,  # static!
            architecture=platform.machine(),  # static!
        )
