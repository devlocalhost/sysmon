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
    SAVE_DIR,
    INTERFACE,
    SHOW_LOCAL_IP,
)
from util.logger import setup_logger


def interface_is_not_blacklisted(iface):
    """checks if a interface is not 'valid'"""

    blacklist = [768, 769, 770, 771, 772, 777, 778, 779, 783]

    with en_open(iface + "/type") as device_type:
        return int(device_type.read()) not in blacklist


def interface_is_up(iface):
    """check if interface is up"""

    with en_open(iface + "/operstate") as status:
        return status.read().strip() == "up"


def find_active_interface():
    """get active interface"""

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
    """Detect an active network interface and return its directory"""

    if INTERFACE is None:
        result = find_active_interface()

        if result:
            logger.debug(f"[net] using iface {result[2]}")
            return result

        return None

    logger.debug(f"[net] using custom iface {INTERFACE}")

    return (
        f"/sys/class/net/{INTERFACE}/statistics/rx_bytes",
        f"/sys/class/net/{INTERFACE}/statistics/tx_bytes",
        INTERFACE,
    )


class Speed:
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

        self.rx_file = en_open(net_save[0])
        self.tx_file = en_open(net_save[1])

        self.logger.debug("[open] net_save")

        self.files_opened = [self.rx_file, self.tx_file]
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
        iface_device = get_network_interface()

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

        if iface_device is not None:
            interface_name = iface_device[2]

            rx = recv_file.read().strip()
            tx = transf_file.read().strip()

            rx_speed = abs(speed_track.rx - int(received))
            tx_speed = abs(speed_track.tx - int(transferred))

            speed_track.set_values(received, transferred)

            # https://stackoverflow.com/a/27494105

            # bad name...?
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            if SHOW_LOCAL_IP:
                try:
                    local_ip = socket.inet_ntoa(
                        fcntl.ioctl(
                            s.fileno(),
                            0x8915,
                            struct.pack("256s", device_name[:15].encode("UTF-8")),
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


        #     logger.debug("[data] print out")

        #     return (
        #         f"  ——— /sys/class/net {'—' * (52 - len(device_name))}\n"
        #         f"      Local IP: {local_ip}{' ' * max(15 - len(local_ip), 0)} | Interface: {device_name}\n"
        #         f"      Received: {human_received}"
        #         + " " * (14 - len(human_received))
        #         + f"({received} bytes)\n"
        #         f"   Transferred: {human_transferred}"
        #         + " " * (14 - len(human_transferred))
        #         + f"({transferred} bytes)\n"
        #         f"         Speed: Down {convert_bytes(recv_speed)}"
        #         + " " * (14 - len(convert_bytes(recv_speed)))
        #         + f"| Up {convert_bytes(transf_speed)}\n"
        #     )

        # return f"  ——— /sys/class/net/!?!? {'—' * 41}\n"
