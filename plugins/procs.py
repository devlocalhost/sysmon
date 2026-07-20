#!/usr/bin/env python3

"""procpid plugin for sysmon"""

import os

from dataclasses import dataclass

from plugins.base import BasePlugin


@dataclass
class ProcessData:
    Name: str = "!?!?"
    PID: int = 0
    VmRSS: float = 0.0
    State: str = "!?!?"
    Utilization: int = 0


class Plugin(BasePlugin):
    def __init__(self):
        super().__init__()

        self.logger.debug("initialize plugin")
        self.processes_to_show = 8

        self.logger.debug(f"showing only {self.processes_to_show} processes")

        self._procstat_file = self._open_file("/proc/stat")
        self._opened_files.append(self._procstat_file)

        self._old_time_total = 0
        self._proc_times = {}

        self.logger.debug("opened file /proc/stat")

    def _get_process_data(self, pid, time_total):
        """get pid data, like name, state, vmrss"""

        # should this function be outside of the ProcsPlugin?

        try:
            with open(f"/proc/{pid}/status") as process_status_file:
                process_file_lines = {}

                for line in process_status_file:
                    line = line.split()
                    key = line[0].rstrip(":").lower()

                    try:
                        value = (
                            " ".join(line[1:][1:]).strip("(").strip(")").title()
                            if key == "state"
                            else line[1:][0]
                        )

                    except IndexError:
                        value = "!?!?"

                    # how accurate is this? does every line consist of key: value ?
                    process_file_lines[key] = value

            with open(f"/proc/{pid}/cmdline") as pid_cmdline:
                exec_name = (
                    pid_cmdline.read()
                    .replace("\x00", " ")
                    .strip()
                    .split("/")[-1]
                    .split(" ")[0]
                )

                if len(exec_name) > 28:
                    exec_name = exec_name[:25] + "..."

                # reading the cmdline file can give us a more "accurate"/better
                # name for the process, compared to the status file
                # BUT, sometimes it can be iaccurate or blank.

            process_name = (
                exec_name
                if len(exec_name) != 0
                else process_file_lines.get("name", "!?!?")
            )

            return ProcessData(
                Name=process_file_lines.get("name", "!?!?"),
                PID=process_file_lines.get("pid", 0),
                VmRSS=int(process_file_lines.get("vmrss", 0)) * 1024,  # or maybe not? give raw value instead?
                State=process_file_lines.get("state", "!?!?"),
                Utilization=self._get_process_utilization(pid, time_total),
            )

        except FileNotFoundError:
            return ProcessData()

    def _get_process_utilization(self, pid, time_total):
        # credit: https://stackoverflow.com/a/1424556

        with self._open_file(f"/proc/{pid}/stat") as f:
            data = f.read()

        after_comm = data[data.rindex(")") + 1 :].split()
        utime = int(after_comm[11])
        stime = int(after_comm[12])

        old_utime, old_stime = self._proc_times.get(pid, (utime, stime))

        # HARDCODED VALUES BELOW
        # DONT HARDCODE THE * 20 PART
        # but then, how am i supposed to get total logical cores? maybe i can import cpuinfo
        # plugin, or maybe another method? idfk
        user_util = 100 * (utime - old_utime) / (time_total - self._old_time_total) * 20
        sys_util = 100 * (stime - old_stime) / (time_total - self._old_time_total) * 20

        self._proc_times[pid] = (utime, stime)

        return round(user_util + sys_util, 1)

    def get_data(self):
        self._procstat_file.seek(0)

        time_total = sum(int(x) for x in self._procstat_file.readline().split()[1:])
        process_data = []

        for process_id in [pid for pid in os.listdir("/proc") if pid.isdigit()]:
            process_data.append(self._get_process_data(process_id, time_total))

        self._old_time_total = time_total
        sorted_processes = sorted(
            process_data, key=lambda x: int(x.VmRSS), reverse=True
        )
        # int(x.VmRSS): this part can be swapped with x.Utilization btw, which will sort
        # by cpu usage. this should definitely be a feature, and config too

        self.logger.debug("data out")

        return sorted_processes[:self.processes_to_show]
