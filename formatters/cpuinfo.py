from plugins.cpuinfo import Plugin
from misc.utils import to_bytes, convert_bytes


cpuinfo_plugin = Plugin()


def get_lines():
    data = cpuinfo_plugin.get_data()
    lines = []

    lines.append(f"  --- /proc/cpuinfo {'-' * 47}")
    lines.append(
        f"   Usage: {data.utilization:>5}% {data.temperature:>5} °C | {data.architecture} {data.model} @ {round(data.average_frequency / 1000):>4} MHz"
    )
    lines.append(
        f"   Cores: {data.physical_cores}C/{data.logical_cores}T | Freq range: {round(data.frequency_min / 1000)}..{round(data.frequency_max / 1000)} MHz | Cache: {data.cache_level} {convert_bytes(to_bytes(data.cache_size))}"
    )

    return lines


def close_files():
    cpuinfo_plugin.close_files()
