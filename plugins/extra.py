#!/usr/bin/env python3

"""
extra plugin for sysmon - basic functions
needed for sysmon to function
"""

import os
import glob


# START OF IMPORTANT PART FOR THE PLUGINS

# general vars
# general vars, save data directory and IEC or metric conversion (size)
SAVE_DIR = None
CONVERSION_TYPE = 1024

# cpuinfo.py vars
# cpuinfo.py vars - control whenever to show cpu temperature
SHOW_TEMPERATURE = True

# meminfo.py vars
# meminfo.py vars - show swap statsor no
SHOW_SWAP = True

# procpid.py vars
# procpid.py vars - how many processes to display
PROCS = 6

# netstats vars
# netstats vars - custom interface, from /sys/class/net/
# check /sys/class/net/ for more
INTERFACE = None

# END OF IMPORTANT PART FOR THE PLUGINS


try:
    os.makedirs("/tmp/sysmon_save", exist_ok=True)
    SAVE_DIR = "/tmp/sysmon_save"

except OSError:
    os.makedirs(".sysmon_save", exist_ok=True)
    SAVE_DIR = ".sysmon_save"


def char_padding(char, value):
    """
    return char value times
    """
    return char * value


def convert_bytes(fsize, units=(" bytes", " KiB", " MiB", " GiB", " TiB")):
    """convert bytes to k, m, g and t"""
    for unit in units:
        if fsize < CONVERSION_TYPE:
            return f"{fsize:.2f}{unit if CONVERSION_TYPE == 1024 else unit.replace('i', '')}"

        fsize /= CONVERSION_TYPE

    return f"{fsize:.2f} {units[-1]}"


def en_open(file, method="r"):
    """modifying the default open method so i dont have to define encoding every time"""
    return open(file, mode=method, encoding="utf-8")


def detect_network_adapter():
    """detect an active network adapter/card/whatever and return its directory"""

    if INTERFACE is None:
        for adapter_dir in glob.glob("/sys/class/net/*"):
            with en_open(adapter_dir + "/type") as device_type:
                if int(device_type.read()) != 772:  # if not loopback device
                    with en_open(adapter_dir + "/operstate") as status:
                        if status.read().strip() == "up":
                            return adapter_dir
        return None

    else:
        return "/sys/class/net/" + INTERFACE


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


def uptime_format():
    """format the uptime from seconds to a human readable format"""
    intervals = (("week", 604800), ("day", 86400), ("hour", 3600), ("minute", 60))
    result = []

    with en_open("/proc/uptime") as uptime_file:
        seconds = int(float(uptime_file.readline().split()[0]))

    original_seconds = seconds

    if seconds < 60:
        return f"{seconds} seconds"

    for time_type, count in intervals:
        value = seconds // count

        if value:
            seconds -= value * count
            result.append(f"{value} {time_type if value == 1 else time_type + 's'}")

    if len(result) > 1:
        result[-1] = "and " + result[-1]

    return (", ".join(result), original_seconds)


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
