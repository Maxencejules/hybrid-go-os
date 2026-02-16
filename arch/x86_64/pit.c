#include <stdint.h>
#include "pit.h"
#include "../../kernel/serial.h"

#define PIT_CHANNEL0 0x40
#define PIT_COMMAND  0x43
#define PIT_BASE_FREQ 1193182

void pit_init(uint32_t frequency) {
    uint32_t divisor = PIT_BASE_FREQ / frequency;

    /* Channel 0, lobyte/hibyte, mode 2 (rate generator) */
    outb(PIT_COMMAND, 0x34);

    outb(PIT_CHANNEL0, (uint8_t)(divisor & 0xFF));
    outb(PIT_CHANNEL0, (uint8_t)((divisor >> 8) & 0xFF));

    serial_puts("ARCH: PIT configured\n");
}
