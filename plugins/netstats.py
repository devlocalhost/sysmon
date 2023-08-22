#!/usr/bin/env python3

"""netstats plugin for sysmon"""

import os
import sys
import fcntl
import socket
import struct

from .extra import (
    en_open,
    char_padding,
    convert_bytes,
    detect_network_adapter,
    SAVE_DIR,
)


def main():
    """/sys/class/net/ - network stats, and speed"""

    adapter_directory = detect_network_adapter()


    if adapter_directory is not None:
        device_name = adapter_directory.split("/")[4]
        if not os.path.isfile(f"{SAVE_DIR}/rx") and not os.path.isfile(f"{SAVE_DIR}tx"):
            with en_open(f"{SAVE_DIR}/rx", "w") as rx_file:
                rx_file.write("0")

            with en_open(f"{SAVE_DIR}/tx", "w") as tx_file:
                tx_file.write("0")

        try:
            with en_open(adapter_directory + "/statistics/rx_bytes") as received:
                received = received.read().strip()

            with en_open(adapter_directory + "/statistics/tx_bytes") as transferred:
                transferred = transferred.read().strip()

            with en_open(f"{SAVE_DIR}/rx") as recv_speed:
                recv_speed = abs(int(recv_speed.read().strip()) - int(received))

        except FileNotFoundError:
            sys.exit(f'Network interface "{device_name}" not found')

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
        local_ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack("256s", device_name[:15].encode("UTF-8")))[20:24])


        return (
            f"  --- /sys/class/net/{device_name} {char_padding('-', (45 - len(device_name)))}\n"
            f"      Local IP: {local_ip}\n"
            f"      Received: {human_received}"
            + char_padding(" ", (14 - len(human_received)))
            + f"({received} bytes)\n"
            f"   Transferred: {human_transferred}"
            + char_padding(" ", (14 - len(human_transferred)))
            + f"({transferred} bytes)\n"
            f"         Speed: Down {convert_bytes(recv_speed)}"
            + char_padding(" ", (14 - len(convert_bytes(recv_speed))))
            + f"| Up {convert_bytes(transf_speed)}\n"
        )

    return f"  --- /sys/class/net/!?!? {char_padding('-', 41)}\n"
