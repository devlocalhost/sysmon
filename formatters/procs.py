from plugins.procs import ProcsPlugin

def show_plugin(config):
    procs_plugin = ProcsPlugin(config)
    data = procs_plugin.get_data()

    for stuff in data:
        print(stuff)
