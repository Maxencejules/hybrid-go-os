#include <stdint.h>
#include "pic.h"
#include "../../kernel/serial.h"

#define PIC1_CMD  0x20
#define PIC1_DATA 0x21
#define PIC2_CMD  0xA0
#define PIC2_DATA 0xA1

#define ICW1_INIT 0x11
#define ICW4_8086 0x01

void pic_init(void) {
    /* ICW1: start init sequence */
    outb(PIC1_CMD, ICW1_INIT);
    outb(PIC2_CMD, ICW1_INIT);

    /* ICW2: vector offsets */
    outb(PIC1_DATA, 32);    /* master: IRQ 0-7  → vectors 32-39 */
    outb(PIC2_DATA, 40);    /* slave:  IRQ 8-15 → vectors 40-47 */

    /* ICW3: cascade wiring */
    outb(PIC1_DATA, 0x04);  /* master: slave on IRQ2 */
    outb(PIC2_DATA, 0x02);  /* slave: cascade identity */

    /* ICW4: 8086 mode */
    outb(PIC1_DATA, ICW4_8086);
    outb(PIC2_DATA, ICW4_8086);

    /* OCW1: mask all except IRQ0 (timer) */
    outb(PIC1_DATA, 0xFE);
    outb(PIC2_DATA, 0xFF);

    serial_puts("ARCH: PIC initialized\n");
}

void pic_send_eoi(uint8_t irq) {
    if (irq >= 8)
        outb(PIC2_CMD, 0x20);
    outb(PIC1_CMD, 0x20);
}
