#!/usr/bin/env python3

"""
formatter for cpuinfo plugin
"""

from util.util import SHOW_TEMPERATURE, convert_bytes
from plugins import cpuinfo

cpuinfo_class = cpuinfo.Cpuinfo()


def main():
    """
    returns the data, but formatted.
    """

    data = cpuinfo_class.get_data()

    cpu_temperature = data["temperature"]

    if SHOW_TEMPERATURE and cpu_temperature:
        cpu_temperature = str(cpu_temperature)
        cpu_temperature += " °C"

        arch_model_temp_line = (
            f"{cpu_temperature:>8} | CPU: {data['architecture']} {data['model']}"
        )

    else:
        arch_model_temp_line = f"| CPU: {data['architecture']} {data['model']}"

    cores_count_text = (
        f"Cores: {data['cores']['physical']}C/{data['cores']['logical']}T"
        if data["cores"]["physical"] != 0
        else f"Cores: {data['cores']['logical']}"
    )
    # this fuckery can only happen on arm platforms  since for some
    # fucking reason some retard thought it would be a good idea for
    # the cpuinfo file to be different on x86 and arm platforms
    # fuck you.

    cache_line = " | Cache: No data\n"

    if data["cache"]["level"]:
        cache_line = f" | Cache: {data['cache']['level']}"
        if data["cache"]["size"]:
            cache_line += f" {convert_bytes(data['cache']['size'])}\n"

    output_text = [
        f"  --- /proc/cpuinfo {'-' * 47}\n",
        f"   Usage: {data['usage']:>5}% {arch_model_temp_line}" + "\n",
        f"   {cores_count_text} | Frequency: {data['frequency']:>7} MHz",
    ]

    output_text[2] += cache_line
    # output_text[2] = output_text[2] + cache_line

    return "".join(output_text)


def end():
    """
    clean up when the program exits
    """

    cpuinfo_class.close_files()


if __name__ == "__main__":
    main()
