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

    if device_name and data["local_ip"] != "!?!?":
        # the above local_ip check is a workaround so netstats updates the output
        # when youre using sysmon, and your internet connection goes down or up

        local_ip = data["local_ip"]
        raw_received = data["statistics"]["received"]
        raw_transferred = data["statistics"]["transferred"]

        human_received = convert_bytes(raw_received)
        human_transferred = convert_bytes(raw_transferred)
        
        human_received_speed = convert_bytes(data["statistics"]["speeds"]["received"])
        human_transferred_speed = convert_bytes(
            data["statistics"]["speeds"]["transferred"]
        )

        return (
            f"  ——— /sys/class/net {'—' * (52 - len(device_name))}\n"
            f"      Local IP: {local_ip}{' ' * max(15 - len(local_ip), 0)} | Interface: {device_name}\n"
            f"      Received: {human_received}"
            + " " * (14 - len(human_received))
            + f"({raw_received} bytes)\n"
            f"   Transferred: {human_transferred}"
            + " " * (14 - len(human_transferred))
            + f"({raw_transferred} bytes)\n"
            f"         Speed: Down {human_received_speed}"
            + " " * (14 - len(human_received_speed))
            + f"| Up {human_transferred_speed}\n"
        )

    return f"  ——— /sys/class/net/!?!? {'—' * 41}\n"


if __name__ == "__main__":
    main()
