from plugins.meminfo import MeminfoPlugin

meminfo_plugin = MeminfoPlugin()
data = meminfo_plugin.get_data()

print(data)
