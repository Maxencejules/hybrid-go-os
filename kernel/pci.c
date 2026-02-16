#include <stdint.h>
#include "pci.h"
#include "serial.h"
#include "io.h"

/* Read a 32-bit word from PCI configuration space */
static uint32_t pci_config_read32(uint8_t bus, uint8_t dev,
                                  uint8_t func, uint8_t offset) {
    uint32_t addr = (1U << 31)
                  | ((uint32_t)bus << 16)
                  | ((uint32_t)dev << 11)
                  | ((uint32_t)func << 8)
                  | (offset & 0xFC);
    outl(PCI_CONFIG_ADDR, addr);
    return inl(PCI_CONFIG_DATA);
}

void pci_init(void) {
    serial_puts("PCI: scanning bus 0\n");
    for (uint8_t dev = 0; dev < 32; dev++) {
        uint32_t id = pci_config_read32(0, dev, 0, 0x00);
        uint16_t vendor = id & 0xFFFF;
        if (vendor == 0xFFFF)
            continue;
        uint16_t devid = (id >> 16) & 0xFFFF;
        serial_puts("PCI: dev=");
        serial_put_hex(dev);
        serial_puts(" vendor=");
        serial_put_hex(vendor);
        serial_puts(" device=");
        serial_put_hex(devid);
        serial_putc('\n');
    }
}

int pci_find_device(uint16_t vendor, uint16_t device,
                    struct pci_device *out) {
    for (uint8_t dev = 0; dev < 32; dev++) {
        uint32_t id = pci_config_read32(0, dev, 0, 0x00);
        uint16_t v = id & 0xFFFF;
        uint16_t d = (id >> 16) & 0xFFFF;
        if (v == vendor && d == device) {
            out->bus       = 0;
            out->device    = dev;
            out->function  = 0;
            out->vendor_id = v;
            out->device_id = d;
            out->bar0      = pci_config_read32(0, dev, 0, 0x10) & ~0x3U;
            uint32_t irq   = pci_config_read32(0, dev, 0, 0x3C);
            out->irq_line  = irq & 0xFF;
            return 0;
        }
    }
    return -1;
}
