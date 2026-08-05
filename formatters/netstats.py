from plugins.netstats import Plugin
from misc.utils import to_bytes, convert_bytes

netstats_plugin = Plugin()


def get_lines():
    data = netstats_plugin.get_data()
    lines = [f"  --- /sys/class/net {'-' * 46}"]
    
    lines.append(f"   Local IP: {data.ip:<15} | Interface: {data.name}")
    lines.append(f"   Total: Down {convert_bytes(data.transfer_statistics.total_received):<13} | Up {convert_bytes(data.transfer_statistics.total_transferred)}")
    lines.append(f"    Rate: Down {convert_bytes(data.transfer_statistics.speeds.received):<13} | Up {convert_bytes(data.transfer_statistics.speeds.transferred)}")
    
    return lines


def close_files():
    netstats_plugin.close_files()
