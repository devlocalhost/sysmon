#!/usr/bin/env python3

"""
extra plugin for sysmon - basic functions
needed for sysmon to function
"""

import os
import sys


# START OF IMPORTANT PART FOR THE PLUGINS

# general vars, save data directory and IEC or metric conversion (size)
SAVE_DIR = None
CONVERSION_TYPE = 1024

# cpuinfo.py vars - control whenever to show cpu temperature
SHOW_TEMPERATURE = True

# meminfo.py vars - show swap statsor no
SHOW_SWAP = True

# procpid.py vars - how many processes to display
PROCS = 5
SHOW_SYSMON = True

# netstats vars - custom interface, from /sys/class/net/
# check /sys/class/net/ for more
INTERFACE = None
SHOW_LOCAL_IP = True

# debugging - for logger.py
DEBUGGING = False

# END OF IMPORTANT PART FOR THE PLUGINS


try:
    os.makedirs("/tmp/sysmon_save", exist_ok=True)
    SAVE_DIR = "/tmp/sysmon_save"

except OSError:
    os.makedirs(".sysmon_save", exist_ok=True)
    SAVE_DIR = ".sysmon_save"


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


def file_has(string, lines):
    """checking if file contains string. return string if contains else return None"""

    for line in lines:
        if line.startswith(string):
            return line.strip().split(":")[1]

    return None


def clean_output(text):
    """
    cleans the output that sysmon reads, so it gets only 1005744
    instead of MemTotal:        1005744 kB
    """

    return text.split(":")[0].strip().replace("kB", "")


def to_bytes(kilobytes):
    """convert kilobytes to bytes"""

    return kilobytes * 1024
