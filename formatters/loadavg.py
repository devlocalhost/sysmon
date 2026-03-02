import time

from plugins.loadavg import LoadavgPlugin

loadavg_plugin = LoadavgPlugin()

while True:
    data = loadavg_plugin.get_data()
    print(data)
    time.sleep(1)
