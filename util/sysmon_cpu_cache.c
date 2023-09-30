#include <stdio.h>
#include <unistd.h>

void get_cache_size(char* cache_info) {
    long cpu_cache_size = sysconf(_SC_LEVEL3_CACHE_SIZE);

    if (cpu_cache_size <= 0) {
        cpu_cache_size = sysconf(_SC_LEVEL2_CACHE_SIZE); // Remove the 'long' declaration
        if (cpu_cache_size <= 0) {
            snprintf(cache_info, 64, "N/A.cache");
        } else {
            snprintf(cache_info, 64, "%ld.2", cpu_cache_size);
        }
    } else {
        snprintf(cache_info, 64, "%ld.3", cpu_cache_size);
    }
}

