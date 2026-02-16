#ifndef PCI_H
#define PCI_H

#include <stdint.h>

#define PCI_CONFIG_ADDR 0xCF8
#define PCI_CONFIG_DATA 0xCFC

struct pci_device {
    uint8_t  bus;
    uint8_t  device;
    uint8_t  function;
    uint16_t vendor_id;
    uint16_t device_id;
    uint32_t bar0;
    uint8_t  irq_line;
};

void pci_init(void);
int  pci_find_device(uint16_t vendor, uint16_t device, struct pci_device *out);

#endif
