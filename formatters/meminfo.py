from plugins.meminfo import Plugin
from misc.utils import to_bytes, convert_bytes

meminfo_plugin = Plugin()


def get_lines():
    data = meminfo_plugin.get_data()

    left = [
        "   RAM:",
        f"       Total: {convert_bytes(data.physical_values.MemTotal)}",
        f"        Used: {convert_bytes(data.physical_values.Used)} ({data.physical_percentages.Used}%)",
        f"   Available: {convert_bytes(data.physical_values.MemAvailable)} ({data.physical_percentages.Available}%)",
    ]
    right = [
        "",
        f"    Free: {convert_bytes(data.physical_values.MemFree)} ({data.physical_percentages.Free}%)",
        f"Ac. Used: {convert_bytes(data.physical_values.ActualUsed)} ({data.physical_percentages.ActualUsed}%)",
        f"  Cached: {convert_bytes(data.physical_values.Cached)} ({data.physical_percentages.Cached}%)",
    ]

    lines = [f"  --- /proc/meminfo {'-' * 47}"]

    for l, r in zip(left, right):
        lines.append(f"{l:<38}{r}")

    return lines


def close_files():
    meminfo_plugin.close_files()
