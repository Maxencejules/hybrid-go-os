#include <stdint.h>
#include <stddef.h>
#include "virtio_blk.h"
#include "pci.h"
#include "pmm.h"
#include "vmm.h"
#include "serial.h"
#include "io.h"
#include "string.h"

/* VirtIO legacy register offsets (from BAR0) */
#define VIRTIO_REG_DEVICE_FEATURES  0x00
#define VIRTIO_REG_GUEST_FEATURES   0x04
#define VIRTIO_REG_QUEUE_PFN        0x08
#define VIRTIO_REG_QUEUE_SIZE       0x0C
#define VIRTIO_REG_QUEUE_SEL        0x0E
#define VIRTIO_REG_QUEUE_NOTIFY     0x10
#define VIRTIO_REG_DEVICE_STATUS    0x12
#define VIRTIO_REG_ISR_STATUS       0x13

/* VirtIO status bits */
#define VIRTIO_STATUS_ACK       1
#define VIRTIO_STATUS_DRIVER    2
#define VIRTIO_STATUS_DRIVER_OK 4
#define VIRTIO_STATUS_FAILED    128

/* Descriptor flags */
#define VRING_DESC_F_NEXT   1
#define VRING_DESC_F_WRITE  2

/* Block request types */
#define VIRTIO_BLK_T_IN   0   /* read  */
#define VIRTIO_BLK_T_OUT  1   /* write */

/* ---- Virtqueue structures (match VirtIO spec) ---- */

struct vring_desc {
    uint64_t addr;
    uint32_t len;
    uint16_t flags;
    uint16_t next;
} __attribute__((packed));

struct vring_avail {
    uint16_t flags;
    uint16_t idx;
    uint16_t ring[];
} __attribute__((packed));

struct vring_used_elem {
    uint32_t id;
    uint32_t len;
} __attribute__((packed));

struct vring_used {
    uint16_t flags;
    uint16_t idx;
    struct vring_used_elem ring[];
} __attribute__((packed));

/* Block request header */
struct virtio_blk_req_hdr {
    uint32_t type;
    uint32_t reserved;
    uint64_t sector;
} __attribute__((packed));

/* ---- Driver state ---- */

static uint16_t bar0;
static uint16_t queue_size;
static struct vring_desc  *descs;
static struct vring_avail *avail;
static struct vring_used  *used;
static uint16_t last_used_idx;

static uint64_t queue_phys;
static uint64_t req_page_phys;
static uint64_t data_page_phys;
static void    *req_page_virt;
static void    *data_page_virt;

static int initialized;

/* ---- Helpers ---- */

static inline uint8_t  vio_read8(uint16_t off)  { return inb(bar0 + off); }
static inline uint16_t vio_read16(uint16_t off) { return inw(bar0 + off); }
static inline uint32_t vio_read32(uint16_t off) { return inl(bar0 + off); }
static inline void vio_write8(uint16_t off, uint8_t v)   { outb(bar0 + off, v); }
static inline void vio_write16(uint16_t off, uint16_t v) { outw(bar0 + off, v); }
static inline void vio_write32(uint16_t off, uint32_t v) { outl(bar0 + off, v); }

/* ---- Init ---- */

int virtio_blk_init(void) {
    struct pci_device dev;
    if (pci_find_device(0x1AF4, 0x1001, &dev) != 0) {
        serial_puts("BLK: no virtio-blk found\n");
        return -1;
    }
    bar0 = (uint16_t)dev.bar0;
    serial_puts("BLK: found virtio-blk\n");

    /* 1. Reset */
    vio_write8(VIRTIO_REG_DEVICE_STATUS, 0);

    /* 2. Acknowledge */
    vio_write8(VIRTIO_REG_DEVICE_STATUS, VIRTIO_STATUS_ACK);

    /* 3. Driver */
    vio_write8(VIRTIO_REG_DEVICE_STATUS, VIRTIO_STATUS_ACK | VIRTIO_STATUS_DRIVER);

    /* 4. Feature negotiation (accept none for simplicity) */
    (void)vio_read32(VIRTIO_REG_DEVICE_FEATURES);
    vio_write32(VIRTIO_REG_GUEST_FEATURES, 0);

    /* 5. Select queue 0, read size */
    vio_write16(VIRTIO_REG_QUEUE_SEL, 0);
    queue_size = vio_read16(VIRTIO_REG_QUEUE_SIZE);
    if (queue_size == 0) {
        serial_puts("BLK: queue size 0\n");
        vio_write8(VIRTIO_REG_DEVICE_STATUS, VIRTIO_STATUS_FAILED);
        return -1;
    }

    /* 6. Calculate virtqueue memory layout and allocate */
    uint64_t avail_end = (uint64_t)queue_size * 16 + 6 + 2 * (uint64_t)queue_size;
    uint64_t used_offset = (avail_end + 4095) & ~4095ULL;
    uint64_t used_end = used_offset + 6 + 8 * (uint64_t)queue_size;
    uint32_t queue_pages = (uint32_t)((used_end + 4095) / 4096);

    queue_phys = pmm_alloc_contiguous(queue_pages);
    if (!queue_phys) {
        serial_puts("BLK: OOM (queue)\n");
        vio_write8(VIRTIO_REG_DEVICE_STATUS, VIRTIO_STATUS_FAILED);
        return -1;
    }

    uint8_t *qbase = (uint8_t *)phys_to_virt(queue_phys);
    memset(qbase, 0, queue_pages * 4096);

    descs = (struct vring_desc *)qbase;
    avail = (struct vring_avail *)(qbase + queue_size * 16);
    used = (struct vring_used *)(qbase + used_offset);
    last_used_idx = 0;

    /* Tell device the queue page frame number */
    vio_write32(VIRTIO_REG_QUEUE_PFN, (uint32_t)(queue_phys >> 12));

    /* 7. Allocate DMA pages for request header/status and data */
    req_page_phys  = pmm_alloc_page();
    data_page_phys = pmm_alloc_page();
    if (!req_page_phys || !data_page_phys) {
        serial_puts("BLK: OOM (dma)\n");
        vio_write8(VIRTIO_REG_DEVICE_STATUS, VIRTIO_STATUS_FAILED);
        return -1;
    }
    req_page_virt  = phys_to_virt(req_page_phys);
    data_page_virt = phys_to_virt(data_page_phys);
    memset(req_page_virt, 0, 4096);
    memset(data_page_virt, 0, 4096);

    /* 8. Driver OK */
    vio_write8(VIRTIO_REG_DEVICE_STATUS,
               VIRTIO_STATUS_ACK | VIRTIO_STATUS_DRIVER | VIRTIO_STATUS_DRIVER_OK);

    initialized = 1;
    serial_puts("BLK: driver ready\n");
    return 0;
}

/* ---- Block I/O (3-descriptor chain, polling) ---- */

static int virtio_blk_io(uint32_t type, uint64_t sector,
                         void *buf, uint32_t count) {
    if (!initialized || count == 0 || count > 8)
        return -1;

    uint32_t data_len = count * 512;

    /* Request header */
    struct virtio_blk_req_hdr *hdr = (struct virtio_blk_req_hdr *)req_page_virt;
    hdr->type     = type;
    hdr->reserved = 0;
    hdr->sector   = sector;

    /* Status byte right after header (volatile — device writes via DMA) */
    volatile uint8_t *status_ptr = (volatile uint8_t *)((uint8_t *)req_page_virt + sizeof(struct virtio_blk_req_hdr));
    *status_ptr = 0xFF;

    /* For write: copy data to DMA page */
    if (type == VIRTIO_BLK_T_OUT)
        memcpy(data_page_virt, buf, data_len);
    else
        memset(data_page_virt, 0, data_len);

    /* Descriptor 0: header (device reads) */
    descs[0].addr  = req_page_phys;
    descs[0].len   = sizeof(struct virtio_blk_req_hdr);
    descs[0].flags = VRING_DESC_F_NEXT;
    descs[0].next  = 1;

    /* Descriptor 1: data */
    descs[1].addr  = data_page_phys;
    descs[1].len   = data_len;
    descs[1].flags = VRING_DESC_F_NEXT;
    if (type == VIRTIO_BLK_T_IN)
        descs[1].flags |= VRING_DESC_F_WRITE;
    descs[1].next  = 2;

    /* Descriptor 2: status byte (device writes) */
    descs[2].addr  = req_page_phys + sizeof(struct virtio_blk_req_hdr);
    descs[2].len   = 1;
    descs[2].flags = VRING_DESC_F_WRITE;
    descs[2].next  = 0;

    /* Add to available ring */
    uint16_t avail_idx = avail->idx;
    avail->ring[avail_idx % queue_size] = 0;

    __asm__ volatile ("" ::: "memory");  /* compiler barrier */

    avail->idx = avail_idx + 1;

    /* Notify device */
    vio_write16(VIRTIO_REG_QUEUE_NOTIFY, 0);

    /* Poll for completion */
    __asm__ volatile ("" ::: "memory");
    uint32_t timeout = 10000000;
    while (used->idx == last_used_idx) {
        __asm__ volatile ("pause" ::: "memory");
        if (--timeout == 0) {
            serial_puts("BLK: timeout\n");
            return -1;
        }
    }
    last_used_idx++;

    /* Read ISR status to acknowledge and ensure device writes are visible */
    (void)vio_read8(VIRTIO_REG_ISR_STATUS);
    __asm__ volatile ("" ::: "memory");

    /* Check status */
    uint8_t st = *status_ptr;
    if (st != 0) {
        serial_puts("BLK: io error status=");
        serial_put_hex(st);
        serial_putc('\n');
        return -1;
    }

    /* For read: copy data from DMA page to caller */
    if (type == VIRTIO_BLK_T_IN)
        memcpy(buf, data_page_virt, data_len);

    return 0;
}

int virtio_blk_read(uint64_t sector, void *buf, uint32_t count) {
    return virtio_blk_io(VIRTIO_BLK_T_IN, sector, buf, count);
}

int virtio_blk_write(uint64_t sector, const void *buf, uint32_t count) {
    return virtio_blk_io(VIRTIO_BLK_T_OUT, sector, (void *)buf, count);
}
