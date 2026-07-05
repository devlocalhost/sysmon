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


def get_process_data(pid):
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
            process_file_lines["name"] = exec_name

        return ProcessData(
            Name=process_file_lines.get("name", "!?!?"),
            PID=process_file_lines.get("pid", 0),
            VmRSS=int(process_file_lines.get("vmrss", 0)) * 1024,  # or maybe not? give raw value instead?
            State=process_file_lines.get("state", "!?!?"),
        )

    except FileNotFoundError:
        return ProcessData()


class Plugin(BasePlugin):
    def __init__(self):
        super().__init__()

        self.logger.debug("initialize plugin")
        self.processes_to_show = 6

        self.logger.debug(f"showing only {self.processes_to_show} processes")

    def get_data(self):
        process_data = []

        # i dont like how im repeatedly opening and closing files
        # but theres probably not a better way
        for process_id in [pid for pid in os.listdir("/proc") if pid.isdigit()]:
            process_data.append(get_process_data(process_id))

        sorted_processes = sorted(
            process_data, key=lambda x: int(x.VmRSS), reverse=True
        )

        self.logger.debug("data out")

        return sorted_processes[: self.processes_to_show]
