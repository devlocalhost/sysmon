from plugins.procs import Plugin
from misc.utils import to_bytes, convert_bytes

procs_plugin = Plugin()


def get_lines():
    data = procs_plugin.get_data()
    lines = [f"  --- /proc/pid/status {'-' * 44}"]
    lines.append("   Process ID Process name                VmRSS         State")

    for process in data:
        lines.append(f"   {process.PID:>10} {process.Name:<28}{convert_bytes(process.VmRSS):<14}{process.State}")

    return lines


def close_files():
    procs_plugin.close_files()
