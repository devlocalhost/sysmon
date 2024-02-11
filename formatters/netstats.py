#!/usr/bin/env python3

"""
formatter for netstats plugin
"""

from util.util import convert_bytes
from plugins import netstats

netstats_class = netstats.Netstats()

def main():
    """
    returns the data, but formatted.
    """

    data = netstats_class.get_data()

    device_name = data["interface"]

    if device_name:
        local_ip = data["local_ip"]
        human_received = convert_bytes(data["statistics"]["received"])
        human_transferred = convert_bytes(data["statistics"]["transferred"])
        human_received_speed = convert_bytes(
            data["statistics"]["speeds"]["received"]
        )
        human_transferred_speed = convert_bytes(
            data["statistics"]["speeds"]["transferred"]
        )

        return (
            f"  ——— /sys/class/net {'—' * (52 - len(device_name))}\n"
            f"      Local IP: {local_ip}{' ' * max(15 - len(local_ip), 0)} | Interface: {device_name}\n"
            f"      Received: {human_received}"
            + " " * (14 - len(human_received))
            + f"({human_received} bytes)\n"
            f"   Transferred: {human_transferred}"
            + " " * (14 - len(human_transferred))
            + f"({human_transferred} bytes)\n"
            f"         Speed: Down {human_received_speed}"
            + " " * (14 - len(human_received_speed))
            + f"| Up {human_transferred_speed}\n"
        )

    return f"  ——— /sys/class/net/!?!? {'—' * 41}\n"


if __name__ == "__main__":
    main()