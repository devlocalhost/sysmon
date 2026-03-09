import sys
import time

from plugins.netstats import NetstatsPlugin
from utils.util import convert_bytes

netstats_plugin = NetstatsPlugin()


while True:
    data = netstats_plugin.get_data()
    print(convert_bytes(data.transfer_statistics.speeds.received))
    print(convert_bytes(data.transfer_statistics.speeds.transferred))
    
    try:
        time.sleep(1)

    except:
        netstats_plugin._close_files()
        sys.exit()
