#ifndef SERVICE_REGISTRY_H
#define SERVICE_REGISTRY_H

#include <stdint.h>

#define MAX_SERVICES     8
#define SERVICE_NAME_MAX 32

void     service_registry_init(void);
int      service_register(const char *name, uint32_t port);
uint32_t service_lookup(const char *name);

#endif
