#!/usr/bin/env python3

"""
formatter for meminfo plugin
"""

from util.util import convert_bytes, SHOW_SWAP
from plugins import meminfo

meminfo_class = meminfo.Meminfo()


def main():
    """
    returns the data, but formatted.
    """

    data = meminfo_class.get_data()

    phys_memory_used_format = f"{convert_bytes(data['physical']['values']['used'])} ({data['physical']['percentage']['used']}%)"
    phys_memory_avail_format = f"{convert_bytes(data['physical']['values']['available'])} ({data['physical']['percentage']['available']}%)"

    if data["virtual"]["values"]["total"] != 0 and SHOW_SWAP is not False:
        combined_total_memory = (
            data["physical"]["values"]["total"] + data["virtual"]["values"]["total"]
        )
        combined_total_actual_used = (
            data["physical"]["values"]["actual_used"]
            + data["virtual"]["values"]["used"]
        )
        combined_total_used = (
            data["physical"]["values"]["used"] + data["virtual"]["values"]["used"]
        )
        combined_total_available = (
            data["physical"]["values"]["available"]
            + data["virtual"]["values"]["available"]
        )

        combined_used_percent = round(
            (
                data["physical"]["percentage"]["used"]
                + data["virtual"]["percentage"]["used"]
            )
            / 2,
            1,
        )
        combined_available_percent = round(
            (
                data["physical"]["percentage"]["available"]
                + data["virtual"]["percentage"]["available"]
            )
            / 2,
            1,
        )

        return (
            f"  ——— /proc/meminfo {'—' * 47}\n"
            f"     RAM: {' ' * 25}Swap:\n"
            f"         Total: {convert_bytes(data['physical']['values']['total'])}"
            + f"{' ':<16}Total: {convert_bytes(data['virtual']['values']['total'])}\n"
            f"          Used: {phys_memory_used_format}"
            + " " * (25 - len(phys_memory_used_format))
            + f"Used: {convert_bytes(data['virtual']['values']['used'])} ({data['virtual']['percentage']['used']}%)\n"
            f"   Actual Used: {convert_bytes(data['physical']['values']['actual_used'])} ({data['physical']['percentage']['actual_used']}%)\n"
            f"     Available: {phys_memory_avail_format}"
            + " " * (20 - len(phys_memory_avail_format))
            + f"Available: {convert_bytes(data['virtual']['values']['available'])} ({data['virtual']['percentage']['available']}%)\n"
            f"          Free: {convert_bytes(data['physical']['values']['free'])} ({data['physical']['percentage']['free']}%)\n"
            f"        Cached: {convert_bytes(data['physical']['values']['cached'])}"
            + " " * (23 - len(convert_bytes(data["physical"]["values"]["cached"])))
            + f"Cached: {convert_bytes(data['virtual']['values']['cached'])}\n   — Combined: {'— ' * 26}\n"
            + f"         Total: {convert_bytes(combined_total_memory)}{' ':<17}Used: {convert_bytes(combined_total_used)} ({combined_used_percent}%)\n"
            f"     Available: {convert_bytes(combined_total_available)} ({combined_available_percent}%){' ':<2}Actual Used: {convert_bytes(combined_total_actual_used)}\n"
        )

    return (
        f"  ——— /proc/meminfo {'—' * 47}\n"
        f"   RAM: {' ' * 25}\n"
        f"        Total: {convert_bytes(data['physical']['values']['total'])}"
        + f"{' ':<17}Cached: {convert_bytes(data['physical']['values']['cached'])}\n"
        f"         Used: {convert_bytes(data['physical']['values']['used'])} ({data['physical']['percentage']['used']}%)"
        + " " * (20 - len(str(phys_memory_used_format)))
        + f"Actual Used: {convert_bytes(data['physical']['values']['actual_used'])} ({data['physical']['percentage']['actual_used']}%)\n"
        f"    Available: {convert_bytes(data['physical']['values']['available'])} ({data['physical']['percentage']['available']}%)"
        + f"{' ':<9}Free: {convert_bytes(data['physical']['values']['free'])} ({data['physical']['percentage']['free']}%)\n"
    )


if __name__ == "__main__":
    main()
