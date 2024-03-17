#!/usr/bin/env python3

"""
formatter for cpuinfo plugin
"""

from util.util import SHOW_TEMPERATURE
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

    cpu_cores_phys = data["cores"]["physical"]

    if cpu_cores_phys == 0:
        if data["uses_smt"] is True:
            cpu_cores_phys = data["cores"]["logical"] / 2

        cpu_cores_phys = data["cores"]["logical"]  # um, what the fuck?

    output_text = (
        f"  ——— /proc/cpuinfo {'—' * 47}\n"
        f"   Usage: {data['usage']:>5}% {arch_model_temp_line}" + "\n"
        f"   Cores: {cpu_cores_phys}c/{data['cores']['logical']}t | Frequency: {data['frequency']:>7} MHz | Cache: {data['cache_size']}"
    )

    if data["cache_type"] != 0:
        output_text += f", {data['cache_type']}\n"

    else:
        output_text += "\n"

    return output_text


def end():
    """
    clean up when the program exits
    """

    cpuinfo_class.close_files()


if __name__ == "__main__":
    main()
