#!/usr/bin/env python3

"""netstats plugin for sysmon"""

import os
import fcntl
import glob
import socket
import struct

from util.util import (
    en_open,
    convert_bytes,
    INTERFACE,
    SHOW_LOCAL_IP,
)
from util.logger import setup_logger


def interface_is_not_blacklisted(iface):
    """
    checks if a interface is not 'valid'
    """

    blacklist = [768, 769, 770, 771, 772, 777, 778, 779, 783]

    with en_open(iface + "/type") as device_type:
        return int(device_type.read()) not in blacklist


def interface_is_up(iface):
    """
    check if interface is up
    """

    with en_open(iface + "/operstate") as status:
        return status.read().strip() == "up"


def find_active_interface():
    """
    get active interface
    """

    for iface in glob.glob("/sys/class/net/*"):
        if (
            os.path.isdir(iface)
            and interface_is_not_blacklisted(iface)
            and interface_is_up(iface)
        ):
            return (
                f"{iface}/statistics/rx_bytes",
                f"{iface}/statistics/tx_bytes",
                iface.split("/")[4],
            )

    return None


def get_network_interface():
    """
    Detect an active network interface and return its directory
    """

    if INTERFACE is None:
        result = find_active_interface()

        if result:
            return result

        return None

    return (
        f"/sys/class/net/{INTERFACE}/statistics/rx_bytes",
        f"/sys/class/net/{INTERFACE}/statistics/tx_bytes",
        INTERFACE,
    )


class Speed:
    """
    calculate internet speed
    """

    def __init__(self):
        self.rx = 0
        self.tx = 0

    def set_values(self, rx, tx):
        self.rx = int(rx)
        self.tx = int(tx)


class Netstats:
    """
    Netstats class - get network stats and speed

    Usage:
        call get_data() to get data
            returns dict

    DO:
        NOT CALL print_data(). That function
    is intended to be used by sysmon. (might change in the future...?)
        CALL close_files() when your program ends
        to avoid opened files
    """

    def __init__(self):
        """
        initializing important stuff
        """

        self.logger = setup_logger(__name__)

        self.logger.debug("[init] initializing")

        self.interface = get_network_interface()

        if self.interface:
            self.rx_file = en_open(self.interface[0])
            self.tx_file = en_open(self.interface[1])

            self.files_opened = [self.rx_file, self.tx_file]

        self.logger.debug("[open] net_save")

        self.speed_track = Speed()

    def close_files(self):
        """
        closing the opened files. always call this
        when ending the program
        """

        for file in self.files_opened:
            self.logger.debug(f"[close] {file.name}")
            file.close()

    def get_data(self):
        """
        returns a json dict with data
        """

        data = {
            "interface": None,
            "local_ip": None,
            "statistics": {
                "received": None,
                "transferred": None,
                "speeds": {
                    "received": None,
                    "transferred": None,
                },
            },
        }

        if self.interface is not None:
            interface_name = self.interface[2]

            self.rx_file.seek(0)
            self.tx_file.seek(0)

            rx = int(self.rx_file.read().strip())
            tx = int(self.tx_file.read().strip())

            rx_speed = abs(self.speed_track.rx - rx)
            tx_speed = abs(self.speed_track.tx - tx)

            self.speed_track.set_values(rx, tx)

            # https://stackoverflow.com/a/27494105
            create_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            if SHOW_LOCAL_IP:
                try:
                    local_ip = socket.inet_ntoa(
                        fcntl.ioctl(
                            create_socket.fileno(),
                            0x8915,
                            struct.pack("256s", interface_name[:15].encode("UTF-8")),
                        )[20:24]
                    )

                except OSError:
                    local_ip = "!?!?"

            else:
                local_ip = "Hidden"

            data["interface"] = interface_name
            data["local_ip"] = local_ip
            data["statistics"]["received"] = rx
            data["statistics"]["transferred"] = tx
            data["statistics"]["speeds"]["received"] = rx_speed
            data["statistics"]["speeds"]["transferred"] = tx_speed

        return data

    def print_data(self):
        """
        returns the data, but formatted.
        not intended to be used, please
        use get_data() instead
        """

        data = self.get_data()

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
