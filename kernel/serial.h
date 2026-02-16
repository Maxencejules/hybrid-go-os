#ifndef SERIAL_H
#define SERIAL_H

#include <stdint.h>

#define COM1_PORT 0x3F8

/* --- Port I/O primitives --- */

static inline void outb(uint16_t port, uint8_t val) {
    __asm__ volatile ("outb %0, %1" : : "a"(val), "Nd"(port));
}

static inline uint8_t inb(uint16_t port) {
    uint8_t ret;
    __asm__ volatile ("inb %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}

/* --- Serial interface --- */

void serial_init(void);
void serial_putc(char c);
void serial_puts(const char *s);

#endif
