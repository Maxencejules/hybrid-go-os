#include <stdint.h>
#include <stddef.h>
#include "virtio_net.h"
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

/* Device-specific config starts at offset 0x14 for legacy */
#define VIRTIO_NET_CFG_MAC          0x14

/* VirtIO status bits */
#define VIRTIO_STATUS_ACK       1
#define VIRTIO_STATUS_DRIVER    2
#define VIRTIO_STATUS_DRIVER_OK 4
#define VIRTIO_STATUS_FAILED    128

/* Descriptor flags */
#define VRING_DESC_F_NEXT   1
#define VRING_DESC_F_WRITE  2

/* VirtIO net header (10 bytes, no mergeable buffers) */
struct virtio_net_hdr {
    uint8_t  flags;
    uint8_t  gso_type;
    uint16_t hdr_len;
    uint16_t gso_size;
    uint16_t csum_start;
    uint16_t csum_offset;
} __attribute__((packed));

#define NET_HDR_SIZE sizeof(struct virtio_net_hdr)

/* ---- Virtqueue structures (same as virtio_blk) ---- */

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

/* ---- Per-queue state ---- */

struct virtq {
    uint16_t             size;
    struct vring_desc   *descs;
    struct vring_avail  *avail;
    struct vring_used   *used;
    uint16_t             last_used;
    uint64_t             queue_phys;
    /* DMA buffer */
    uint64_t             buf_phys;
    void                *buf_virt;
};

/* ---- Driver state ---- */

static uint16_t bar0;
static struct virtq rxq;
static struct virtq txq;
static uint8_t mac_addr[6];
static int initialized;

/* ---- Helpers ---- */

static inline uint8_t  vio_read8(uint16_t off)  { return inb(bar0 + off); }
static inline uint16_t vio_read16(uint16_t off) { return inw(bar0 + off); }
static inline uint32_t vio_read32(uint16_t off) { return inl(bar0 + off); }
static inline void vio_write8(uint16_t off, uint8_t v)   { outb(bar0 + off, v); }
static inline void vio_write16(uint16_t off, uint16_t v) { outw(bar0 + off, v); }
static inline void vio_write32(uint16_t off, uint32_t v) { outl(bar0 + off, v); }

/* Setup a single virtqueue (select, read size, alloc vring, tell device) */
static int setup_queue(uint16_t idx, struct virtq *q) {
    vio_write16(VIRTIO_REG_QUEUE_SEL, idx);
    q->size = vio_read16(VIRTIO_REG_QUEUE_SIZE);
    if (q->size == 0)
        return -1;

    /* Calculate vring layout */
    uint64_t avail_end = (uint64_t)q->size * 16 + 6 + 2 * (uint64_t)q->size;
    uint64_t used_offset = (avail_end + 4095) & ~4095ULL;
    uint64_t used_end = used_offset + 6 + 8 * (uint64_t)q->size;
    uint32_t queue_pages = (uint32_t)((used_end + 4095) / 4096);

    q->queue_phys = pmm_alloc_contiguous(queue_pages);
    if (!q->queue_phys)
        return -1;

    uint8_t *qbase = (uint8_t *)phys_to_virt(q->queue_phys);
    memset(qbase, 0, queue_pages * 4096);

    q->descs = (struct vring_desc *)qbase;
    q->avail = (struct vring_avail *)(qbase + q->size * 16);
    q->used  = (struct vring_used *)(qbase + used_offset);
    q->last_used = 0;

    vio_write32(VIRTIO_REG_QUEUE_PFN, (uint32_t)(q->queue_phys >> 12));

    /* Allocate one DMA page for buffers (4KB, enough for one full frame) */
    q->buf_phys = pmm_alloc_page();
    if (!q->buf_phys)
        return -1;
    q->buf_virt = phys_to_virt(q->buf_phys);
    memset(q->buf_virt, 0, 4096);

    return 0;
}

/* Pre-post a receive buffer descriptor */
static void rx_post(void) {
    /* Descriptor 0: writable buffer for device to fill */
    rxq.descs[0].addr  = rxq.buf_phys;
    rxq.descs[0].len   = 4096;  /* max frame + net hdr */
    rxq.descs[0].flags = VRING_DESC_F_WRITE;
    rxq.descs[0].next  = 0;

    uint16_t avail_idx = rxq.avail->idx;
    rxq.avail->ring[avail_idx % rxq.size] = 0;
    __asm__ volatile ("" ::: "memory");
    rxq.avail->idx = avail_idx + 1;

    /* Notify device of new RX buffer */
    vio_write16(VIRTIO_REG_QUEUE_NOTIFY, 0);
}

/* ---- Init ---- */

int virtio_net_init(void) {
    struct pci_device dev;
    /* Subsystem ID 1 = network */
    if (pci_find_device_subsys(0x1AF4, 0x1000, 1, &dev) != 0) {
        serial_puts("NET: no virtio-net found\n");
        return -1;
    }
    bar0 = (uint16_t)dev.bar0;
    serial_puts("NET: found virtio-net\n");

    /* 1. Reset */
    vio_write8(VIRTIO_REG_DEVICE_STATUS, 0);

    /* 2. Acknowledge */
    vio_write8(VIRTIO_REG_DEVICE_STATUS, VIRTIO_STATUS_ACK);

    /* 3. Driver */
    vio_write8(VIRTIO_REG_DEVICE_STATUS, VIRTIO_STATUS_ACK | VIRTIO_STATUS_DRIVER);

    /* 4. Feature negotiation — accept none for simplicity */
    (void)vio_read32(VIRTIO_REG_DEVICE_FEATURES);
    vio_write32(VIRTIO_REG_GUEST_FEATURES, 0);

    /* 5. Read MAC address from device-specific config */
    for (int i = 0; i < 6; i++)
        mac_addr[i] = vio_read8(VIRTIO_NET_CFG_MAC + i);

    serial_puts("NET: MAC=");
    for (int i = 0; i < 6; i++) {
        serial_put_hex(mac_addr[i]);
        if (i < 5) serial_putc(':');
    }
    serial_putc('\n');

    /* 6. Setup queues: 0=RX, 1=TX */
    if (setup_queue(0, &rxq) != 0) {
        serial_puts("NET: rxq setup fail\n");
        vio_write8(VIRTIO_REG_DEVICE_STATUS, VIRTIO_STATUS_FAILED);
        return -1;
    }
    if (setup_queue(1, &txq) != 0) {
        serial_puts("NET: txq setup fail\n");
        vio_write8(VIRTIO_REG_DEVICE_STATUS, VIRTIO_STATUS_FAILED);
        return -1;
    }

    /* 7. Driver OK */
    vio_write8(VIRTIO_REG_DEVICE_STATUS,
               VIRTIO_STATUS_ACK | VIRTIO_STATUS_DRIVER | VIRTIO_STATUS_DRIVER_OK);

    /* 8. Pre-post one RX buffer */
    rx_post();

    initialized = 1;
    serial_puts("NET: driver ready\n");
    return 0;
}

/* ---- Send ---- */

int virtio_net_send(const void *frame, uint32_t len) {
    if (!initialized || len == 0 || len > 1514)
        return -1;

    /* Build packet: virtio_net_hdr + Ethernet frame */
    uint8_t *buf = (uint8_t *)txq.buf_virt;
    memset(buf, 0, NET_HDR_SIZE);
    memcpy(buf + NET_HDR_SIZE, frame, len);

    uint32_t total = NET_HDR_SIZE + len;

    /* Single descriptor */
    txq.descs[0].addr  = txq.buf_phys;
    txq.descs[0].len   = total;
    txq.descs[0].flags = 0;  /* device reads */
    txq.descs[0].next  = 0;

    uint16_t avail_idx = txq.avail->idx;
    txq.avail->ring[avail_idx % txq.size] = 0;
    __asm__ volatile ("" ::: "memory");
    txq.avail->idx = avail_idx + 1;

    /* Notify device */
    vio_write16(VIRTIO_REG_QUEUE_NOTIFY, 1);

    /* Poll for completion */
    __asm__ volatile ("" ::: "memory");
    uint32_t timeout = 10000000;
    while (txq.used->idx == txq.last_used) {
        __asm__ volatile ("pause" ::: "memory");
        if (--timeout == 0) {
            serial_puts("NET: tx timeout\n");
            return -1;
        }
    }
    txq.last_used++;

    (void)vio_read8(VIRTIO_REG_ISR_STATUS);
    __asm__ volatile ("" ::: "memory");

    return 0;
}

/* ---- Recv (non-blocking) ---- */

int virtio_net_recv(void *frame, uint32_t max_len) {
    if (!initialized)
        return -1;

    __asm__ volatile ("" ::: "memory");

    /* Check if device has filled our RX buffer */
    if (rxq.used->idx == rxq.last_used)
        return 0;  /* nothing available */

    /* Get the used element */
    uint16_t used_idx = rxq.last_used % rxq.size;
    uint32_t total_len = rxq.used->ring[used_idx].len;
    rxq.last_used++;

    (void)vio_read8(VIRTIO_REG_ISR_STATUS);
    __asm__ volatile ("" ::: "memory");

    /* Strip virtio_net_hdr */
    if (total_len <= NET_HDR_SIZE) {
        rx_post();  /* re-post buffer */
        return 0;
    }

    uint32_t frame_len = total_len - NET_HDR_SIZE;
    if (frame_len > max_len)
        frame_len = max_len;

    uint8_t *buf = (uint8_t *)rxq.buf_virt;
    memcpy(frame, buf + NET_HDR_SIZE, frame_len);

    /* Re-post RX buffer for next packet */
    rx_post();

    return (int)frame_len;
}

/* ---- Get MAC ---- */

void virtio_net_get_mac(uint8_t mac[6]) {
    for (int i = 0; i < 6; i++)
        mac[i] = mac_addr[i];
}
