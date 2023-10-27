#!?usr/bin/env python3

"""procpid plugin for sysmon"""

import os
from util.util import (
    en_open,
    convert_bytes,
    to_bytes,
    PROCS,
)
from util.logger import setup_logger

logger = setup_logger("procpid")


def main():
    """return the most ram (vmrss) consuming pids, with their state and name"""

    process_dirs = [pid for pid in os.listdir("/proc") if pid.isdigit()]
    processes = []

    for pid in process_dirs:
        try:
            with en_open(f"/proc/{pid}/status") as status_file:
                process_info = {}

                vmrss_found = False
                process_info["pid"] = pid

                for line in status_file:
                    parts = line.split()
                    if len(parts) >= 2:
                        key = parts[0].rstrip(":")
                        if (
                            key == "Name"
                            or key == "State"
                            or (key == "VmRSS" and len(parts) >= 3)
                        ):
                            if key != "State":
                                value = parts[1]
                            else:
                                state_part = (
                                    parts[2].partition("(")[2].partition(")")[0].title()
                                )
                                value = state_part
                            process_info[key] = value

                            if key == "VmRSS":
                                vmrss_found = True

                if vmrss_found:
                    processes.append(process_info)

        except FileNotFoundError:
            pass

    processes = sorted(
        processes, key=lambda x: int(x.get("VmRSS", 0)), reverse=True
    )

    formatted_data = [
            f"  ——— /proc/pid/status (self: {os.getpid():<5}) {'—' * 30}\n   Name            PID         RSS            State"
    ]

    for procs_data in processes[:PROCS]:
        process_name = procs_data["Name"]
        pid = procs_data["pid"]
        rss_usage = convert_bytes(to_bytes(int(procs_data["VmRSS"])))
        pstate = procs_data["State"]

        formatted_data.append(
            f"   {process_name or '!?!?'}{' ' * (15 - len(process_name or '!?!?'))}"
            f" {pid}{' ' * (11 - len(pid))}"
            f" {rss_usage}{' ' * (14 - len(rss_usage))} {pstate or '!?!?'}"
        )

    return "\n".join(formatted_data) + "\n"
