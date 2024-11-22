#!/usr/bin/env python3

"""
extra plugin for sysmon - basic functions
needed for sysmon to function
"""

import os


# START OF IMPORTANT PART FOR THE PLUGINS

# general vars, save data directory and IEC or metric conversion (size)
SAVE_DIR = None
CONVERSION_TYPE = 1024

# cpuinfo.py vars - control whenever to show cpu temperature
SHOW_TEMPERATURE = True

# meminfo.py vars - show swap statsor no
SHOW_SWAP = True

# procpid.py vars - how many processes to display
PROCS = 6

# netstats vars - custom interface, from /sys/class/net/
# check /sys/class/net/ for more
INTERFACE = None
SHOW_LOCAL_IP = True

# debugging - for logger.py
DEBUGGING = False

# END OF IMPORTANT PART FOR THE PLUGINS


def convert_bytes(fsize, units=("bytes", "KiB", "MiB", "GiB", "TiB")):
    """convert bytes to human readable format"""

    for unit in units:
        if fsize < CONVERSION_TYPE:
            return f"{fsize:.2f} {unit if CONVERSION_TYPE == 1024 else unit.replace('i', '')}"

        fsize /= CONVERSION_TYPE

    return f"{fsize:.2f} {units[-1]}"


def en_open(file, method="r"):
    """modifying the default open method so i dont have to define encoding every time"""

    return open(file, mode=method, encoding="utf-8")


def to_bytes(kilobytes):
    """convert kilobytes to bytes"""

    return kilobytes * 1024
