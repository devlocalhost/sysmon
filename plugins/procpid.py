#!/usr/bin/env python3

"""procpid plugin for sysmon"""

import os
import sys


from util.util import (
    en_open,
    to_bytes,
    PROCS,
)

from util.logger import setup_logger


def read_process_status(pid):
    """get pid data, like name, state, vmrss"""

    pid_data = {}

    try:
        with en_open(f"/proc/{pid}/status") as pid_status_file:
            pid_file_lines = {}
            pid_data["pid"] = pid

            for line in pid_status_file:
                line = line.split()

                key = line[0].rstrip(":").lower()

                try:
                    value = (
                        line[1:][1].strip("(").strip(")").title()
                        if key == "state"
                        else line[1:][0]
                    )

                except IndexError:
                    value = "!?!?"

                pid_file_lines[key] = value

        return pid_file_lines

    except FileNotFoundError:
        sys.exit(f"PID {pid} does not exist (anymore?)")


class Procpid:
    """
    Procpid class - get processes and sort from highest to lowest
    based on VmRSS usage

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
        """
        initializing important stuff
        """

        self.logger = setup_logger(__name__)

        self.logger.debug("[init] initializing")

    def get_data(self):
        """
        returns a json dict with data
        """

        data = {"processes": []}

        process_dirs = [pid for pid in os.listdir("/proc") if pid.isdigit()]
        processes = []

        for pid in process_dirs:
            process_info = read_process_status(pid)

            if process_info:
                processes.append(process_info)

        self.logger.debug("[get_data] sorting")

        processes = sorted(
            processes, key=lambda x: int(x.get("vmrss", 0)), reverse=True
        )

        for proc_data in processes[:PROCS]:
            data["processes"].append(
                {
                    "name": proc_data["name"],
                    "pid": int(proc_data["pid"]),
                    "vmrss": to_bytes(int(proc_data["vmrss"])),
                    "state": proc_data["state"],
                }
            )

        return data
