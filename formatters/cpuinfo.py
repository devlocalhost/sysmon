import time

from plugins.cpuinfo import CpuinfoPlugin

cpuinfo_plugin = CpuinfoPlugin()

while True:
    data = cpuinfo_plugin.get_data()
    print(data)
    time.sleep(1)
