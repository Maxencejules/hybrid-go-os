#include <stddef.h>
#include <stdint.h>

void *memset(void *dest, int val, size_t n) {
    uint8_t *p = (uint8_t *)dest;
    while (n--)
        *p++ = (uint8_t)val;
    return dest;
}

void *memcpy(void *dest, const void *src, size_t n) {
    uint8_t *d = (uint8_t *)dest;
    const uint8_t *s = (const uint8_t *)src;
    while (n--)
        *d++ = *s++;
    return dest;
}
