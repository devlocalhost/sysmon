import time

from plugins.meminfo import MeminfoPlugin

meminfo_plugin = MeminfoPlugin()

while True:
    data = meminfo_plugin.get_data()
    print(data)
    time.sleep(1)
