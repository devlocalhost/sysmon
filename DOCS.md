# Documentation
This is a document on how to use sysmon in other programs/scripts. This is not a "how to use sysmon".

# Plugins
Sysmon is splitted into parts (plugins). There are 5 plugins:
1. [cpuinfo](/plugins/cpuinfo.py)
2. [meminfo](/plugins/meminfo.py)
3. [loadavg](/plugins/loadavg.py)
4. [procpid](/plugins/procpid.py)
5. [netstats](/plugins/netstats.py)

# Usage
Usage for all plugins is the same. Copy the plugins and util directory to the root of your script, then:
1. import the plugin
```python
from plugins import cpuinfo
```

2. create a object
```python
cpuinfo_class = cpuinfo.Cpuinfo()
```

3. execute the get_data function
```python
cpuinfo_class.get_data()
```

4. close all files (if the plugin keeps any files opened)
```python
cpuinfo_class.close_files()
```

Then, format the data however you want. The output is in JSON

## cpuinfo
cpuinfo is a plugin which provides details about the cpu. The available details are:
1. cpu frequency (¹)
2. cores count (logical and physical, ²)
3. model
4. architecture type
5. cache type and size (³)
6. temperature (⁴)
7. usage

- ¹: frequency may not be available on android phones. frequency depends on kernel configuration. frequency may not be the max frequency your cpu can reach, bur rather the current
- ²: count may not be correct
- ³: cache size may not be correct
- ⁴: temperature may not be correct

### Usage
```python
from plugins import cpuinfo
cpuinfo_class = cpuinfo.Cpuinfo()
print(cpuinfo_class.get_data())
cpuinfo_class.close_files()
```
### Output
```
{'static': {'architecture': 'aarch64',
            'cache_size': 'Unknown',
            'cache_type': 'Unknown',
            'cores': {'logical': 8, 'physical': 0},
            'frequency': 1420.8,
            'model': 'Qualcomm SM6125',
            'uses_smt': False},
 'temperature': '39',
 'usage': 5.8}
```

- `architecture`: the architecture of the CPU
- `cache_size`: cache size (human formatted)
- `cache_type`: the type of the cache (L2, L3)
- `logical`: logical cores count
- `physical`: physical cores count
- `frequency`: the frequency of CPU
- `model`: model string
- `uses_smt`: unknown
- `temperature`: CPU temperature, in Celsius
- `usage`: CPU usage

## meminfo
meminfo shows details about physical (RAM) and virtual (ZRAM/SWAP). The available details are:
1. total phys and virt memory
2. used phys and virt memory
3. "actual used" phys memory
4. available phys and virt memory
5. free phys memory
6. cached phys and virt memory

Coming soon:
- combined phys and virt memory statistics

### Usage
```python
from plugins import meminfo
meminfo_class = meminfo.Meminfo()
print(meminfo_class.get_data())
meminfo_class.close_files()
```

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
 'virtual': {'percentage': {'available': 27.1, 'used': 72.9},
             'values': {'available': 874192896,
                        'cached': 39645184,
                        'total': 3221221376,
                        'used': 2347028480}}}
```

Under:
- physical: the stats are for physical memory.
- virtual: the stats are for virtual memory.
- percentage: usage in percentage.
- values: there are the raw values, in bytes.

For values key:
- `available`: raw (bytes) available memory value
- `cached`: raw (bytes) cached memory value
- `free`: raw (bytes) free memory value
- `total`: raw (bytes) total memory value
- `used`: raw (bytes) used memory value

## loadavg
loadavg shows load times, uptime, and boot time. The available details are:
1. Load times (1, 5, and 15 mins)
2. Entities (processes [?]) (¹) (active and total)
3. Uptime and boot time

### Usage
```
from plugins import loadavg
loadavg_class = loadavg.Loadavg()
print(loadavg_class.get_data())
loadavg_class.close_files()
```

### Output
```
{'entities': {'active': '2', 'total': '1586'},
 'load_times': {'1': '1.23', '15': '1.42', '5': '1.80'},
 'uptime': {'since': 'Thursday February 22 2024, 03:37:58 PM',
            'uptime': '2 hours, and 50 minutes'}}
```

Under:
- entities, the active and total running processes (?) are reported. The values are ints
- load_times, system load for 1, 5  and 15 mins are reported. The values are float.
- uptime:
  - since: the date the system has been up since
  - uptime: uptime in human readable format

## procpid
procpid shows (by default) the 6 most VmRSS consuming processes. The available details are:
1. process name
2. process id
3. process vmrss
4. process state

### Usage
```
from plugins import procpid
procpid_class = procpid.Procpid()
print(procpid_class.get_data())
procpid_class.close_files()
```

### Output
```
{'processes': [{'name': 'e.android.music',
                'pid': '5864',
                'state': 'Sleeping',
                'vmrss': 465547264},
               {'name': 'firefox',
                'pid': '3759',
                'state': 'Sleeping',
                'vmrss': 354238464},
               {'name': 'system_server',
                'pid': '4895',
                'state': 'Sleeping',
                'vmrss': 352677888},
               {'name': 'ndroid.systemui',
                'pid': '5062',
                'state': 'Sleeping',
                'vmrss': 305909760},
               {'name': 'AndroidUI',
                'pid': '6421',
                'state': 'Sleeping',
                'vmrss': 294662144},
               {'name': 'droid.launcher3',
                'pid': '5452',
                'state': 'Sleeping',
                'vmrss': 242987008}]}
```

Note: name is truncated to 15 characters by the kernel, not sysmon.

Under processes:
`name`: process name
`pid`: process id (int)
`state`: process state
`vmrss`: process vmrss usage (int)

## netstats
netstats shows network status such as network adapter name, and more. The available details are:
1. local ip
2. network interface
3. received and transferred bytes since boot time
4. received and transferred bytes one second ago (network speed meter)

### Usage
```
from plugins import netstats
netstats_class = netstats.Netstats()
print(netstats_class.get_data())
netstats_class.close_files()
```

### Output
```
{'interface': 'waydroid0',
 'local_ip': '192.168.240.1',
 'statistics': {'received': 9024248,
                'speeds': {'received': 9024248, 'transferred': 556928103},
                'transferred': 556928103}}
```

`interface`: the network interface name
`local_ip`: the local ip

Under statistics:
`received`: total received bytes
`transferred`: total transferred bytes

Under speeds:
`received`: total received bytes one second ago
`transferred`: total transferred bytes one second ago
