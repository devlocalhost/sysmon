import os
import fcntl
import socket
import struct

from dataclasses import dataclass

from plugins.base import BasePlugin
from utils.util import en_open


@dataclass
class InterfaceDetails:
    name: str = "!?!?"
    directory: str = "!?!?"
    rx_bytes_file: str = None
    tx_bytes_file: str = None


@dataclass
class TransferSpeeds:
    received: int = 0
    transferred: int = 0


@dataclass
class TransferStatistics:
    total_received: int = 0
    total_transferred: int = 0
    speeds: TransferSpeeds = None


@dataclass
class NetstatsData:
    name: str = "!?!?"
    ip: str = "!?!?"
    transfer_statistics: TransferStatistics = None


class _TrackTranferSpeeds:
    def __init__(self):
        self.rx = 0
        self.tx = 0

    def update_values(self, rx, tx):
        self.rx = rx
        self.tx = tx


class NetstatsPlugin(BasePlugin):
    def __init__(self):
        super().__init__()

        self.logger.debug("initialize plugin")
        self.interface_data = self.get_current_interface()

        try:
            self._rx_file = en_open(self.interface_data.rx_bytes_file)
            self._tx_file = en_open(self.interface_data.tx_bytes_file)

            self.opened_files.append(self._rx_file)
            self.opened_files.append(self._tx_file)
            self.logger.debug("opened rx and tx files")

        except Exception as exc:
            self.logger.debug(f"could not open files: {exc}")

        self.transfer_speed_track = _TrackTranferSpeeds()

    def _interface_is_not_blacklisted(self, interface_name):
        """
        checks if a interface is not 'valid'
        """

        blacklist = [768, 769, 770, 771, 772, 777, 778, 779, 783, 65534]

        with en_open(f"/sys/class/net/{interface_name}/type") as device_type:
            device_type_int = int(device_type.read())

            self.logger.debug(f"interface {interface_name} type {device_type_int}")
            return device_type_int not in blacklist

    def _interface_is_up(self, interface_name):
        """
        check if interface is up
        """

        with en_open(f"/sys/class/net/{interface_name}/operstate") as device_status:
            device_status_str = device_status.read().strip()

            self.logger.debug(
                f"interface {interface_name} operstate {device_status_str}"
            )
            return device_status_str == "up"

    def _get_interface_ip(self, interface_name):
        # https://stackoverflow.com/a/27494105
        create_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            local_ip = socket.inet_ntoa(
                fcntl.ioctl(
                    create_socket.fileno(),
                    0x8915,
                    struct.pack("256s", interface_name[:15].encode("UTF-8")),
                )[20:24]
            )

        except OSError:
            pass

        return local_ip

    def get_current_interface(self):
        """
        detect which interface is being used right now
        """

        interfaces = []

        # first check: kernel routing
        with en_open("/proc/net/route") as proc_net:
            for iface in proc_net.readlines()[1:]:
                # Iface	Destination	Gateway 	Flags
                # 'wlan0', '00000000', 'FE01A8C0', '0003', '0', '0', '600', '00000000', '0', '0', '0'
                interface_data = iface.strip().split("\t")[:4]

                self.logger.debug(f"found interface: {interface_data}")

                if (
                    interface_data[1] == "00000000"
                ):  # this means default route, which is what we want
                    if int(interface_data[3], 16) >= 2:
                        # more than 2 bits means destination is a gateway, we want that
                        # !!  BUT  !! what if its more than 2? if it was 3, that would be fine
                        # !!  BUT  !! what if its more than 4? 5? 6? is it still valid?
                        interfaces.append(interface_data[0])

        # additional check: sysfs
        for interface in interfaces:
            interface_dir = f"/sys/class/net/{interface}"
            interface_statistics_dir = f"{interface_dir}/statistics"
            interface_rx_bytes = f"{interface_statistics_dir}/rx_bytes"
            interface_tx_bytes = f"{interface_statistics_dir}/tx_bytes"

            try:
                if (
                    self._interface_is_not_blacklisted(interface)
                    and self._interface_is_up(interface)
                    and os.listdir(interface_dir)
                    and os.listdir(interface_statistics_dir)
                    and os.stat(interface_rx_bytes)
                    and os.stat(interface_tx_bytes)
                ):
                    self.logger.debug(f"interface {interface} passes all checks")
                    return InterfaceDetails(
                        name=interface,
                        directory=interface_dir,
                        rx_bytes_file=interface_rx_bytes,
                        tx_bytes_file=interface_tx_bytes,
                    )  # then return interface name

                    # maybe its not a good idea to return the first result
                    # but all of them, then choose randomly? idk

                    # and maybe i should return interface
                    # anyway if statistics dir doesnt exist?

            except FileNotFoundError as exc:
                self.logger.debug(
                    f"one of the checks has failed. check if statistics dir and rx/tx_bytes files exist for {interface}. {exc}"
                )
                return None

        self.logger.debug("nothing found?")
        return None

    def get_data(self):
        self.seek_files()

        transfer_speeds = TransferSpeeds()

        current_rx_bytes = int(self._rx_file.read().strip())
        current_tx_bytes = int(self._tx_file.read().strip())

        rx_speed = abs(self.transfer_speed_track.rx - current_rx_bytes)
        tx_speed = abs(self.transfer_speed_track.tx - current_tx_bytes)

        self.transfer_speed_track.update_values(current_rx_bytes, current_tx_bytes)

        return NetstatsData(
            name=self.interface_data.name,
            ip=self._get_interface_ip(self.interface_data.name),
            transfer_statistics=TransferStatistics(
                total_received=current_rx_bytes,
                total_transferred=current_tx_bytes,
                speeds=TransferSpeeds(
                    received=rx_speed,
                    transferred=tx_speed,
                ),
            ),
        )
