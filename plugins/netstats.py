#!/usr/bin/env python3

"""netstats plugin for sysmon"""

import os
import sys
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
    open_readonly,
)
from util.logger import setup_logger

logger = setup_logger(__name__)


def detect_network_adapter():
    """detect an active network adapter/card/whatever and return its directory"""

    if INTERFACE is None:
        for iface in glob.glob("/sys/class/net/*"):
            with en_open(iface + "/type") as device_type:
                if int(device_type.read()) != 772:  # if not loopback device
                    with en_open(iface + "/operstate") as status:
                        if status.read().strip() == "up":
                            logger.info("[open ->] open net dev")

                            return (
                                open_readonly(f"{iface}/statistics/rx_bytes"),
                                open_readonly(f"{iface}/statistics/tx_bytes"),
                                iface.split("/")[4],
                            )
        return None

    logger.info("[open ->] open cust net dev")

    return (
        open_readonly(f"/sys/class/net/{INTERFACE}/statistics/rx_bytes"),
        open_readonly(f"/sys/class/net/{INTERFACE}/statistics/tx_bytes"),
        INTERFACE,
    )


iface_device = detect_network_adapter()


def main():
    """/sys/class/net/ - network stats, and speed"""

    if iface_device is not None:
        device_name = iface_device[2]

        if not os.path.isfile(f"{SAVE_DIR}/rx") and not os.path.isfile(f"{SAVE_DIR}tx"):
            with en_open(f"{SAVE_DIR}/rx", "w") as rx_file:
                rx_file.write("0")

            with en_open(f"{SAVE_DIR}/tx", "w") as tx_file:
                tx_file.write("0")

        recv_file = iface_device[0]
        transf_file = iface_device[1]
        recv_file.seek(0)
        transf_file.seek(0)

        received = recv_file.read().strip()
        transferred = transf_file.read().strip()

        logger.info("[read <-] net dev")

        with en_open(f"{SAVE_DIR}/rx") as recv_speed:
            recv_speed = abs(int(recv_speed.read().strip()) - int(received))

        with en_open(f"{SAVE_DIR}/tx") as transf_speed:
            transf_speed = abs(int(transf_speed.read().strip()) - int(transferred))

        with en_open(f"{SAVE_DIR}/rx", "w") as rxsave:
            rxsave.write(received if len(received) != 0 else "0")

        with en_open(f"{SAVE_DIR}/tx", "w") as txsave:
            txsave.write(transferred if len(transferred) != 0 else "0")

        human_received = convert_bytes(int(received))
        human_transferred = convert_bytes(int(transferred))

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

        logger.info("[ out >>] net dev")

        return (
            f"  ——— /sys/class/net {'—' * (52 - len(device_name))}\n"
            f"      Local IP: {local_ip}{' ' * max(15 - len(local_ip), 0)} | Interface: {device_name}\n"
            f"      Received: {human_received}"
            + " " * (14 - len(human_received))
            + f"({received} bytes)\n"
            f"   Transferred: {human_transferred}"
            + " " * (14 - len(human_transferred))
            + f"({transferred} bytes)\n"
            f"         Speed: Down {convert_bytes(recv_speed)}"
            + " " * (14 - len(convert_bytes(recv_speed)))
            + f"| Up {convert_bytes(transf_speed)}\n"
        )

    return f"  ——— /sys/class/net/!?!? {'—' * 41}\n"
