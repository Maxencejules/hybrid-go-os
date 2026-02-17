#![no_std]

use core::panic::PanicInfo;

// --------------- Port I/O ---------------

#[inline(always)]
unsafe fn outb(port: u16, value: u8) {
    core::arch::asm!("out dx, al", in("dx") port, in("al") value, options(nomem, nostack));
}

// --------------- Serial (COM1) ---------------

const COM1: u16 = 0x3F8;

fn serial_init() {
    unsafe {
        outb(COM1 + 1, 0x00); // Disable interrupts
        outb(COM1 + 3, 0x80); // DLAB on
        outb(COM1 + 0, 0x01); // Baud divisor low (115200)
        outb(COM1 + 1, 0x00); // Baud divisor high
        outb(COM1 + 3, 0x03); // 8N1, DLAB off
        outb(COM1 + 2, 0x00); // Disable FIFO
        outb(COM1 + 4, 0x00); // No modem control
    }
}

fn serial_write(s: &[u8]) {
    for &b in s {
        unsafe {
            outb(COM1, b);
        }
    }
}

// --------------- Limine boot protocol markers (v8 API) ---------------

#[used]
#[link_section = ".limine_requests_start"]
static LIMINE_REQUESTS_START: [u64; 4] = [
    0xf6b8f4b39de7d1ae,
    0xfab91a6940fcb9cf,
    0x785c6ed015d3e316,
    0x181e920a7852b9d9,
];

#[used]
#[link_section = ".limine_requests"]
static LIMINE_BASE_REVISION: [u64; 3] = [
    0xf9562b2d5c95a6c8,
    0x6a7b384944536bdc,
    3,
];

#[used]
#[link_section = ".limine_requests_end"]
static LIMINE_REQUESTS_END: [u64; 2] = [
    0xadc0e0531bb10d03,
    0x9572709f31764c62,
];

// --------------- QEMU debug exit ---------------

const DEBUG_EXIT_PORT: u16 = 0xF4;

fn qemu_exit(code: u8) {
    unsafe {
        outb(DEBUG_EXIT_PORT, code);
    }
}

// --------------- Kernel entry ---------------

#[no_mangle]
pub extern "C" fn kmain() -> ! {
    serial_init();
    serial_write(b"RUGO: boot ok\n");
    serial_write(b"RUGO: halt ok\n");

    #[cfg(feature = "panic_test")]
    panic!("deliberate test panic");

    #[cfg(not(feature = "panic_test"))]
    {
        // Normal path: clean QEMU exit
        qemu_exit(0x31);
        loop {
            unsafe {
                core::arch::asm!("cli; hlt", options(nomem, nostack));
            }
        }
    }
}

// --------------- Panic handler ---------------

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    serial_write(b"RUGO: panic code=0xDEAD\n");

    // Exit QEMU (exit code = (0x31 << 1) | 1 = 99)
    qemu_exit(0x31);

    loop {
        unsafe {
            core::arch::asm!("cli; hlt", options(nomem, nostack));
        }
    }
}
