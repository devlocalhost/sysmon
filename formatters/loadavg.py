from datetime import datetime

from plugins.loadavg import Plugin

loadavg_plugin = Plugin()


# crazy name, i know.
def _dynamicallyAddTheLetterSForTheFormatSecondsFunction(value, unit):
    return f"{value} {unit}" if value == 1 else f"{value} {unit}s"


def _format_seconds(seconds):
    wk, remainder = divmod(seconds, 7 * 24 * 3600)
    ds, remainder = divmod(remainder, 24 * 3600)
    hr, remainder = divmod(remainder, 3600)
    mn, sec = divmod(remainder, 60)

    fmted = [] # formatted output

    if wk:
        fmted.append(_dynamicallyAddTheLetterSForTheFormatSecondsFunction(wk, "week"))

    if ds:
        fmted.append(_dynamicallyAddTheLetterSForTheFormatSecondsFunction(ds, "day"))

    if hr:
        fmted.append(_dynamicallyAddTheLetterSForTheFormatSecondsFunction(hr, "hour"))

    if mn:
        fmted.append(_dynamicallyAddTheLetterSForTheFormatSecondsFunction(mn, "minute"))

    if sec or not fmted:
        fmted.append(_dynamicallyAddTheLetterSForTheFormatSecondsFunction(sec, "second"))

    return ", ".join(fmted)


def get_lines():
    data = loadavg_plugin.get_data()

    lines = [f"  --- /proc/loadavg {'-' * 47}"]

    lines.append(f"     Load: {data.load_times.OneMin} {data.load_times.FiveMin} {data.load_times.FifteenMin}")
    lines.append(f"   Uptime: {_format_seconds(data.uptime.Seconds)}")
    lines.append(f"   Booted: {datetime.fromtimestamp(data.uptime.Timestamp).strftime('%A, %B %d %Y, %I:%M:%S %p')}")

    lines[1] = (
        lines[1] + " " * max(0, 35 - len(lines[1]))
        + f"| Procs: {data.entities.Active} active, {data.entities.Total} total"
    )

    return lines


def close_files():
    loadavg_plugin.close_files()
