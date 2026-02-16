#include <stdint.h>
#include <stddef.h>
#include "service_registry.h"
#include "serial.h"
#include "string.h"

struct service_entry {
    char     name[SERVICE_NAME_MAX];
    uint32_t port;
};

static struct service_entry services[MAX_SERVICES];

void service_registry_init(void) {
    for (int i = 0; i < MAX_SERVICES; i++)
        services[i].port = 0;
    serial_puts("SERVICE: initialized\n");
}

static void safe_strncpy(char *dst, const char *src, size_t n) {
    size_t i;
    for (i = 0; i < n - 1 && src[i] != '\0'; i++)
        dst[i] = src[i];
    dst[i] = '\0';
}

int service_register(const char *name, uint32_t port) {
    if ((uint64_t)name >= 0x8000000000000000ULL || port == 0)
        return -1;

    for (int i = 0; i < MAX_SERVICES; i++) {
        if (services[i].port == 0) {
            safe_strncpy(services[i].name, name, SERVICE_NAME_MAX);
            services[i].port = port;
            return 0;
        }
    }
    return -1;
}

uint32_t service_lookup(const char *name) {
    if ((uint64_t)name >= 0x8000000000000000ULL)
        return 0;

    for (int i = 0; i < MAX_SERVICES; i++) {
        if (services[i].port != 0 &&
            strncmp(services[i].name, name, SERVICE_NAME_MAX) == 0)
            return services[i].port;
    }
    return 0;
}
