## sysmon, a system monitor ready to use

using [**curses**](https://docs.python.org/3/howto/curses.html)

## preview
## sysmon on a laptop
![sysmon laptop screenshot](screens/sysmon-pc.png)
## sysmon on a mobile phone (with root access, because some things won't work)
![sysmon phone screenshot](screens/sysmon-phone.png)

## old sysmon
![old sysmon screenshot](screens/sysmon-old.png)

## try before cloning
```sh
curl https://raw.githubusercontent.com/devlocalhost/sysmon/main/sysmon | python
```

## download without cloning
```
curl https://raw.githubusercontent.com/devlocalhost/sysmon/main/sysmon -O sysmon
```

## what is sysmon
sysmon is *another* system monitor which is **ready to use** and easy to understand. it uses [**linux's /proc pseudo filesystem**](https://www.kernel.org/doc/html/latest/filesystems/proc.html) to read information and [**curses**](https://docs.python.org/3/howto/curses.html) to display them. the only thing you have to do is git clone this repo, and run the sysmon file

## what can sysmon do?
 - show cpu information, like model, temperature (1), frequency (2), cores (1) and threads count, and cache memory size (1)
 - show memory information, like total, available, used (3) and cached ram and swap information
 - show system load, entities and uptime
 - show the proccesses (6 by default) that are consuming the most VmRSS, including the state and name
 - show network information, like device, transferred and received, and speed

1. information reported **might** not be correct

2. ive heard this depends on the kernel, i am not sure. sysmon might not show the max frequency the manufacturer website reports

3. ~~Used = MemTotal - MemAvailable. dont worry if htop shows less ram used. htop counts it differently (it also substracts MemCached [i think] which i dont do that) i am using 2 implementations/calculations for this: the [htop way](https://stackoverflow.com/a/41251290) (but a bit modified), and "my way". the htop way is: Used = MemTotal - MemFree - Buffers - (Cached + SReclaimable - Shmem). my way is: Used = MemTotal - MemAvailable. now, my way is accurate, but a friend told me htop way is more accurate, so ill keep both unless i get annoyed by it. also, you may notice that actual used percent + available percent might not equal to 100 ("my way" used percent + available does). why? im not sure. you may also notice that it wont be that accurate to htop. for me, the difference is 4mb (htop shows 4mb less)~~. there are 2 used columns, one is the accurate way (matching `htop` and `free`), the other is MemTotal - MemAvailable.

## why 2 files?
because i like the old layout of sysmon too (but I rarely use it). i strongly suggest you to use the new sysmon, because better code, improvements, and faster

## help and usage
```
  -h, --help                                  show this help message and exit
  -nc, --nocpu                                disables cpuinfo (cpu information, like usage, model, and more)
  -nm, --nomem                                disables meminfo (memory information, like total, used and more)
  -nl, --noload                               disables loadavg (load times information, including uptime, and more)
  -np, --nopid                                disables procpid (shows the most vmrss consuming processes)
  -nn, --nonet                                disables network_stats (network stats, like received/transfered bytes, and more)
  -nt, --notemp                               disables cpu temperature
  -ns, --noswap                               disables swap information in meminfo
  -m, --metric                                use metric (1000) instead of IEC (1024) unit for data convertion
  -p INT, --procs INT                         how many processes to show in procpid. Default: 6
  -s FLOAT, --sleep FLOAT                     refresh time. Default: 1.0
  -f FUNC [FUNC ...], --func FUNC [FUNC ...]  executes only the mentioned functions. can be: cpu, mem, load, pid, and/or net (usage: --func mem load)
```

## bug/suggestion/correction
please open a issue, including traceback and a screenshot if you found a bug

if you want to suggest a new feature, or if you found something that is not correct (for example, incorrect cpu temperature or ram usage/something else) feel free to open an issue

## credits
many thanks to [skyblueborb](https://github.com/skyblueborb) for helping me test, fix and make the cpu temperature feature better

also many thanks to [ari](https://ari-web.xyz/gh) for helping me with the padding/formatting of the text
