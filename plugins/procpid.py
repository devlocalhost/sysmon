#!?usr/bin/env python3

"""
procpid plugin for sysmon
"""

import os

from .extra import (
    en_open,
    char_padding,
    convert_bytes,
    clean_output,
    to_bytes,
    PROCS,
)


def main():
    """
    return the most ram (vmrss) consuming pids, with their state and name
    """

    processes = []

    for entry_dir in os.scandir("/proc"):
        if entry_dir.is_dir() and entry_dir.name.isdigit():
            try:
                with en_open(
                    os.path.join(entry_dir.path, "status"), "r"
                ) as status_file:
                    s_readlines = status_file.readlines()

                    pid_name = None
                    rss = None
                    state = None

                    pid_name_line = next(
                        (line for line in s_readlines if line.startswith("Name:")), None
                    )
                    if pid_name_line:
                        pid_name = pid_name_line.partition(":")[2].strip()

                    rss_line = next(
                        (line for line in s_readlines if line.startswith("VmRSS:")),
                        None,
                    )
                    if rss_line:
                        rss = int(clean_output(rss_line.partition(":")[2].strip()))

                    state_line = next(
                        (line for line in s_readlines if line.startswith("State:")),
                        None,
                    )
                    if state_line:
                        state = state_line.partition("(")[2].partition(")")[0].title()

                    if rss is not None:
                        processes.append(
                            (pid_name, to_bytes(rss), state, entry_dir.name)
                        )

            except FileNotFoundError:
                pass  # processes.append((None, 76328097200209, None, "64"))

    processes.sort(key=lambda a: a[1], reverse=True)

    formatted_data = [
        f"  --- /proc/pid/* {char_padding('-', 49)}\n   Name            PID         RSS            State"
    ]

    for process_name, rss, pstate, pid in processes[:PROCS]:
        rss_usage = convert_bytes(rss) if rss is not None else "!?"

        formatted_data.append(
            f"   {process_name or '!?!?'}{char_padding(' ', (15 - len(process_name or '!?!?')))}"
            f" {pid}{char_padding(' ', (11 - len(pid)))}"
            f" {rss_usage}{char_padding(' ', (14 - len(rss_usage)))} {pstate or '!?!?'}"
        )

    return "\n".join(formatted_data) + "\n"
