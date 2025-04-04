#!/usr/bin/env python3

"""fan plugin for sysmon"""

import os
import glob

from util.util import en_open
from util.logger import setup_logger

# TODO: rename to sensors, and make this plugin fetch
#       other sensor details, like battery too?

def detect_fans():
    hwmon_dirs = glob.glob("/sys/class/hwmon/*")

    # the fans list
    fans = []
    
    # each dir has (?) a /name file. only the dirs with the names below are correct
    fan_names = ["dell_ddv"]

    for hwmon in hwmon_dirs:
        with en_open(os.path.join(hwmon, "name")) as hwmon_name:
            if hwmon_name.read().strip() in fan_names:
                fans.append(hwmon)

    return fans

class Fans:
    def __init__(self):
        self.logger = setup_logger(__name__)

        self.logger.debug("[init] initializing")

        self.fan_paths = detect_fans()

    def get_data(self):
        fan_data = []
        
        for fan in self.fan_paths:
            fan_input_file = glob.glob(os.path.join(fan, "fan*_input"))
            fan_label_file = glob.glob(os.path.join(fan, "fan*_label"))

            fan_data.append({"input": fan_input_file, "label": fan_label_file})
    
        data = {"data": fan_data}

        return data
