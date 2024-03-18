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

        output_list_phys_virt = [
            f"  ——— /proc/meminfo {'—' * 47}\n",
            f"     RAM: {' ' * 25}Swap:\n",
            f"         Total: {convert_bytes(data['physical']['values']['total'])}",
            f"          Used: {convert_bytes(data['physical']['values']['used'])} ({data['physical']['percentage']['used']}%)",
            f"   Actual Used: {convert_bytes(data['physical']['values']['actual_used'])} ({data['physical']['percentage']['actual_used']}%)\n",
            f"     Available: {convert_bytes(data['physical']['values']['available'])} ({data['physical']['percentage']['available']}%)",
            f"          Free: {convert_bytes(data['physical']['values']['free'])} ({data['physical']['percentage']['free']}%)\n",
            f"        Cached: {convert_bytes(data['physical']['values']['cached'])}",
            f"   — Combined: {'— ' * 26}\n",
            f"         Total: {convert_bytes(combined_total_memory)}",
            f"     Available: {convert_bytes(combined_total_available)} ({combined_available_percent}%)",
        ]
        # 0. plugin name
        # 1. table row
        # 2. Total
        # 3. Used
        # 4. Actual Used
        # 5. Available
        # 6. Free
        # 7. Cached

        # line = line + spaces * 40 [len line] + other_line
        # this is what basically happens over the next lines. i choose to do this
        # instead of using a library because i do not want to depend on external libraries
        # and i "cba" to write a different solution. for now, this is the best solution.
        output_list_phys_virt[2] = (
            output_list_phys_virt[2]
            + " " * max(0, 40 - len(output_list_phys_virt[2]))
            + f"Total: {convert_bytes(data['virtual']['values']['total'])}\n"
        )
        output_list_phys_virt[3] = (
            output_list_phys_virt[3]
            + " " * max(0, 41 - len(output_list_phys_virt[3]))
            + f"Used: {convert_bytes(data['virtual']['values']['used'])} ({data['virtual']['percentage']['used']}%)\n"
        )
        output_list_phys_virt[5] = (
            output_list_phys_virt[5]
            + " " * max(0, 36 - len(output_list_phys_virt[5]))
            + f"Available: {convert_bytes(data['virtual']['values']['available'])} ({data['virtual']['percentage']['available']}%)\n"
        )
        output_list_phys_virt[7] = (
            output_list_phys_virt[7]
            + " " * max(0, 39 - len(output_list_phys_virt[7]))
            + f"Cached: {convert_bytes(data['virtual']['values']['cached'])}\n"
        )
        output_list_phys_virt[9] = (
            output_list_phys_virt[9]
            + " " * max(0, 41 - len(output_list_phys_virt[9]))
            + f"Used: {convert_bytes(combined_total_used)} ({combined_used_percent}%)\n"
        )
        output_list_phys_virt[10] = (
            output_list_phys_virt[10]
            + " " * max(0, 34 - len(output_list_phys_virt[10]))
            + f"Actual Used: {convert_bytes(combined_total_actual_used)}\n"
        )

        return "".join(output_list_phys_virt)

    output_list_phys = [
        f"  ——— /proc/meminfo {'—' * 47}\n",
        f"   RAM: {' ' * 25}\n",
        f"        Total: {convert_bytes(data['physical']['values']['total'])}",
        f"         Used: {convert_bytes(data['physical']['values']['used'])} ({data['physical']['percentage']['used']}%)",
        f"    Available: {convert_bytes(data['physical']['values']['available'])} ({data['physical']['percentage']['available']}%)",
    ]
    # 0. plugin name
    # 1. table row
    # 2. Total
    # 3. Used
    # 4. Free

    # avail, actual, cached

    output_list_phys[2] = (
        output_list_phys[2]
        + " " * max(0, 32 - len(output_list_phys[2]))
        + f"         Free: {convert_bytes(data['physical']['values']['free'])} ({data['physical']['percentage']['free']}%)\n"
    )
    output_list_phys[3] = (
        output_list_phys[3]
        + " " * max(0, 31 - len(output_list_phys[3]))
        + f"   Actual Used: {convert_bytes(data['physical']['values']['actual_used'])} ({data['physical']['percentage']['actual_used']}%)\n"
    )
    output_list_phys[4] = (
        output_list_phys[4]
        + " " * max(0, 31 - len(output_list_phys[4]))
        + f"        Cached: {convert_bytes(data['physical']['values']['cached'])}\n"
    )

    return "".join(output_list_phys)


def end():
    """
    clean up when the program exits
    """

    meminfo_class.close_files()


if __name__ == "__main__":
    main()
