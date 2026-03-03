from dataclasses import dataclass

from plugins.base import BasePlugin
from utils.util import en_open




class NetstatsPlugin(BasePlugin):
    def __init__(self):
        super().__init__()

        self.logger.debug("initialize plugin")

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
            
            self.logger.debug(f"interface {interface_name} operstate {device_status_str}")
            return device_status_str == "up"


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

                self.logger.debug(f"got interface: {interface_data}")

                if interface_data[1] == "00000000": # this means default route, which is what we want
                    if int(interface_data[3], 16) >= 2: 
                        # more than 2 bits means destination is a gateway, we want that
                        # !!  BUT  !! what if its more than 2? if it was 3, that would be fine
                        # !!  BUT  !! what if its more than 4? 5? 6? is it still valid?
                        interfaces.append(interface_data[0])

        # additional check: sysfs
        for interface in interfaces:
            if self._interface_is_not_blacklisted(interface) and self._interface_is_up(interface):
                self.logger.debug(f"interface {interface} passes all checks")
                return interface
                # maybe its not a good idea to return the first result
                # but all of them, then choose randomly? idk

        self.logger.debug("nothing found?")
        return None # nothing found

    def get_data(self):
        return self.get_current_interface()
