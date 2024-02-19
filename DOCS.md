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
