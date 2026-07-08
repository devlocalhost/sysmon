from plugins.procs import Plugin
from misc.utils import to_bytes, convert_bytes

procs_plugin = Plugin()


def get_lines():
    data = procs_plugin.get_data()

    pnl = [] # save length of proc names
    for proc in data:
        pnl.append(len(proc.Name))
        
    lpnl = int(max(pnl) + 1) # longest proc name length, the length of the longest proc name
    lpidl = 7 # longest pid length, this is a default fallback value

    with open("/proc/sys/kernel/pid_max", encoding="utf-8") as pid_max:
        lpidl = len(pid_max.read().strip())
        
    lines = [f"  --- /proc/pid/status {'-' * 44}"]
    lines.append(f"{' ' * lpidl}PID Name {' ' * (lpnl - 5)}VmRSS         State")

    for process in data:
        lines.append(f"   {process.PID:>{lpidl}} {process.Name:<{lpnl}}{convert_bytes(process.VmRSS):<14}{process.State}")

    return lines


def close_files():
    procs_plugin.close_files()
