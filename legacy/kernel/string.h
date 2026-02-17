#ifndef STRING_H
#define STRING_H

#include <stddef.h>

void *memset(void *s, int c, size_t n);
void *memcpy(void *dest, const void *src, size_t n);
int strncmp(const char *s1, const char *s2, size_t n);
size_t strnlen(const char *s, size_t maxlen);

#endif
