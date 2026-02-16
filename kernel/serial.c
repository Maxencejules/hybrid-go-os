#include "serial.h"

void serial_init(void) {
    outb(COM1_PORT + 1, 0x00);    /* Disable interrupts        */
    outb(COM1_PORT + 3, 0x80);    /* Enable DLAB               */
    outb(COM1_PORT + 0, 0x03);    /* Baud divisor lo (38 400)  */
    outb(COM1_PORT + 1, 0x00);    /* Baud divisor hi           */
    outb(COM1_PORT + 3, 0x03);    /* 8N1                       */
    outb(COM1_PORT + 2, 0xC7);    /* Enable FIFO, 14-byte      */
    outb(COM1_PORT + 4, 0x0B);    /* RTS/DSR, IRQs enabled     */
}

void serial_putc(char c) {
    while ((inb(COM1_PORT + 5) & 0x20) == 0)
        ;
    outb(COM1_PORT, (uint8_t)c);
}

void serial_puts(const char *s) {
    while (*s) {
        serial_putc(*s);
        s++;
    }
}
