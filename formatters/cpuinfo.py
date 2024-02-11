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

    if SHOW_TEMPERATURE:
        cpu_temperature += " °C"
        arch_model_temp_line = f"{cpu_temperature:>6} | CPU: {data['static']['architecture']} {data['static']['model']}"

    else:
        arch_model_temp_line = (
            f"| CPU: {data['static']['architecture']} {data['static']['model']}"
        )

    cpu_cores_phys = data["static"]["cores"]["physical"]

    if cpu_cores_phys == 0:
        if data["static"]["uses_smt"] is True:
            cpu_cores_phys = data["static"]["cores"]["logical"] / 2

        cpu_cores_phys = data["static"]["cores"]["logical"]  # um, what the fuck?

    output_text = (
        f"  ——— /proc/cpuinfo {'—' * 47}\n"
        f"   Usage: {data['usage']:>5}% {arch_model_temp_line}" + "\n"
        f"   Cores: {cpu_cores_phys}c/{data['static']['cores']['logical']}t | Frequency: {data['static']['frequency']:>7} MHz | Cache: {data['static']['cache_size']}"
    )

    if data["static"]["cache_type"] != 0:
        output_text += f", {data['static']['cache_type']}\n"

    else:
        output_text += "\n"

    return output_text


if __name__ == "__main__":
    main()
