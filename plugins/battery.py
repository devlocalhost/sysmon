#!/usr/bin/env python3

"""battery plugin for sysmon"""

import os
import glob

from util.util import en_open
from util.logger import setup_logger


def detect_battery():
    """
    detect which supply from
    /sys/class/power_supply is a battery
    """

    for supply in glob.glob("/sys/class/power_supply/*"):
        with en_open(os.path.join(supply, "type")) as supply_type:
            if supply_type.read().strip().lower() == "battery":
                return supply

    return None


class Battery:
    """
    Battery class - get power supply details

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

        self.battery_directory = detect_battery()
        self.logger.debug(f"[init] battery_directory: {self.battery_directory}")

        self.files_opened = []
        files_to_open = ["capacity", "status", "voltage_now", "current_now", "technology", "model_name", "manufacturer", "cycles_count"]
        
        if self.battery_directory:
            # try:
            self.capacity = en_open(os.path.join(self.battery_directory, "capacity"))
            self.status = en_open(os.path.join(self.battery_directory, "status"))
            self.voltage_now = en_open(os.path.join(self.battery_directory, "voltage_now"))
            self.current_now = en_open(os.path.join(self.battery_directory, "current_now"))
            self.technology = en_open(os.path.join(self.battery_directory, "technology"))
            self.model_name = en_open(os.path.join(self.battery_directory, "model_name"))
            self.manufacturer = en_open(os.path.join(self.battery_directory, "manufacturer"))
            # self.cycles_count = en_open(os.path.join(self.battery_directory, "cycles_count"))

            self.files_opened.append(self.capacity)
            self.files_opened.append(self.status)
            self.files_opened.append(self.voltage_now)
            self.files_opened.append(self.current_now)
            self.files_opened.append(self.technology)
            self.files_opened.append(self.model_name)
            self.files_opened.append(self.manufacturer)
            # self.files_opened.append(self.cycles_count)

            # except (FileNotFoundError, AttributeError):
            #     pass

        self.logger.debug(f"[init] files_opened: {self.files_opened}")

    
    def close_files(self):
        """
        closing the opened files. always call this
        when ending the program
        """

        for file in self.files_opened:
            try:
                self.logger.debug(f"[close_files] {file.name}")
                file.close()

            except:
                pass

    def get_data(self):
        """
        returns a json dict with data
        """ 

        # data = {
        #     "status": "Unknown",
        #     "type": "Unknown",
        #     "technology": "Unknown",
        #     "cycles": "Unknown",
        #     "now": {
        #         "charge": "Unknown",
        #         "voltage": "Unknown",
        #         "current": "Unknown",
        #     },
        #     "capacity": "Unknown",
        #     "model": "Unknown",
        #     "manufacturer": "Unknown",
        # }

        data = {
            "supply": "Unknown",
            "capacity": "Unknown",
            "status": "Unknown",
            "voltage": "Unknown",
            "current": "Unknown",
            "technology": "Unknown",
            "model_name": "Unknown",
            "manufacturer": "Unknown",
            "cycles_count": "Unknown"
        }

        if self.battery_directory:
            for file in self.files_opened:
                file.seek(0)
                
            data["supply"] = self.battery_directory.split("/")[-1:][0]
            data["capacity"] = self.capacity.read().strip()
            data["status"] = self.status.read().strip()
            data["voltage"] = int(self.voltage_now.read().strip()) / 1000
            data["current"] = int(self.current_now.read().strip()) / 1000
            data["technology"] = self.technology.read().strip()
            data["model_name"] = self.model_name.read().strip()
            data["manufacturer"] = self.manufacturer.read().strip()
            # data["cycles_count"] = self.cycles_count.read().strip()

        self.logger.debug("[get_data] return data")

        return data
