#!/usr/bin/env python3

"""
formatter for loadavg plugin
"""

from datetime import datetime

from plugins import loadavg

loadavg_class = loadavg.Loadavg()


def main():
    """
    returns the data, but formatted.
    """

    data = loadavg_class.get_data()

    intervals = (("month", 2628288), ("week", 604800), ("day", 86400), ("hour", 3600), ("minute", 60))
    result = []

    seconds = data["uptime"]["seconds"]
    original_seconds = seconds

    if seconds < 60:
        result.append(f"{seconds} seconds")

    else:
        for time_type, count in intervals:
            value = seconds // count

            if value:
                seconds -= value * count
                result.append(f"{value} {time_type if value == 1 else time_type + 's'}")

    if len(result) > 1:
        result[-1] = "and " + result[-1]

    uptime_formatted = ", ".join(result)
    uptime_since = datetime.fromtimestamp(data["uptime"]["timestamp"]).strftime(
        "%A, %B %d %Y, %I:%M:%S %p"
    )

    output_list = [
        f"  --- /proc/loadavg {'-' * 47}\n",
        f"     Load: {data['load_times']['1']}, {data['load_times']['5']}, {data['load_times']['15']}",
        f"\n   Uptime: {uptime_formatted}\n   Booted: {uptime_since}\n",
    ]

    output_list[1] = output_list[1] = (
        output_list[1]
        + " " * max(0, 35 - len(output_list[1]))
        + f"| Procs: {data['entities']['active']} active, {data['entities']['total']} total"
    )

    return "".join(output_list)


def end():
    """
    clean up when the program exits
    """

    loadavg_class.close_files()


if __name__ == "__main__":
    main()
