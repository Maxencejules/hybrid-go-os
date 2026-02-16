#include <stdint.h>
#include <stddef.h>
#include "pmm.h"
#include "limine.h"
#include "serial.h"

/* ------------------------------------------------------------------ */
/*  Bitmap allocator — static 32 KB supports 1 GB at 4 KB granularity */
/* ------------------------------------------------------------------ */

#define BITMAP_SIZE 32768   /* 32768 bytes × 8 bits = 262144 pages = 1 GB */

static uint8_t bitmap[BITMAP_SIZE];
static uint64_t total_usable_pages;

/* External: Limine memmap request (defined in main.c) */
extern struct limine_memmap_request memmap_request;

/* ------------------------------------------------------------------ */
/*  Helpers                                                           */
/* ------------------------------------------------------------------ */

static inline void bitmap_set(uint64_t page) {
    if (page / 8 < BITMAP_SIZE)
        bitmap[page / 8] |= (1 << (page % 8));
}

static inline void bitmap_clear(uint64_t page) {
    if (page / 8 < BITMAP_SIZE)
        bitmap[page / 8] &= ~(1 << (page % 8));
}

static inline int bitmap_test(uint64_t page) {
    if (page / 8 >= BITMAP_SIZE)
        return 1;  /* Out of range → reserved */
    return (bitmap[page / 8] >> (page % 8)) & 1;
}

/* ------------------------------------------------------------------ */
/*  pmm_init                                                          */
/* ------------------------------------------------------------------ */

void pmm_init(void) {
    /* Mark all pages as reserved (bit set = reserved) */
    for (uint64_t i = 0; i < BITMAP_SIZE; i++)
        bitmap[i] = 0xFF;

    total_usable_pages = 0;

    struct limine_memmap_response *resp = memmap_request.response;
    if (!resp) {
        serial_puts("MM: no memmap response\n");
        return;
    }

    for (uint64_t i = 0; i < resp->entry_count; i++) {
        struct limine_memmap_entry *e = resp->entries[i];
        if (e->type != LIMINE_MEMMAP_USABLE)
            continue;

        uint64_t start_page = e->base / PAGE_SIZE;
        uint64_t page_count = e->length / PAGE_SIZE;

        for (uint64_t p = start_page; p < start_page + page_count; p++) {
            bitmap_clear(p);
            total_usable_pages++;
        }
    }

    serial_puts("MM: ");
    serial_put_hex(total_usable_pages);
    serial_puts(" usable pages\n");
}

/* ------------------------------------------------------------------ */
/*  pmm_alloc_page / pmm_free_page                                    */
/* ------------------------------------------------------------------ */

uint64_t pmm_alloc_page(void) {
    for (uint64_t i = 0; i < BITMAP_SIZE; i++) {
        if (bitmap[i] == 0xFF)
            continue;
        for (int bit = 0; bit < 8; bit++) {
            if (!(bitmap[i] & (1 << bit))) {
                bitmap[i] |= (1 << bit);
                return (i * 8 + bit) * PAGE_SIZE;
            }
        }
    }
    return 0;  /* Out of memory */
}

void pmm_free_page(uint64_t paddr) {
    uint64_t page = paddr / PAGE_SIZE;
    bitmap_clear(page);
}
