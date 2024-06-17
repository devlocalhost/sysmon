#!/usr/bin/env python3

"""
formatter for battery plugin
"""

from plugins import battery

battery_class = battery.Battery()


def main():
    """
    returns the data, but formatted.
    """

    data = battery_class.get_data()

    return f"  --- /sys/class/power_supply {'-' * 37}\n    Supply: {data['supply']} | Capacity: {data['capacity']:>3}% | Status: {data['status']}\n     Model: {data['model_name']}, Technology: {data['technology']}, Manufacturer: {data['manufacturer']}\n   Voltage: {data['voltage']} | Current: {data['current']}\n"

def end():
    """
    clean up when the program exits
    """

    battery_class.close_files()


if __name__ == "__main__":
    main()
