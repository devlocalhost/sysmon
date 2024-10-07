# Documentation
This document outlines how to integrate sysmon into other programs or scripts. It serves as a guide for developers looking to utilize sysmon's functionality within their projects.

## Plugins
Sysmon is divided into five distinct plugins, each catering to different system monitoring aspects:

1. [cpuinfo](#cpuinfo-plugin) [(source)](/plugins/cpuinfo.py)
2. [meminfo](#meminfo-plugin) [(source)](/plugins/meminfo.py)
3. [loadavg](#loadavg-plugin) [(source)](/plugins/loadavg.py)
4. [procpid](#procpid-plugin) [(source)](/plugins/procpid.py)
5. [netstats](#netstats-plugin) [(source)](/plugins/netstats.py)

## Utils
The utils file offers configurations to customize the output data from plugins. For instance, in meminfo, you can disable swap stats, and in netstats, you can hide the local IP address. Below is an example:

```python
from util import util

# Disable showing local IP
util.SHOW_LOCAL_IP = False

# Override interface
util.INTERFACE = "wlp4s0"

from plugins import netstats

netstats_class = netstats.Netstats()
print(netstats_class.get_data())
netstats_class.close_files() # Always close files!!
```

Output:

```
{'interface': 'wlp4s0',
 'local_ip': 'Hidden',
 'statistics': {'received': 721839959,
                'speeds': {'received': 721839959, 'transferred': 23420738},
                'transferred': 23420738}}
```

## Usage
The usage pattern for all plugins remains consistent. Follow these steps to integrate a plugin into your script:

1. Import the desired plugin:
```python
from plugins import cpuinfo
```

2. Create an object of the plugin:
```python
cpuinfo_class = cpuinfo.Cpuinfo()
```

3. Execute the `get_data` function to retrieve system information:
```python
cpuinfo_class.get_data()
```

4. Ensure to close any open files if the plugin maintains them:
```python
cpuinfo_class.close_files()
```

Format the retrieved data as required; the output is in JSON format. You can also check the [formatters](/formatters) directory, to get an idea of how to use these plugins.

## cpuinfo Plugin
The `cpuinfo` plugin provides detailed information about the CPU, including:

- `architecture`: CPU architecture
- `cache`:
  1. `size`: size (in bytes)
  2. `level`: level
- `cores`:
  1. `physical`: physical cores count
  2. `logical`: logical cores count
- `frequency`: CPU frequency
- `model`: CPU model
- `uses_smt`: Whether CPU uses simultaneous multithreading (SMT)
- `temperature`: CPU temperature in Celsius
- `usage`: CPU usage

### Output
```
{'architecture': 'x86_64',
 'cache': {'level': 'L2', 'size': 3145728},
 'cores': {'logical': 2, 'physical': 2},
 'frequency': 1064.03,
 'model': 'Intel Core2 Duo P7450',
 'temperature': 45.0,
 'usage': 94.2}
```

## meminfo Plugin
The `meminfo` plugin offers details about physical (RAM) and virtual (ZRAM/SWAP) memory usage. It includes:

Under the `physical` and `virtual` sections:
- `percentage`: Memory usage percentage
- `values`: Raw memory values in bytes

### Output
```
{'physical': {'percentage': {'actual_used': 69.7,
                             'available': 23.8,
                             'free': 3.7,
                             'used': 76.2},
              'values': {'actual_used': 2667823104,
                         'available': 911327232,
                         'cached': 1017966592,
                         'free': 141074432,
                         'total': 3826864128,
                         'used': 2915536896}},
 'virtual': {'percentage': {'free': 27.1, 'used': 72.9},
             'values': {'free': 874192896,
                        'cached': 39645184,
                        'total': 3221221376,
                        'used': 2347028480}}}
```

Note: there are two "used" fields, due to different calculation. "actual_used" is close to how htop calculates it, and used is: MemTotal - MemAvailable

## loadavg Plugin
The `loadavg` plugin provides load times, uptime, and boot time information. It includes:

- `entities`: Active and total running processes
- `load_times`: System load for 1, 5, and 15 minutes
- `uptime`:
  1. `seconds`: uptime, in seconds
  2. `timestamp`: unix timestamp. use strftime to convert it to human readable format

### Output
```
{'entities': {'active': 4, 'total': 557},
 'load_times': {'1': 1.26, '15': 1.0, '5': 1.11},
 'uptime': {'seconds': 166860, 'timestamp': 1719750035.6097515}}
```

## procpid Plugin
The `procpid` plugin displays information about the most VmRSS-consuming processes. It includes:

- `name`: process name
- `pid`: process id (int)
- `state`: process state
- `vmrss`: process vmrss usage (int)

### Output
```
{'processes': [{'name': 'firefox',
                'pid': 3759,
                'state': 'Sleeping',
                'vmrss': 462802944},
               {'name': 'e.android.music',
                'pid': 5864,
                'state': 'Sleeping',
                'vmrss': 422006784},
               {'name': 'system_server',
                'pid': 4895,
                'state': 'Sleeping',
                'vmrss': 306163712},
               {'name': 'ndroid.systemui',
                'pid': 5062,
                'state': 'Sleeping',
                'vmrss': 268738560},
               {'name': 'Isolated',
                'pid': 11112,
                'state': 'Sleeping',
                'vmrss': 268210176},
               {'name': 'AndroidUI',
                'pid': 6421,
                'state': 'Sleeping',
                'vmrss': 249049088}]}
```

## netstats Plugin
The `netstats` plugin shows network status such as the network adapter name and data transfer statistics. It includes:

- `interface`: Network interface name
- `local_ip`: Local IP address
- `statistics`: Data transfer statistics since boot time
  - `speeds`: Network speed in bytes per second

### Output
```
{'interface': 'waydroid0',
 'local_ip': '192.168.240.1',
 'statistics': {'received': 9024248,
                'speeds': {'received': 9024248, 'transferred': 556928103},
                'transferred': 556928103}}
```
