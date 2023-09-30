# compiling

`clang -O3 -shared -o /usr/lib/sysmon_cpu_cache.so -fPIC sysmon_cpu_cache.c`

root needed. why? so sysmon can load the library anywhere you execute it
