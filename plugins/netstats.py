from utils.util import en_open

def _interface_is_not_blacklisted(interface_name):
    """
    checks if a interface is not 'valid'
    """

    blacklist = [768, 769, 770, 771, 772, 777, 778, 779, 783, 65534]

    with en_open(f"/sys/class/net/{interface_name}/type") as device_type:
        return int(device_type.read()) not in blacklist


def _interface_is_up(interface_name):
    """
    check if interface is up
    """

    with en_open(f"/sys/class/net/{interface_name}/operstate") as device_status:
        return device_status.read().strip() == "up"


def get_current_interface():
    """
    detect which interface is being used right now
    """

    interfaces = []

    # first check: kernel routing
    with en_open("/proc/net/route") as proc_net:
        for iface in proc_net.readlines()[1:]:
            # Iface	Destination	Gateway 	Flags
            # 'wlan0', '00000000', 'FE01A8C0', '0003', '0', '0', '600', '00000000', '0', '0', '0'
            interface_data = iface.strip().split("\t")

            if interface_data[1] == "00000000": # this means default route, which is what we want
                if int(interface_data[3], 16) >= 2: 
                    # more than 2 bits means destination is a gateway, we want that
                    # !!  BUT  !! what if its more than 2? if it was 3, that would be fine
                    # !!  BUT  !! what if its more than 4? 5? 6? is it still valid?
                    interfaces.append(interface_data[0])

    # additional check: sysfs
    for interface in interfaces:
        if _interface_is_not_blacklisted(interface) and _interface_is_up(interface):
            return interface

    return None # nothing found


print(get_current_interface())
