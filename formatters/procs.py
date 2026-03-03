import time

from plugins.procs import ProcsPlugin

procs_plugin = ProcsPlugin()
data = procs_plugin.get_data()

for stuff in data:
    print(stuff.VmRSS)
