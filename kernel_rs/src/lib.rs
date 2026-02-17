#![no_std]
#![allow(static_mut_refs)]

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
        unsafe { outb(COM1, b); }
    }
}

fn serial_write_hex(val: u64) {
    const HEX: &[u8; 16] = b"0123456789ABCDEF";
    let mut buf = [b'0'; 16];
    let mut v = val;
    for i in (0..16).rev() {
        buf[i] = HEX[(v & 0xF) as usize];
        v >>= 4;
    }
    serial_write(&buf);
}

// --------------- Limine boot protocol markers (v8 API) ---------------

#[used]
#[link_section = ".limine_requests_start"]
static LIMINE_REQUESTS_START: [u64; 4] = [
    0xf6b8f4b39de7d1ae, 0xfab91a6940fcb9cf,
    0x785c6ed015d3e316, 0x181e920a7852b9d9,
];

#[used]
#[link_section = ".limine_requests"]
static LIMINE_BASE_REVISION: [u64; 3] = [
    0xf9562b2d5c95a6c8, 0x6a7b384944536bdc, 3,
];

#[used]
#[link_section = ".limine_requests_end"]
static LIMINE_REQUESTS_END: [u64; 2] = [
    0xadc0e0531bb10d03, 0x9572709f31764c62,
];

// --------------- QEMU debug exit ---------------

const DEBUG_EXIT_PORT: u16 = 0xF4;

fn qemu_exit(code: u8) {
    unsafe { outb(DEBUG_EXIT_PORT, code); }
}

// --------------- GDT ---------------

#[repr(C, packed)]
struct DtPtr {
    limit: u16,
    base: u64,
}

// Must be mutable: CPU writes the Accessed bit when loading segment registers
static mut GDT: [u64; 3] = [
    0x0000_0000_0000_0000, // Null descriptor
    0x00AF_9A00_0000_FFFF, // 64-bit code segment (selector 0x08)
    0x00CF_9200_0000_FFFF, // Data segment (selector 0x10)
];

unsafe fn gdt_init() {
    let limit = (core::mem::size_of_val(&GDT) - 1) as u16;
    let base = GDT.as_ptr() as u64;
    let ptr = DtPtr { limit, base };
    core::arch::asm!("lgdt [{}]", in(reg) &ptr);

    // Reload CS via far return, then reload data segment registers
    core::arch::asm!(
        "push 0x08",
        "lea {tmp}, [rip + 2f]",
        "push {tmp}",
        ".byte 0x48, 0xCB",
        "2:",
        "mov {tmp:x}, 0x10",
        "mov ds, {tmp:x}",
        "mov es, {tmp:x}",
        "mov fs, {tmp:x}",
        "mov gs, {tmp:x}",
        "mov ss, {tmp:x}",
        tmp = lateout(reg) _,
    );
}

// --------------- IDT ---------------

#[derive(Clone, Copy)]
#[repr(C, packed)]
struct IdtEntry {
    offset_low: u16,
    selector: u16,
    ist: u8,
    type_attr: u8,
    offset_mid: u16,
    offset_high: u32,
    reserved: u32,
}

impl IdtEntry {
    const NULL: Self = Self {
        offset_low: 0, selector: 0, ist: 0, type_attr: 0,
        offset_mid: 0, offset_high: 0, reserved: 0,
    };
}

static mut IDT: [IdtEntry; 256] = [IdtEntry::NULL; 256];

unsafe fn idt_set_gate(vector: usize, handler: u64) {
    IDT[vector] = IdtEntry {
        offset_low: handler as u16,
        selector: 0x08,
        ist: 0,
        type_attr: 0x8E, // Present, DPL=0, 64-bit interrupt gate
        offset_mid: (handler >> 16) as u16,
        offset_high: (handler >> 32) as u32,
        reserved: 0,
    };
}

unsafe fn idt_init() {
    extern "C" {
        fn isr_stub_0();
        fn isr_stub_3();
        fn isr_stub_8();
        fn isr_stub_13();
        fn isr_stub_14();
    }

    idt_set_gate(0,  isr_stub_0  as *const () as u64);
    idt_set_gate(3,  isr_stub_3  as *const () as u64);
    idt_set_gate(8,  isr_stub_8  as *const () as u64);
    idt_set_gate(13, isr_stub_13 as *const () as u64);
    idt_set_gate(14, isr_stub_14 as *const () as u64);

    let ptr = DtPtr {
        limit: (256 * core::mem::size_of::<IdtEntry>() - 1) as u16,
        base: IDT.as_ptr() as u64,
    };
    core::arch::asm!("lidt [{}]", in(reg) &ptr, options(nostack));
}

// --------------- Exception handler (called from ISR stubs) ---------------

#[no_mangle]
pub extern "C" fn exception_handler(vector: u64, error_code: u64, _rip: u64, cr2: u64) {
    match vector {
        0 => serial_write(b"TRAP: div0\n"),
        3 => serial_write(b"TRAP: ok\n"),
        8 => serial_write(b"TRAP: double fault\n"),
        13 => {
            serial_write(b"TRAP: gpf err=0x");
            serial_write_hex(error_code);
            serial_write(b"\n");
        }
        14 => {
            serial_write(b"PF: addr=0x");
            serial_write_hex(cr2);
            serial_write(b" err=0x");
            serial_write_hex(error_code);
            serial_write(b"\n");
        }
        _ => serial_write(b"TRAP: unknown\n"),
    }
    qemu_exit(0x31);
    loop {
        unsafe { core::arch::asm!("cli; hlt", options(nomem, nostack)); }
    }
}

// --------------- Paging verification ---------------

fn check_paging() {
    let cr0: u64;
    unsafe {
        core::arch::asm!("mov {}, cr0", out(reg) cr0, options(nomem, nostack));
    }
    if cr0 & (1 << 31) != 0 {
        serial_write(b"MM: paging=on\n");
    } else {
        serial_write(b"MM: paging=off\n");
    }
}

// --------------- Kernel entry ---------------

#[no_mangle]
pub extern "C" fn kmain() -> ! {
    serial_init();
    serial_write(b"RUGO: boot ok\n");

    // M1: verify paging is active
    check_paging();

    // M1: set up GDT and IDT
    unsafe {
        gdt_init();
        idt_init();
    }

    // Feature-gated test paths (each triggers an exception → handler exits QEMU)
    #[cfg(feature = "pf_test")]
    unsafe {
        let p = 0x0000_0040_0000_0000u64 as *const u8;
        core::ptr::read_volatile(p);
    }

    #[cfg(feature = "idt_smoke_test")]
    unsafe {
        core::arch::asm!("int3", options(nomem, nostack));
    }

    serial_write(b"RUGO: halt ok\n");

    #[cfg(feature = "panic_test")]
    panic!("deliberate test panic");

    #[cfg(not(feature = "panic_test"))]
    {
        qemu_exit(0x31);
        loop {
            unsafe { core::arch::asm!("cli; hlt", options(nomem, nostack)); }
        }
    }
}

// --------------- Panic handler ---------------

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    serial_write(b"RUGO: panic code=0xDEAD\n");
    qemu_exit(0x31);
    loop {
        unsafe { core::arch::asm!("cli; hlt", options(nomem, nostack)); }
    }
}
