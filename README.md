# SysMon, a system monitor aiming to be fast and ready to use

using [**curses**](https://docs.python.org/3/howto/curses.html)

![sysmon screenshot](sysmon-screen.png)

## what is sysmon
sysmon is *another* system monitor designed to be **ready to use** and easy to understand. it uses [**linux's /proc pseudo filesystem**](https://www.kernel.org/doc/html/latest/filesystems/proc.html) to read information and [**curses**](https://docs.python.org/3/howto/curses.html) display them

## help and usage
Usage: ./sysmon OPTS where OPTS can be:
+ mem ----> Display RAM and swap (if available) usage (total, used, free, cached, %)
+ cpu ----> Display CPU information (model, usage, temperature, cores & threads, max frequency, cache, architecture)
+ load ---> Display Load averange (1, 5 and 15 mins) and uptime (total, since when) of your system
+ nomem --> Dont display memory stats
+ nocpu --> Dont display cpu stats
+ noload -> Dont display load times and uptime

By default, when running without options it will display everything, memory usage, cpu and load times. If you dont want to see an option run: ./sysmon XOPT where X can be yes or no and OPT cpu, mem or load for example ./sysmon noload. You can also "print" the options once, with the "once" option. Example: ./sysmon once OPT (which can be mem, cpu or load)

## bug/suggestion/correction
please open a issue, including traceback and a screenshot if you found a bug

if you want to suggest a new feature, or if you found something that is not correct (for example, incorrect cpu temperature or ram usage/something else) feel free to open an issue

## notes
You might **NOT** be able to view the temperature, or the temperature might **NOT** be accurate, because sysmon reads `/sys/class/thermal/thermal_zone0/temp` or `/sys/class/hwmon/hwmon1/temp1_input` to get the temperature, and your system might report it in a different file for example. If sysmon cannot read the temperature, it will display "??". **You will NOT see the temperature if you have an AMD cpu**. If you know how to fix this, please open an issue or pull request 

many thanks to [skyblueborb](https://github.com/skyblueborb) for helping me test, fix and make the cpu temperature feature better
