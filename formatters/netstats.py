from plugins.netstats import Plugin
from misc.utils import to_bytes, convert_bytes

netstats_plugin = Plugin()


def get_lines():
    data = netstats_plugin.get_data()
    lines = [f"  --- /sys/class/net {'-' * 46}"]
    
    lines.append(f"   Local IP: {data.ip:<15} | Interface: {data.name}")
    lines.append(f"   Download: {convert_bytes(data.transfer_statistics.speeds.received):<13} (Total: {convert_bytes(data.transfer_statistics.total_received)}, {data.transfer_statistics.total_received} bytes)")
    lines.append(f"     Upload: {convert_bytes(data.transfer_statistics.speeds.transferred):<13} (Total: {convert_bytes(data.transfer_statistics.total_transferred)}, {data.transfer_statistics.total_transferred} bytes)")
    
    return lines


def close_files():
    netstats_plugin.close_files()
