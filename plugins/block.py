#!/usr/bin/env python3

"""block plugin for sysmon"""

import os
import sys
import glob

from util.util import en_open, DEVICE
from util.logger import setup_logger


def detect_active_drive():
    if DEVICE is None:
        devices = []
        active_devices = []

        for device in glob.glob("/sys/block/*/device"):
            if os.path.exists(os.path.join(device, "state")):
                devices.append(device)

        for device in devices:
            with en_open(os.path.join(device, "state")) as device_state:
                if device_state.read().strip() == "running":
                    active_devices.append(device)

        return os.path.dirname(active_devices[0])

    return DEVICE


class Speed:
    """
    track r/w speed
    """

    def __init__(self):
        self.read = 0
        self.write = 0

    def set_values(self, read, write):
        """
        set read and write values
        """

        self.read = int(read)
        self.write = int(write)


class Block:
    """
    Block class - get statistics about disk device

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
        self.tracker = Speed()

        self.drive = detect_active_drive()

        try:
            self.drive_stat_file = en_open(os.path.join(self.drive, "stat"))

        except FileNotFoundError:
            sys.exit(
                f'Drive "{self.drive}" does not exist. Report this issue, double check device argument (if passed), or disable this plugin (--noblock)'
            )

        self.files_opened = [self.drive_stat_file]

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

        for file in self.files_opened:
            self.logger.debug(f"[get_data] {file.name}")
            file.seek(0)

        drive_stats = self.drive_stat_file.read().split()
        model = None

        readio, readsect, writeio, writesect = (
            int(drive_stats[0]),
            int(drive_stats[2]),
            int(drive_stats[4]),
            int(drive_stats[6]),
        )

        readsect_conv, writesect_conv = readsect * 512, writesect * 512
        readsect_speed, writesect_speed = (
            abs(self.tracker.read - readsect_conv),
            abs(self.tracker.write - writesect_conv),
        )

        self.tracker.set_values(readsect_conv, writesect_conv)

        try:
            with en_open(os.path.join(self.drive, "device/model")) as drive_model:
                model = drive_model.read().strip()

        except Exception:
            pass

        data = {
            "drive": {
                "name": self.drive,
                "model": model,
            },
            "io": {
                "read": readio,
                "write": writeio,
            },
            "sectors": {
                "read": readsect,
                "write": writesect,
                "speed": {
                    "read": readsect_speed,
                    "write": writesect_speed,
                },
            },
        }

        return data
