#include <stdio.h>
#include <unistd.h>

void get_cache_size(char* cache_info) {
    long cpu_cache_size = sysconf(_SC_LEVEL3_CACHE_SIZE);

    if (cpu_cache_size <= 0) {
        cpu_cache_size = sysconf(_SC_LEVEL2_CACHE_SIZE);
        if (cpu_cache_size <= 0) {
            snprintf(cache_info, 64, "Unknown.0");
        } else {
            snprintf(cache_info, 64, "%ld.2", cpu_cache_size);
        }
    } else {
        snprintf(cache_info, 64, "%ld.3", cpu_cache_size);
    }
}

// physical = 1 -> physical cores
// physical = 0 -> logical cores
unsigned int get_cores(int physical) {
    unsigned int eax = 11, ebx = 0, ecx = 1;

    asm volatile("cpuid"
                 : "=a"(eax), "=b"(ebx), "=c"(ecx)
                 : "0"(eax), "2"(ecx)
                 :);
    if (physical) {
        return eax;
    }
    else {
        return ebx;
    }
}
