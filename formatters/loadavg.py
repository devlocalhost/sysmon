from datetime import datetime

from plugins.loadavg import Plugin

loadavg_plugin = Plugin()

# crazy name, i know.
def _dynamicallyAddTheLetterSForTheFormatSecondsFunction(value, unit):
    return f"{value} {unit}" if value == 1 else f"{value} {unit}s"

def _format_seconds(seconds):
    wk, remainder = divmod(seconds, 7 * 24 * 3600)
    hr, remainder = divmod(remainder, 3600)
    min, sec = divmod(remainder, 60)

    format = []

    if wk:
        format.append(_dynamicallyAddTheLetterSForTheFormatSecondsFunction(wk, "week"))

    if hr:
        format.append(_dynamicallyAddTheLetterSForTheFormatSecondsFunction(hr, "hour"))

    if min:
        format.append(_dynamicallyAddTheLetterSForTheFormatSecondsFunction(min, "minute"))

    if sec or not format:
        format.append(_dynamicallyAddTheLetterSForTheFormatSecondsFunction(sec, "second"))

    return ", ".join(format)

def get_lines():
    data = loadavg_plugin.get_data()

    lines = [f"  --- /proc/loadavg {'-' * 47}"]

    lines.append(f"     Load: {data.load_times.OneMin} {data.load_times.FiveMin} {data.load_times.FifteenMin}")
    lines.append(f"   Uptime: {_format_seconds(data.uptime.Seconds)}")
    lines.append(f"   Booted: {datetime.fromtimestamp(data.uptime.Timestamp).strftime('%A, %B %d %Y, %I:%M:%S %p')}")

    lines[1] = lines[1] + " " * max(0, 35 - len(lines[1])) + f"| Procs: {data.entities.Active} active, {data.entities.Total} total"
    
    return lines

def close_files():
    loadavg_plugin.close_files()
