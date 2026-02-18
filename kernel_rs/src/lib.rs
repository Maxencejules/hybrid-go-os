#![no_std]
#![allow(static_mut_refs)]

use core::panic::PanicInfo;

// Shorthand for "any M3 user-mode test feature is active"
macro_rules! cfg_m3 {
    ($($item:item)*) => {
        $(
            #[cfg(any(feature = "user_hello_test", feature = "syscall_test", feature = "user_fault_test"))]
            $item
        )*
    };
}

// Shorthand for "any user-mode feature (M3 or R4)"
macro_rules! cfg_user {
    ($($item:item)*) => {
        $(
            #[cfg(any(
                feature = "user_hello_test", feature = "syscall_test", feature = "user_fault_test",
                feature = "ipc_test", feature = "shm_test",
            ))]
            $item
        )*
    };
}

// Shorthand for "any R4 feature"
macro_rules! cfg_r4 {
    ($($item:item)*) => {
        $(
            #[cfg(any(feature = "ipc_test", feature = "shm_test"))]
            $item
        )*
    };
}

// --------------- Port I/O ---------------

#[inline(always)]
unsafe fn outb(port: u16, value: u8) {
    core::arch::asm!("out dx, al", in("dx") port, in("al") value, options(nomem, nostack));
}

#[inline(always)]
unsafe fn inb(port: u16) -> u8 {
    let val: u8;
    core::arch::asm!("in al, dx", out("al") val, in("dx") port, options(nomem, nostack));
    val
}

// --------------- Serial (COM1) ---------------

const COM1: u16 = 0x3F8;

fn serial_init() {
    unsafe {
        outb(COM1 + 1, 0x00);
        outb(COM1 + 3, 0x80);
        outb(COM1 + 0, 0x01);
        outb(COM1 + 1, 0x00);
        outb(COM1 + 3, 0x03);
        outb(COM1 + 2, 0x00);
        outb(COM1 + 4, 0x00);
    }
}

fn serial_write(s: &[u8]) {
    for &b in s {
        unsafe {
            while inb(COM1 + 5) & 0x20 == 0 {}
            outb(COM1, b);
        }
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

// --------------- Limine HHDM request ---------------

#[repr(C)]
struct LimineHhdmResponse {
    revision: u64,
    offset: u64,
}

#[repr(C)]
struct LimineHhdmRequest {
    id: [u64; 4],
    revision: u64,
    response: *const LimineHhdmResponse,
}

unsafe impl Sync for LimineHhdmRequest {}

#[used]
#[link_section = ".limine_requests"]
static mut HHDM_REQUEST: LimineHhdmRequest = LimineHhdmRequest {
    id: [0xc7b1dd30df4c8b88, 0x0a82e883a194f07b,
         0x48dcf1cb8ad2b852, 0x63984e959a98244b],
    revision: 0,
    response: core::ptr::null(),
};

// --------------- Limine kernel address request ---------------

#[repr(C)]
struct LimineKaddrResponse {
    revision: u64,
    physical_base: u64,
    virtual_base: u64,
}

#[repr(C)]
struct LimineKaddrRequest {
    id: [u64; 4],
    revision: u64,
    response: *const LimineKaddrResponse,
}

unsafe impl Sync for LimineKaddrRequest {}

#[used]
#[link_section = ".limine_requests"]
static mut KADDR_REQUEST: LimineKaddrRequest = LimineKaddrRequest {
    id: [0xc7b1dd30df4c8b88, 0x0a82e883a194f07b,
         0x71ba76863cc55f63, 0xb2644a48c516a487],
    revision: 0,
    response: core::ptr::null(),
};

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

static mut GDT: [u64; 7] = [
    0x0000_0000_0000_0000, // 0x00 Null
    0x00AF_9A00_0000_FFFF, // 0x08 Kernel code 64-bit (DPL=0)
    0x00CF_9200_0000_FFFF, // 0x10 Kernel data (DPL=0)
    0x00CF_F200_0000_FFFF, // 0x18 User data (DPL=3)
    0x00AF_FA00_0000_FFFF, // 0x20 User code 64-bit (DPL=3)
    0,                      // 0x28 TSS descriptor low
    0,                      // 0x30 TSS descriptor high
];

unsafe fn gdt_init() {
    let limit = (core::mem::size_of_val(&GDT) - 1) as u16;
    let base = GDT.as_ptr() as u64;
    let ptr = DtPtr { limit, base };
    core::arch::asm!("lgdt [{}]", in(reg) &ptr);
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

// --------------- TSS (needed for ring 3 -> ring 0 transitions) ---------------

cfg_user! {
    #[repr(C, packed)]
    struct Tss {
        reserved0: u32,
        rsp0: u64,
        rsp1: u64,
        rsp2: u64,
        reserved1: u64,
        ist: [u64; 7],
        reserved2: u64,
        reserved3: u16,
        iopb_offset: u16,
    }

    static mut TSS: Tss = Tss {
        reserved0: 0,
        rsp0: 0, rsp1: 0, rsp2: 0,
        reserved1: 0,
        ist: [0; 7],
        reserved2: 0,
        reserved3: 0,
        iopb_offset: 104,
    };

    unsafe fn tss_init(kernel_stack_top: u64) {
        TSS.rsp0 = kernel_stack_top;
        let tss_addr = &TSS as *const Tss as u64;
        GDT[5] = (103u64)
                | ((tss_addr & 0xFFFF) << 16)
                | (((tss_addr >> 16) & 0xFF) << 32)
                | (0x89u64 << 40)
                | (((tss_addr >> 24) & 0xFF) << 56);
        GDT[6] = tss_addr >> 32;
        let limit = (core::mem::size_of_val(&GDT) - 1) as u16;
        let base = GDT.as_ptr() as u64;
        let gdt_ptr = DtPtr { limit, base };
        core::arch::asm!("lgdt [{}]", in(reg) &gdt_ptr);
        core::arch::asm!(
            "mov ax, 0x28",
            "ltr ax",
            out("ax") _,
            options(nostack),
        );
    }
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
        type_attr: 0x8E,
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
        fn isr_stub_32();
        fn isr_stub_128();
    }

    idt_set_gate(0,  isr_stub_0  as *const () as u64);
    idt_set_gate(3,  isr_stub_3  as *const () as u64);
    idt_set_gate(8,  isr_stub_8  as *const () as u64);
    idt_set_gate(13, isr_stub_13 as *const () as u64);
    idt_set_gate(14, isr_stub_14 as *const () as u64);
    idt_set_gate(32, isr_stub_32 as *const () as u64);

    let handler = isr_stub_128 as *const () as u64;
    IDT[128] = IdtEntry {
        offset_low: handler as u16,
        selector: 0x08,
        ist: 0,
        type_attr: 0xEE, // DPL=3
        offset_mid: (handler >> 16) as u16,
        offset_high: (handler >> 32) as u32,
        reserved: 0,
    };

    let ptr = DtPtr {
        limit: (256 * core::mem::size_of::<IdtEntry>() - 1) as u16,
        base: IDT.as_ptr() as u64,
    };
    core::arch::asm!("lidt [{}]", in(reg) &ptr, options(nostack));
}

// --------------- Trap handler ------------------------------------------------
//
// Frame layout (22 u64s):
//   [0..14]  r15 r14 r13 r12 r11 r10 r9 r8 rbp rdi rsi rdx rcx rbx rax
//   [15] int_num  [16] error_code
//   [17] rip  [18] cs  [19] rflags  [20] rsp  [21] ss

#[no_mangle]
pub extern "C" fn trap_handler(frame: *mut u64) {
    unsafe {
        let int_num = *frame.add(15);
        let error_code = *frame.add(16);

        match int_num {
            0 => {
                serial_write(b"TRAP: div0\n");
                qemu_exit(0x31);
                loop { core::arch::asm!("cli; hlt", options(nomem, nostack)); }
            }
            3 => {
                serial_write(b"TRAP: ok\n");
                qemu_exit(0x31);
                loop { core::arch::asm!("cli; hlt", options(nomem, nostack)); }
            }
            8 => {
                serial_write(b"TRAP: double fault\n");
                qemu_exit(0x31);
                loop { core::arch::asm!("cli; hlt", options(nomem, nostack)); }
            }
            13 => {
                let cs = *frame.add(18);
                if cs & 3 == 3 {
                    handle_user_fault(frame);
                    return;
                }
                serial_write(b"TRAP: gpf err=0x");
                serial_write_hex(error_code);
                serial_write(b"\n");
                qemu_exit(0x31);
                loop { core::arch::asm!("cli; hlt", options(nomem, nostack)); }
            }
            14 => {
                let cs = *frame.add(18);
                if cs & 3 == 3 {
                    handle_user_fault(frame);
                    return;
                }
                let cr2: u64;
                core::arch::asm!("mov {}, cr2", out(reg) cr2, options(nomem, nostack));
                serial_write(b"PF: addr=0x");
                serial_write_hex(cr2);
                serial_write(b" err=0x");
                serial_write_hex(error_code);
                serial_write(b"\n");
                qemu_exit(0x31);
                loop { core::arch::asm!("cli; hlt", options(nomem, nostack)); }
            }
            #[cfg(feature = "sched_test")]
            32 => {
                TICK_COUNT += 1;
                if TICK_COUNT == 100 {
                    serial_write(b"TICK: 100\n");
                }
                pic_send_eoi(0);
                if TICK_COUNT >= 400 {
                    qemu_exit(0x31);
                    loop { core::arch::asm!("cli; hlt", options(nomem, nostack)); }
                }
                schedule();
            }
            128 => {
                syscall_dispatch(frame);
            }
            _ => {}
        }
    }
}

// --------------- User fault containment --------------------------------------

extern "C" fn user_fault_return() -> ! {
    serial_write(b"RUGO: halt ok\n");
    qemu_exit(0x31);
    loop {
        unsafe { core::arch::asm!("cli; hlt", options(nomem, nostack)); }
    }
}

extern "C" { static stack_top: u8; }

unsafe fn handle_user_fault(frame: *mut u64) {
    // R4: kill current task and switch to next
    #[cfg(any(feature = "ipc_test", feature = "shm_test"))]
    {
        r4_kill_and_switch(frame);
        return;
    }

    // M3: kill user task and return to kernel
    #[cfg(not(any(feature = "ipc_test", feature = "shm_test")))]
    {
        serial_write(b"USER: killed\n");
        let kstack = &stack_top as *const u8 as u64;
        *frame.add(17) = user_fault_return as *const () as u64;
        *frame.add(18) = 0x08;
        *frame.add(19) = 0x02;
        *frame.add(20) = kstack;
        *frame.add(21) = 0x10;
    }
}

// --------------- Syscall dispatch (int 0x80) ---------------------------------

cfg_user! {
    static mut HHDM_OFFSET: u64 = 0;
}

cfg_m3! {
    static mut MONOTONIC_TICK: u64 = 1;
}

unsafe fn syscall_dispatch(frame: *mut u64) {
    let nr   = *frame.add(14); // rax
    let arg1 = *frame.add(9);  // rdi
    let arg2 = *frame.add(10); // rsi
    let arg3 = *frame.add(11); // rdx

    // R4 dispatch
    #[cfg(any(feature = "ipc_test", feature = "shm_test"))]
    {
        match nr {
            0  => { *frame.add(14) = sys_debug_write(arg1, arg2); }
            6  => { *frame.add(14) = sys_shm_create_r4(arg1); }
            7  => { *frame.add(14) = sys_shm_map_r4(arg1, arg2, arg3); }
            8  => { *frame.add(14) = sys_ipc_send_r4(arg1, arg2, arg3); }
            9  => { sys_ipc_recv_r4(frame, arg1, arg2, arg3); } // may swap frame
            10 => { *frame.add(14) = sys_time_now(); }
            11 => { *frame.add(14) = sys_svc_register_r4(arg1, arg2, arg3); }
            12 => { *frame.add(14) = sys_svc_lookup_r4(arg1, arg2); }
            _  => { *frame.add(14) = 0xFFFF_FFFF_FFFF_FFFF; }
        }
        return;
    }

    // M3 dispatch
    #[cfg(not(any(feature = "ipc_test", feature = "shm_test")))]
    {
        let ret: u64 = match nr {
            0  => sys_debug_write(arg1, arg2),
            10 => sys_time_now(),
            _  => 0xFFFF_FFFF_FFFF_FFFF,
        };
        *frame.add(14) = ret;
    }
}

unsafe fn sys_debug_write(buf: u64, len: u64) -> u64 {
    let max_len = 256u64;
    let actual_len = if len > max_len { max_len } else { len };
    if actual_len == 0 { return 0; }
    if buf >= 0x0000_8000_0000_0000 { return 0xFFFF_FFFF_FFFF_FFFF; }
    if buf.checked_add(actual_len).is_none() || buf + actual_len > 0x0000_8000_0000_0000 {
        return 0xFFFF_FFFF_FFFF_FFFF;
    }

    #[cfg(any(
        feature = "user_hello_test", feature = "syscall_test", feature = "user_fault_test",
        feature = "ipc_test", feature = "shm_test",
    ))]
    {
        let hhdm = HHDM_OFFSET;
        let start_page = buf & !0xFFF;
        let end_page = (buf + actual_len - 1) & !0xFFF;
        let mut page = start_page;
        loop {
            if !check_page_user_accessible(page, hhdm) {
                return 0xFFFF_FFFF_FFFF_FFFF;
            }
            if page >= end_page { break; }
            page += 4096;
        }
    }

    let mut kbuf = [0u8; 256];
    let n = actual_len as usize;
    core::ptr::copy_nonoverlapping(buf as *const u8, kbuf.as_mut_ptr(), n);
    serial_write(&kbuf[..n]);
    actual_len
}

unsafe fn sys_time_now() -> u64 {
    #[cfg(any(feature = "user_hello_test", feature = "syscall_test", feature = "user_fault_test"))]
    {
        let t = MONOTONIC_TICK;
        MONOTONIC_TICK += 1;
        return t;
    }
    #[cfg(not(any(feature = "user_hello_test", feature = "syscall_test", feature = "user_fault_test")))]
    { 0 }
}

// --------------- User pointer validation (page table walk) -------------------

#[cfg(any(
    feature = "user_hello_test", feature = "syscall_test", feature = "user_fault_test",
    feature = "ipc_test", feature = "shm_test",
))]
unsafe fn check_page_user_accessible(va: u64, hhdm: u64) -> bool {
    let cr3: u64;
    core::arch::asm!("mov {}, cr3", out(reg) cr3, options(nomem, nostack));
    let pml4_phys = cr3 & 0x000F_FFFF_FFFF_F000;
    let pml4 = (pml4_phys + hhdm) as *const u64;
    let pml4e = *pml4.add(((va >> 39) & 0x1FF) as usize);
    if pml4e & 1 == 0 || pml4e & 4 == 0 { return false; }
    let pdpt = ((pml4e & 0x000F_FFFF_FFFF_F000) + hhdm) as *const u64;
    let pdpte = *pdpt.add(((va >> 30) & 0x1FF) as usize);
    if pdpte & 1 == 0 || pdpte & 4 == 0 { return false; }
    if pdpte & 0x80 != 0 { return true; }
    let pd = ((pdpte & 0x000F_FFFF_FFFF_F000) + hhdm) as *const u64;
    let pde = *pd.add(((va >> 21) & 0x1FF) as usize);
    if pde & 1 == 0 || pde & 4 == 0 { return false; }
    if pde & 0x80 != 0 { return true; }
    let pt = ((pde & 0x000F_FFFF_FFFF_F000) + hhdm) as *const u64;
    let pte = *pt.add(((va >> 12) & 0x1FF) as usize);
    pte & 1 != 0 && pte & 4 != 0
}

// --------------- User page table infrastructure (shared M3+R4) ---------------

cfg_user! {
    const USER_CODE_VA: u64   = 0x40_0000;
    const USER_STACK_TOP: u64 = 0x80_0000;

    #[repr(C, align(4096))]
    struct Page([u8; 4096]);

    static mut USER_PML4:      Page = Page([0; 4096]);
    static mut USER_PDPT:      Page = Page([0; 4096]);
    static mut USER_PD:        Page = Page([0; 4096]);
    static mut USER_PT_CODE:   Page = Page([0; 4096]);
    static mut USER_PT_STACK:  Page = Page([0; 4096]);
    static mut USER_CODE_PAGE: Page = Page([0; 4096]);
    static mut USER_STACK_PAGE: Page = Page([0; 4096]);

    unsafe fn enter_ring3_at(code_va: u64, user_sp: u64) -> ! {
        core::arch::asm!(
            "push 0x1B",       // SS = user data (0x18 | RPL=3)
            "push {stack}",    // RSP
            "push 0x002",      // RFLAGS (IF=0)
            "push 0x23",       // CS = user code (0x20 | RPL=3)
            "push {code}",     // RIP
            "iretq",
            stack = in(reg) user_sp,
            code = in(reg) code_va,
            options(noreturn),
        );
    }
}

// --------------- M3: User page setup -----------------------------------------

cfg_m3! {
    unsafe fn setup_user_pages(user_code: &[u8]) {
        let hhdm_resp_ptr = core::ptr::read_volatile(
            core::ptr::addr_of!(HHDM_REQUEST.response));
        let kaddr_resp_ptr = core::ptr::read_volatile(
            core::ptr::addr_of!(KADDR_REQUEST.response));
        let hhdm = (*hhdm_resp_ptr).offset;
        let kphys = (*kaddr_resp_ptr).physical_base;
        let kvirt = (*kaddr_resp_ptr).virtual_base;
        HHDM_OFFSET = hhdm;
        let kv2p = |va: u64| -> u64 { va - kvirt + kphys };

        let cr3: u64;
        core::arch::asm!("mov {}, cr3", out(reg) cr3, options(nomem, nostack));
        let old_pml4_phys = cr3 & 0x000F_FFFF_FFFF_F000;
        let old_pml4 = (old_pml4_phys + hhdm) as *const u64;
        let new_pml4 = USER_PML4.0.as_mut_ptr() as *mut u64;
        for i in 0..512 { *new_pml4.add(i) = *old_pml4.add(i); }

        let pdpt = USER_PDPT.0.as_mut_ptr() as *mut u64;
        *pdpt = kv2p(USER_PD.0.as_ptr() as u64) | 0x07;

        let pd = USER_PD.0.as_mut_ptr() as *mut u64;
        *pd.add(2) = kv2p(USER_PT_CODE.0.as_ptr() as u64) | 0x07;
        *pd.add(3) = kv2p(USER_PT_STACK.0.as_ptr() as u64) | 0x07;

        let pt_code = USER_PT_CODE.0.as_mut_ptr() as *mut u64;
        *pt_code = kv2p(USER_CODE_PAGE.0.as_ptr() as u64) | 0x05;

        let pt_stack = USER_PT_STACK.0.as_mut_ptr() as *mut u64;
        *pt_stack.add(511) = kv2p(USER_STACK_PAGE.0.as_ptr() as u64) | 0x07;

        *new_pml4 = kv2p(USER_PDPT.0.as_ptr() as u64) | 0x07;

        core::ptr::copy_nonoverlapping(
            user_code.as_ptr(), USER_CODE_PAGE.0.as_mut_ptr(), user_code.len());

        let new_pml4_phys = kv2p(new_pml4 as u64);
        core::arch::asm!("mov cr3, {}", in(reg) new_pml4_phys, options(nostack));
    }
}

// --------------- M3: User program blobs --------------------------------------

cfg_m3! {
    static USER_HELLO_BLOB: [u8; 32] = [
        0x48, 0x8d, 0x3d, 0x0d, 0x00, 0x00, 0x00,
        0x48, 0xc7, 0xc6, 0x0c, 0x00, 0x00, 0x00,
        0x31, 0xc0,
        0xcd, 0x80,
        0xf4, 0x00,
        b'U', b'S', b'E', b'R', b':', b' ',
        b'h', b'e', b'l', b'l', b'o', b'\n',
    ];

    static USER_SYSCALL_BLOB: [u8; 41] = [
        0xb8, 0x0a, 0x00, 0x00, 0x00,
        0xcd, 0x80,
        0x48, 0x8d, 0x3d, 0x0f, 0x00, 0x00, 0x00,
        0x48, 0xc7, 0xc6, 0x0c, 0x00, 0x00, 0x00,
        0x31, 0xc0,
        0xcd, 0x80,
        0xf4, 0x00, 0x00, 0x00,
        b'S', b'Y', b'S', b'C', b'A', b'L', b'L',
        b':', b' ', b'o', b'k', b'\n',
    ];

    static USER_FAULT_BLOB: [u8; 9] = [
        0xb8, 0x00, 0x00, 0xad, 0xde,
        0xc6, 0x00, 0x42,
        0xf4,
    ];
}

// =============================================================================
// R4: IPC + shared memory + service registry
// =============================================================================

// --------------- R4: Additional pages for second task -------------------------

cfg_r4! {
    const USER_CODE2_VA: u64   = 0x40_1000;
    const USER_STACK2_TOP: u64 = 0x7F_F000;

    static mut USER_CODE_PAGE_2:  Page = Page([0; 4096]);
    static mut USER_STACK_PAGE_2: Page = Page([0; 4096]);
}

// --------------- R4: SHM backing pages ---------------------------------------

#[cfg(feature = "shm_test")]
const R4_MAX_SHM: usize = 2;

#[cfg(feature = "shm_test")]
struct ShmObject {
    active: bool,
    size: usize,
}

#[cfg(feature = "shm_test")]
static mut R4_SHM_PAGES: [Page; 2] = [Page([0; 4096]), Page([0; 4096])];

#[cfg(feature = "shm_test")]
static mut R4_SHM_OBJECTS: [ShmObject; 2] = [
    ShmObject { active: false, size: 0 },
    ShmObject { active: false, size: 0 },
];

// --------------- R4: Task model ----------------------------------------------

cfg_r4! {
    const R4_MAX_TASKS: usize = 2;

    #[derive(Clone, Copy, PartialEq)]
    enum R4State { Ready, Running, Blocked, Dead }

    #[derive(Clone, Copy)]
    struct R4Task {
        saved_frame: [u64; 22],
        state: R4State,
        recv_ep: u64,
        recv_buf: u64,
        recv_cap: u64,
    }

    impl R4Task {
        const EMPTY: Self = Self {
            saved_frame: [0u64; 22],
            state: R4State::Dead,
            recv_ep: 0, recv_buf: 0, recv_cap: 0,
        };
    }

    static mut R4_TASKS: [R4Task; R4_MAX_TASKS] = [R4Task::EMPTY; R4_MAX_TASKS];
    static mut R4_CURRENT: usize = 0;
    static mut R4_NUM_TASKS: usize = 0;

    unsafe fn r4_init_task(tid: usize, code_va: u64, stk_top: u64) {
        R4_TASKS[tid].saved_frame = [0u64; 22];
        R4_TASKS[tid].saved_frame[17] = code_va;  // RIP
        R4_TASKS[tid].saved_frame[18] = 0x23;     // CS (user code RPL=3)
        R4_TASKS[tid].saved_frame[19] = 0x02;     // RFLAGS
        R4_TASKS[tid].saved_frame[20] = stk_top;  // RSP
        R4_TASKS[tid].saved_frame[21] = 0x1B;     // SS (user data RPL=3)
        R4_TASKS[tid].state = R4State::Ready;
    }

    unsafe fn r4_find_ready(exclude: usize) -> Option<usize> {
        for i in 0..R4_NUM_TASKS {
            if i != exclude && R4_TASKS[i].state == R4State::Ready {
                return Some(i);
            }
        }
        None
    }

    unsafe fn r4_switch_to(frame: *mut u64, tid: usize) {
        for i in 0..22 { *frame.add(i) = R4_TASKS[tid].saved_frame[i]; }
        R4_TASKS[tid].state = R4State::Running;
        R4_CURRENT = tid;
    }

    unsafe fn r4_save_frame(frame: *mut u64, tid: usize) {
        for i in 0..22 { R4_TASKS[tid].saved_frame[i] = *frame.add(i); }
    }

    unsafe fn r4_kill_and_switch(frame: *mut u64) {
        R4_TASKS[R4_CURRENT].state = R4State::Dead;
        match r4_find_ready(R4_CURRENT) {
            Some(tid) => { r4_switch_to(frame, tid); }
            None => {
                // All tasks done — exit
                let kstack = &stack_top as *const u8 as u64;
                *frame.add(17) = r4_all_done as *const () as u64;
                *frame.add(18) = 0x08;
                *frame.add(19) = 0x02;
                *frame.add(20) = kstack;
                *frame.add(21) = 0x10;
            }
        }
    }

    extern "C" fn r4_all_done() -> ! {
        qemu_exit(0x31);
        loop { unsafe { core::arch::asm!("cli; hlt", options(nomem, nostack)); } }
    }
}

// --------------- R4: IPC endpoints -------------------------------------------

cfg_r4! {
    const R4_MAX_ENDPOINTS: usize = 4;
    const R4_MAX_MSG_LEN: usize = 256;

    struct IpcEndpoint {
        active: bool,
        has_msg: bool,
        msg_data: [u8; R4_MAX_MSG_LEN],
        msg_len: usize,
        waiter: i32, // task id blocked on recv, or -1
    }

    impl IpcEndpoint {
        const EMPTY: Self = Self {
            active: false, has_msg: false,
            msg_data: [0u8; R4_MAX_MSG_LEN], msg_len: 0,
            waiter: -1,
        };
    }

    static mut R4_ENDPOINTS: [IpcEndpoint; R4_MAX_ENDPOINTS] =
        [IpcEndpoint::EMPTY, IpcEndpoint::EMPTY, IpcEndpoint::EMPTY, IpcEndpoint::EMPTY];

    unsafe fn sys_ipc_send_r4(endpoint: u64, buf: u64, len: u64) -> u64 {
        let ep = endpoint as usize;
        if ep >= R4_MAX_ENDPOINTS || !R4_ENDPOINTS[ep].active {
            return 0xFFFF_FFFF_FFFF_FFFF;
        }
        let n = if len > R4_MAX_MSG_LEN as u64 { R4_MAX_MSG_LEN } else { len as usize };
        if buf >= 0x0000_8000_0000_0000 { return 0xFFFF_FFFF_FFFF_FFFF; }
        if n > 0 && buf + n as u64 > 0x0000_8000_0000_0000 { return 0xFFFF_FFFF_FFFF_FFFF; }

        // Copy from user to kernel buffe
        let mut kbuf = [0u8; R4_MAX_MSG_LEN];
        if n > 0 {
            core::ptr::copy_nonoverlapping(buf as *const u8, kbuf.as_mut_ptr(), n);
        }

        // If someone is blocked on recv for this endpoint, deliver directly
        let waiter = R4_ENDPOINTS[ep].waiter;
        if waiter >= 0 {
            let wt = waiter as usize;
            let wn = if n < R4_TASKS[wt].recv_cap as usize { n } else { R4_TASKS[wt].recv_cap as usize };
            if wn > 0 {
                core::ptr::copy_nonoverlapping(
                    kbuf.as_ptr(), R4_TASKS[wt].recv_buf as *mut u8, wn);
            }
            R4_TASKS[wt].saved_frame[14] = wn as u64; // return value for recv
            R4_TASKS[wt].state = R4State::Ready;
            R4_ENDPOINTS[ep].waiter = -1;
            return 0;
        }

        // No waiter — buffer the message
        R4_ENDPOINTS[ep].msg_data[..n].copy_from_slice(&kbuf[..n]);
        R4_ENDPOINTS[ep].msg_len = n;
        R4_ENDPOINTS[ep].has_msg = true;
        0
    }

    unsafe fn sys_ipc_recv_r4(frame: *mut u64, endpoint: u64, buf: u64, cap: u64) {
        let ep = endpoint as usize;
        if ep >= R4_MAX_ENDPOINTS || !R4_ENDPOINTS[ep].active {
            *frame.add(14) = 0xFFFF_FFFF_FFFF_FFFF;
            return;
        }
        if buf >= 0x0000_8000_0000_0000 {
            *frame.add(14) = 0xFFFF_FFFF_FFFF_FFFF;
            return;
        }

        // If message available, deliver immediately
        if R4_ENDPOINTS[ep].has_msg {
            let n = if R4_ENDPOINTS[ep].msg_len < cap as usize {
                R4_ENDPOINTS[ep].msg_len
            } else {
                cap as usize
            };
            if n > 0 {
                core::ptr::copy_nonoverlapping(
                    R4_ENDPOINTS[ep].msg_data.as_ptr(), buf as *mut u8, n);
            }
            R4_ENDPOINTS[ep].has_msg = false;
            *frame.add(14) = n as u64;
            return;
        }

        // No message — block current task and switch
        R4_TASKS[R4_CURRENT].recv_ep = endpoint;
        R4_TASKS[R4_CURRENT].recv_buf = buf;
        R4_TASKS[R4_CURRENT].recv_cap = cap;
        r4_save_frame(frame, R4_CURRENT);
        R4_TASKS[R4_CURRENT].state = R4State::Blocked;
        R4_ENDPOINTS[ep].waiter = R4_CURRENT as i32;

        match r4_find_ready(R4_CURRENT) {
            Some(tid) => { r4_switch_to(frame, tid); }
            None => {
                // Deadlock — no ready tasks
                serial_write(b"R4: deadlock\n");
                let kstack = &stack_top as *const u8 as u64;
                *frame.add(17) = r4_all_done as *const () as u64;
                *frame.add(18) = 0x08;
                *frame.add(19) = 0x02;
                *frame.add(20) = kstack;
                *frame.add(21) = 0x10;
            }
        }
    }
}

// --------------- R4: Service registry ----------------------------------------

cfg_r4! {
    const R4_MAX_SERVICES: usize = 4;

    struct ServiceEntry {
        active: bool,
        name: [u8; 16],
        name_len: usize,
        endpoint: u64,
    }

    impl ServiceEntry {
        const EMPTY: Self = Self {
            active: false, name: [0u8; 16], name_len: 0, endpoint: 0,
        };
    }

    static mut R4_SERVICES: [ServiceEntry; R4_MAX_SERVICES] =
        [ServiceEntry::EMPTY, ServiceEntry::EMPTY, ServiceEntry::EMPTY, ServiceEntry::EMPTY];

    unsafe fn sys_svc_register_r4(name_ptr: u64, name_len: u64, endpoint: u64) -> u64 {
        let n = name_len as usize;
        if n == 0 || n > 16 { return 0xFFFF_FFFF_FFFF_FFFF; }
        if name_ptr >= 0x0000_8000_0000_0000 { return 0xFFFF_FFFF_FFFF_FFFF; }
        let mut name = [0u8; 16];
        core::ptr::copy_nonoverlapping(name_ptr as *const u8, name.as_mut_ptr(), n);
        for i in 0..R4_MAX_SERVICES {
            if !R4_SERVICES[i].active {
                R4_SERVICES[i].active = true;
                R4_SERVICES[i].name = name;
                R4_SERVICES[i].name_len = n;
                R4_SERVICES[i].endpoint = endpoint;
                return 0;
            }
        }
        0xFFFF_FFFF_FFFF_FFFF
    }

    unsafe fn sys_svc_lookup_r4(name_ptr: u64, name_len: u64) -> u64 {
        let n = name_len as usize;
        if n == 0 || n > 16 { return 0xFFFF_FFFF_FFFF_FFFF; }
        if name_ptr >= 0x0000_8000_0000_0000 { return 0xFFFF_FFFF_FFFF_FFFF; }
        let mut name = [0u8; 16];
        core::ptr::copy_nonoverlapping(name_ptr as *const u8, name.as_mut_ptr(), n);
        for i in 0..R4_MAX_SERVICES {
            if R4_SERVICES[i].active && R4_SERVICES[i].name_len == n
                && R4_SERVICES[i].name[..n] == name[..n]
            {
                return R4_SERVICES[i].endpoint;
            }
        }
        0xFFFF_FFFF_FFFF_FFFF
    }
}

// --------------- R4: SHM syscalls --------------------------------------------

cfg_r4! {
    unsafe fn sys_shm_create_r4(size: u64) -> u64 {
        #[cfg(feature = "shm_test")]
        {
            if size == 0 || size > 4096 { return 0xFFFF_FFFF_FFFF_FFFF; }
            for i in 0..R4_MAX_SHM {
                if !R4_SHM_OBJECTS[i].active {
                    R4_SHM_OBJECTS[i].active = true;
                    R4_SHM_OBJECTS[i].size = 4096;
                    core::ptr::write_bytes(R4_SHM_PAGES[i].0.as_mut_ptr(), 0, 4096);
                    return i as u64;
                }
            }
            return 0xFFFF_FFFF_FFFF_FFFF;
        }
        #[cfg(not(feature = "shm_test"))]
        { let _ = size; 0xFFFF_FFFF_FFFF_FFFF }
    }

    unsafe fn sys_shm_map_r4(handle: u64, addr_hint: u64, _flags: u64) -> u64 {
        #[cfg(feature = "shm_test")]
        {
            let h = handle as usize;
            if h >= R4_MAX_SHM || !R4_SHM_OBJECTS[h].active { return 0xFFFF_FFFF_FFFF_FFFF; }
            if addr_hint & 0xFFF != 0 { return 0xFFFF_FFFF_FFFF_FFFF; }
            if addr_hint >= 0x0000_8000_0000_0000 { return 0xFFFF_FFFF_FFFF_FFFF; }

            // Get physical address of SHM backing page via kv2p
            let hhdm_resp_ptr = core::ptr::read_volatile(
                core::ptr::addr_of!(HHDM_REQUEST.response));
            let kaddr_resp_ptr = core::ptr::read_volatile(
                core::ptr::addr_of!(KADDR_REQUEST.response));
            let hhdm = (*hhdm_resp_ptr).offset;
            let kphys = (*kaddr_resp_ptr).physical_base;
            let kvirt = (*kaddr_resp_ptr).virtual_base;
            let shm_phys = R4_SHM_PAGES[h].0.as_ptr() as u64 - kvirt + kphys;

            // Walk page tables to find PT and install PTE
            let cr3: u64;
            core::arch::asm!("mov {}, cr3", out(reg) cr3, options(nomem, nostack));
            let pml4_phys = cr3 & 0x000F_FFFF_FFFF_F000;
            let pml4 = (pml4_phys + hhdm) as *const u64;
            let pml4e = *pml4.add(((addr_hint >> 39) & 0x1FF) as usize);
            if pml4e & 1 == 0 { return 0xFFFF_FFFF_FFFF_FFFF; }
            let pdpt = ((pml4e & 0x000F_FFFF_FFFF_F000) + hhdm) as *const u64;
            let pdpte = *pdpt.add(((addr_hint >> 30) & 0x1FF) as usize);
            if pdpte & 1 == 0 { return 0xFFFF_FFFF_FFFF_FFFF; }
            let pd = ((pdpte & 0x000F_FFFF_FFFF_F000) + hhdm) as *const u64;
            let pde = *pd.add(((addr_hint >> 21) & 0x1FF) as usize);
            if pde & 1 == 0 { return 0xFFFF_FFFF_FFFF_FFFF; }
            let pt = ((pde & 0x000F_FFFF_FFFF_F000) + hhdm) as *mut u64;
            let pt_idx = ((addr_hint >> 12) & 0x1FF) as usize;
            *pt.add(pt_idx) = shm_phys | 0x07; // Present | Writable | Use
            core::arch::asm!("invlpg [{}]", in(reg) addr_hint, options(nostack));
            return addr_hint;
        }
        #[cfg(not(feature = "shm_test"))]
        { let _ = (handle, addr_hint, _flags); 0xFFFF_FFFF_FFFF_FFFF }
    }
}

// --------------- R4: Page table setup for two tasks --------------------------

cfg_r4! {
    unsafe fn setup_r4_pages(blob0: &[u8], blob1: &[u8]) {
        let hhdm_resp_ptr = core::ptr::read_volatile(
            core::ptr::addr_of!(HHDM_REQUEST.response));
        let kaddr_resp_ptr = core::ptr::read_volatile(
            core::ptr::addr_of!(KADDR_REQUEST.response));
        let hhdm = (*hhdm_resp_ptr).offset;
        let kphys = (*kaddr_resp_ptr).physical_base;
        let kvirt = (*kaddr_resp_ptr).virtual_base;
        HHDM_OFFSET = hhdm;
        let kv2p = |va: u64| -> u64 { va - kvirt + kphys };

        // Clone current PML4
        let cr3: u64;
        core::arch::asm!("mov {}, cr3", out(reg) cr3, options(nomem, nostack));
        let old_pml4 = ((cr3 & 0x000F_FFFF_FFFF_F000) + hhdm) as *const u64;
        let new_pml4 = USER_PML4.0.as_mut_ptr() as *mut u64;
        for i in 0..512 { *new_pml4.add(i) = *old_pml4.add(i); }

        // PDPT entry 0 -> PD
        let pdpt = USER_PDPT.0.as_mut_ptr() as *mut u64;
        *pdpt = kv2p(USER_PD.0.as_ptr() as u64) | 0x07;

        // PD entry 2 -> PT_CODE (covers 0x400000-0x5FFFFF)
        // PD entry 3 -> PT_STACK (covers 0x600000-0x7FFFFF)
        let pd = USER_PD.0.as_mut_ptr() as *mut u64;
        *pd.add(2) = kv2p(USER_PT_CODE.0.as_ptr() as u64) | 0x07;
        *pd.add(3) = kv2p(USER_PT_STACK.0.as_ptr() as u64) | 0x07;

        // PT_CODE[0] = task 0 code page at 0x400000 (RX User)
        // PT_CODE[1] = task 1 code page at 0x401000 (RX User)
        let pt_code = USER_PT_CODE.0.as_mut_ptr() as *mut u64;
        *pt_code.add(0) = kv2p(USER_CODE_PAGE.0.as_ptr() as u64) | 0x05;
        *pt_code.add(1) = kv2p(USER_CODE_PAGE_2.0.as_ptr() as u64) | 0x05;

        // PT_STACK[511] = task 0 stack page at 0x7FF000 (RW User)
        // PT_STACK[510] = task 1 stack page at 0x7FE000 (RW User)
        let pt_stack = USER_PT_STACK.0.as_mut_ptr() as *mut u64;
        *pt_stack.add(511) = kv2p(USER_STACK_PAGE.0.as_ptr() as u64) | 0x07;
        *pt_stack.add(510) = kv2p(USER_STACK_PAGE_2.0.as_ptr() as u64) | 0x07;

        // PML4[0] -> our user PDPT
        *new_pml4 = kv2p(USER_PDPT.0.as_ptr() as u64) | 0x07;

        // Copy code blobs
        core::ptr::copy_nonoverlapping(
            blob0.as_ptr(), USER_CODE_PAGE.0.as_mut_ptr(), blob0.len());
        core::ptr::copy_nonoverlapping(
            blob1.as_ptr(), USER_CODE_PAGE_2.0.as_mut_ptr(), blob1.len());

        // Switch CR3
        let new_pml4_phys = kv2p(new_pml4 as u64);
        core::arch::asm!("mov cr3, {}", in(reg) new_pml4_phys, options(nostack));
    }
}

// --------------- R4: User program blobs (hand-assembled x86-64) --------------

// IPC ping-pong blobs
#[cfg(feature = "ipc_test")]
static IPC_PONG_BLOB: [u8; 103] = [
    // sys_svc_register("pong", 4, 0)
    0x48, 0x8d, 0x3d, 0x4f, 0x00, 0x00, 0x00, // lea rdi, [rip+0x4F] -> "pong" @86
    0xbe, 0x04, 0x00, 0x00, 0x00,               // mov esi, 4
    0x31, 0xd2,                                   // xor edx, edx
    0xb8, 0x0b, 0x00, 0x00, 0x00,               // mov eax, 11
    0xcd, 0x80,                                   // int 0x80
    // sys_ipc_recv(0, rsp-256, 256)
    0x31, 0xff,                                   // xor edi, edi
    0x48, 0x89, 0xe6,                             // mov rsi, rsp
    0x48, 0x81, 0xee, 0x00, 0x01, 0x00, 0x00,   // sub rsi, 0x100
    0xba, 0x00, 0x01, 0x00, 0x00,               // mov edx, 256
    0xb8, 0x09, 0x00, 0x00, 0x00,               // mov eax, 9
    0xcd, 0x80,                                   // int 0x80
    // sys_ipc_send(1, "pong", 4)
    0xbf, 0x01, 0x00, 0x00, 0x00,               // mov edi, 1
    0x48, 0x8d, 0x35, 0x21, 0x00, 0x00, 0x00,   // lea rsi, [rip+0x21] -> "pong" @90
    0xba, 0x04, 0x00, 0x00, 0x00,               // mov edx, 4
    0xb8, 0x08, 0x00, 0x00, 0x00,               // mov eax, 8
    0xcd, 0x80,                                   // int 0x80
    // sys_debug_write("PONG: ok\n", 9)
    0x48, 0x8d, 0x3d, 0x12, 0x00, 0x00, 0x00,   // lea rdi, [rip+0x12] -> msg @94
    0xbe, 0x09, 0x00, 0x00, 0x00,               // mov esi, 9
    0x31, 0xc0,                                   // xor eax, eax
    0xcd, 0x80,                                   // int 0x80
    0xf4,                                         // hlt
    // Data
    b'p', b'o', b'n', b'g',                     // @86: register name
    b'p', b'o', b'n', b'g',                     // @90: reply payload
    b'P', b'O', b'N', b'G', b':', b' ', b'o', b'k', b'\n', // @94: marke
];

#[cfg(feature = "ipc_test")]
static IPC_PING_BLOB: [u8; 102] = [
    // sys_svc_lookup("pong", 4)
    0x48, 0x8d, 0x3d, 0x4e, 0x00, 0x00, 0x00, // lea rdi, [rip+0x4E] -> "pong" @85
    0xbe, 0x04, 0x00, 0x00, 0x00,               // mov esi, 4
    0xb8, 0x0c, 0x00, 0x00, 0x00,               // mov eax, 12
    0xcd, 0x80,                                   // int 0x80
    // sys_ipc_send(rax, "ping", 4)
    0x48, 0x89, 0xc7,                             // mov rdi, rax
    0x48, 0x8d, 0x35, 0x3c, 0x00, 0x00, 0x00,   // lea rsi, [rip+0x3C] -> "ping" @89
    0xba, 0x04, 0x00, 0x00, 0x00,               // mov edx, 4
    0xb8, 0x08, 0x00, 0x00, 0x00,               // mov eax, 8
    0xcd, 0x80,                                   // int 0x80
    // sys_ipc_recv(1, rsp-256, 256)
    0xbf, 0x01, 0x00, 0x00, 0x00,               // mov edi, 1
    0x48, 0x89, 0xe6,                             // mov rsi, rsp
    0x48, 0x81, 0xee, 0x00, 0x01, 0x00, 0x00,   // sub rsi, 0x100
    0xba, 0x00, 0x01, 0x00, 0x00,               // mov edx, 256
    0xb8, 0x09, 0x00, 0x00, 0x00,               // mov eax, 9
    0xcd, 0x80,                                   // int 0x80
    // sys_debug_write("PING: ok\n", 9)
    0x48, 0x8d, 0x3d, 0x12, 0x00, 0x00, 0x00,   // lea rdi, [rip+0x12] -> msg @93
    0xbe, 0x09, 0x00, 0x00, 0x00,               // mov esi, 9
    0x31, 0xc0,                                   // xor eax, eax
    0xcd, 0x80,                                   // int 0x80
    0xf4,                                         // hlt
    // Data
    b'p', b'o', b'n', b'g',                     // @85: lookup name
    b'p', b'i', b'n', b'g',                     // @89: send payload
    b'P', b'I', b'N', b'G', b':', b' ', b'o', b'k', b'\n', // @93: marke
];

// SHM blobs
#[cfg(feature = "shm_test")]
static SHM_WRITER_BLOB: [u8; 69] = [
    // sys_shm_create(4096)
    0xbf, 0x00, 0x10, 0x00, 0x00,               // mov edi, 4096
    0xb8, 0x06, 0x00, 0x00, 0x00,               // mov eax, 6
    0xcd, 0x80,                                   // int 0x80
    // Save handle in rbx, then sys_shm_map(handle, 0x500000, 0)
    0x48, 0x89, 0xc3,                             // mov rbx, rax
    0x48, 0x89, 0xc7,                             // mov rdi, rax
    0xbe, 0x00, 0x00, 0x50, 0x00,               // mov esi, 0x500000
    0x31, 0xd2,                                   // xor edx, edx
    0xb8, 0x07, 0x00, 0x00, 0x00,               // mov eax, 7
    0xcd, 0x80,                                   // int 0x80
    // Fill 256 bytes: pattern 0,1,2,...,255
    0x48, 0x89, 0xc7,                             // mov rdi, rax  (base=0x500000)
    0x31, 0xc9,                                   // xor ecx, ecx
    // .loop @37:
    0x88, 0x0c, 0x0f,                             // mov [rdi+rcx], cl
    0xff, 0xc1,                                   // inc ecx
    0x81, 0xf9, 0x00, 0x01, 0x00, 0x00,         // cmp ecx, 256
    0x75, 0xf3,                                   // jne .loop (-13)
    // Send handle byte via IPC endpoint 0
    0x53,                                         // push rbx
    0x31, 0xff,                                   // xor edi, edi
    0x48, 0x89, 0xe6,                             // mov rsi, rsp
    0xba, 0x01, 0x00, 0x00, 0x00,               // mov edx, 1
    0xb8, 0x08, 0x00, 0x00, 0x00,               // mov eax, 8
    0xcd, 0x80,                                   // int 0x80
    0xf4,                                         // hlt
];

#[cfg(feature = "shm_test")]
static SHM_READER_BLOB: [u8; 105] = [
    // sys_ipc_recv(0, stack_buf, 8)
    0x48, 0x83, 0xec, 0x10,                     // sub rsp, 16
    0x31, 0xff,                                   // xor edi, edi
    0x48, 0x89, 0xe6,                             // mov rsi, rsp
    0xba, 0x08, 0x00, 0x00, 0x00,               // mov edx, 8
    0xb8, 0x09, 0x00, 0x00, 0x00,               // mov eax, 9
    0xcd, 0x80,                                   // int 0x80
    // Load handle from buffe
    0x0f, 0xb6, 0x3c, 0x24,                     // movzx edi, byte [rsp]
    // sys_shm_map(handle, 0x500000, 0)
    0xbe, 0x00, 0x00, 0x50, 0x00,               // mov esi, 0x500000
    0x31, 0xd2,                                   // xor edx, edx
    0xb8, 0x07, 0x00, 0x00, 0x00,               // mov eax, 7
    0xcd, 0x80,                                   // int 0x80
    // Compute checksum: sum 256 bytes
    0x48, 0x89, 0xc6,                             // mov rsi, rax
    0x31, 0xc9,                                   // xor ecx, ecx
    0x31, 0xd2,                                   // xor edx, edx
    // .loop @46:
    0x0f, 0xb6, 0x04, 0x0e,                     // movzx eax, byte [rsi+rcx]
    0x01, 0xc2,                                   // add edx, eax
    0xff, 0xc1,                                   // inc ecx
    0x81, 0xf9, 0x00, 0x01, 0x00, 0x00,         // cmp ecx, 256
    0x75, 0xf0,                                   // jne .loop (-16)
    // Check sum == 32640 (0+1+...+255)
    0x81, 0xfa, 0x80, 0x7f, 0x00, 0x00,         // cmp edx, 32640
    0x75, 0x11,                                   // jne .bad (+17)
    // sys_debug_write("SHM: checksum ok\n", 17)
    0x48, 0x8d, 0x3d, 0x0b, 0x00, 0x00, 0x00,   // lea rdi, [rip+0x0B] -> msg @88
    0xbe, 0x11, 0x00, 0x00, 0x00,               // mov esi, 17
    0x31, 0xc0,                                   // xor eax, eax
    0xcd, 0x80,                                   // int 0x80
    0xf4,                                         // hlt
    // .bad:
    0xf4,                                         // hlt
    // Data @88:
    b'S', b'H', b'M', b':', b' ', b'c', b'h', b'e',
    b'c', b'k', b's', b'u', b'm', b' ', b'o', b'k', b'\n',
];

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

// --------------- PIC (8259) ---------------

#[cfg(feature = "sched_test")]
const PIC1_CMD: u16 = 0x20;
#[cfg(feature = "sched_test")]
const PIC1_DATA: u16 = 0x21;
#[cfg(feature = "sched_test")]
const PIC2_CMD: u16 = 0xA0;
#[cfg(feature = "sched_test")]
const PIC2_DATA: u16 = 0xA1;

#[cfg(feature = "sched_test")]
unsafe fn pic_init() {
    outb(PIC1_CMD, 0x11);
    outb(PIC2_CMD, 0x11);
    outb(PIC1_DATA, 32);
    outb(PIC2_DATA, 40);
    outb(PIC1_DATA, 0x04);
    outb(PIC2_DATA, 0x02);
    outb(PIC1_DATA, 0x01);
    outb(PIC2_DATA, 0x01);
    outb(PIC1_DATA, 0xFE);
    outb(PIC2_DATA, 0xFF);
}

#[cfg(feature = "sched_test")]
unsafe fn pic_send_eoi(irq: u8) {
    if irq >= 8 { outb(PIC2_CMD, 0x20); }
    outb(PIC1_CMD, 0x20);
}

// --------------- PIT (8254) ---------------

#[cfg(feature = "sched_test")]
unsafe fn pit_init(freq: u32) {
    let divisor = 1_193_182u32 / freq;
    outb(0x43, 0x34);
    outb(0x40, (divisor & 0xFF) as u8);
    outb(0x40, ((divisor >> 8) & 0xFF) as u8);
}

// --------------- M2 Scheduler ---------------

#[cfg(feature = "sched_test")]
static mut TICK_COUNT: u64 = 0;

#[cfg(feature = "sched_test")]
const MAX_THREADS: usize = 4;
#[cfg(feature = "sched_test")]
const THREAD_STACK_SIZE: usize = 16384;

#[cfg(feature = "sched_test")]
#[derive(Clone, Copy, PartialEq)]
#[repr(u8)]
enum ThreadState { Dead = 0, Ready = 1, Running = 2 }

#[cfg(feature = "sched_test")]
#[derive(Clone, Copy)]
#[repr(C)]
struct Thread { rsp: u64, state: ThreadState }

#[cfg(feature = "sched_test")]
impl Thread {
    const EMPTY: Self = Self { rsp: 0, state: ThreadState::Dead };
}

#[cfg(feature = "sched_test")]
static mut THREADS: [Thread; MAX_THREADS] = [Thread::EMPTY; MAX_THREADS];
#[cfg(feature = "sched_test")]
static mut THREAD_STACKS: [[u8; THREAD_STACK_SIZE]; MAX_THREADS] =
    [[0u8; THREAD_STACK_SIZE]; MAX_THREADS];
#[cfg(feature = "sched_test")]
static mut CURRENT_THREAD: usize = 0;
#[cfg(feature = "sched_test")]
static mut NUM_THREADS: usize = 0;

#[cfg(feature = "sched_test")]
extern "C" {
    fn context_switch(old_rsp: *mut u64, new_rsp: u64);
    fn thread_entry_trampoline();
}

#[cfg(feature = "sched_test")]
unsafe fn sched_init() {
    THREADS[0].state = ThreadState::Running;
    THREADS[0].rsp = 0;
    CURRENT_THREAD = 0;
    NUM_THREADS = 1;
}

#[cfg(feature = "sched_test")]
unsafe fn thread_create(func: extern "C" fn()) {
    let tid = NUM_THREADS;
    NUM_THREADS += 1;
    let sp_top = THREAD_STACKS[tid].as_mut_ptr().add(THREAD_STACK_SIZE) as u64;
    let mut sp = sp_top;
    sp -= 8; *(sp as *mut u64) = thread_exit as *const () as u64;
    sp -= 8; *(sp as *mut u64) = func as *const () as u64;
    sp -= 8; *(sp as *mut u64) = thread_entry_trampoline as *const () as u64;
    sp -= 8; *(sp as *mut u64) = 0; // r15
    sp -= 8; *(sp as *mut u64) = 0; // r14
    sp -= 8; *(sp as *mut u64) = 0; // r13
    sp -= 8; *(sp as *mut u64) = 0; // r12
    sp -= 8; *(sp as *mut u64) = 0; // rbx
    sp -= 8; *(sp as *mut u64) = 0; // rbp
    THREADS[tid].rsp = sp;
    THREADS[tid].state = ThreadState::Ready;
}

#[cfg(feature = "sched_test")]
unsafe fn schedule() {
    let cur = CURRENT_THREAD;
    let mut next = (cur + 1) % NUM_THREADS;
    let start = next;
    loop {
        if THREADS[next].state == ThreadState::Ready { break; }
        next = (next + 1) % NUM_THREADS;
        if next == start { return; }
    }
    if next == cur { return; }
    if THREADS[cur].state == ThreadState::Running { THREADS[cur].state = ThreadState::Ready; }
    THREADS[next].state = ThreadState::Running;
    CURRENT_THREAD = next;
    let old_rsp = &mut THREADS[cur].rsp as *mut u64;
    let new_rsp = THREADS[next].rsp;
    context_switch(old_rsp, new_rsp);
}

#[cfg(feature = "sched_test")]
extern "C" fn thread_exit() {
    unsafe {
        THREADS[CURRENT_THREAD].state = ThreadState::Dead;
        schedule();
    }
    loop { unsafe { core::arch::asm!("cli; hlt", options(nomem, nostack)); } }
}

#[cfg(feature = "sched_test")]
extern "C" fn thread_a() { loop { serial_write(b"A\n"); } }

#[cfg(feature = "sched_test")]
extern "C" fn thread_b() { loop { serial_write(b"B\n"); } }

// --------------- Kernel entry ---------------

#[no_mangle]
pub extern "C" fn kmain() -> ! {
    serial_init();
    serial_write(b"RUGO: boot ok\n");
    check_paging();

    unsafe {
        gdt_init();
        idt_init();
    }

    #[cfg(feature = "pf_test")]
    unsafe {
        let p = 0x0000_0040_0000_0000u64 as *const u8;
        core::ptr::read_volatile(p);
    }

    #[cfg(feature = "idt_smoke_test")]
    unsafe {
        core::arch::asm!("int3", options(nomem, nostack));
    }

    #[cfg(feature = "sched_test")]
    {
        unsafe {
            pic_init();
            pit_init(100);
            sched_init();
            thread_create(thread_a);
            thread_create(thread_b);
            core::arch::asm!("sti", options(nomem, nostack));
        }
        loop { unsafe { core::arch::asm!("hlt", options(nomem, nostack)); } }
    }

    // M3: user_hello_test
    #[cfg(feature = "user_hello_test")]
    unsafe {
        let kstack = &stack_top as *const u8 as u64;
        tss_init(kstack);
        setup_user_pages(&USER_HELLO_BLOB);
        enter_ring3_at(USER_CODE_VA, USER_STACK_TOP);
    }

    // M3: syscall_test
    #[cfg(feature = "syscall_test")]
    unsafe {
        let kstack = &stack_top as *const u8 as u64;
        tss_init(kstack);
        setup_user_pages(&USER_SYSCALL_BLOB);
        enter_ring3_at(USER_CODE_VA, USER_STACK_TOP);
    }

    // M3: user_fault_test
    #[cfg(feature = "user_fault_test")]
    unsafe {
        let kstack = &stack_top as *const u8 as u64;
        tss_init(kstack);
        setup_user_pages(&USER_FAULT_BLOB);
        enter_ring3_at(USER_CODE_VA, USER_STACK_TOP);
    }

    // R4: ipc_test — ping-pong between two user tasks
    #[cfg(feature = "ipc_test")]
    unsafe {
        let kstack = &stack_top as *const u8 as u64;
        tss_init(kstack);
        setup_r4_pages(&IPC_PONG_BLOB, &IPC_PING_BLOB);

        // Pre-create endpoints 0 and 1
        R4_ENDPOINTS[0].active = true;
        R4_ENDPOINTS[1].active = true;

        // Init tasks: task 0 = pong, task 1 = ping
        R4_NUM_TASKS = 2;
        r4_init_task(0, USER_CODE_VA, USER_STACK_TOP);
        r4_init_task(1, USER_CODE2_VA, USER_STACK2_TOP);
        R4_TASKS[0].state = R4State::Running;
        R4_CURRENT = 0;

        // Enter ring 3 with task 0 (pong)
        enter_ring3_at(USER_CODE_VA, USER_STACK_TOP);
    }

    // R4: shm_test — shared memory bulk transfe
    #[cfg(feature = "shm_test")]
    unsafe {
        let kstack = &stack_top as *const u8 as u64;
        tss_init(kstack);
        setup_r4_pages(&SHM_WRITER_BLOB, &SHM_READER_BLOB);

        // Pre-create endpoint 0
        R4_ENDPOINTS[0].active = true;

        // Init tasks: task 0 = writer, task 1 = reade
        R4_NUM_TASKS = 2;
        r4_init_task(0, USER_CODE_VA, USER_STACK_TOP);
        r4_init_task(1, USER_CODE2_VA, USER_STACK2_TOP);
        R4_TASKS[0].state = R4State::Running;
        R4_CURRENT = 0;

        enter_ring3_at(USER_CODE_VA, USER_STACK_TOP);
    }

    // Normal boot path (M0/M1)
    #[cfg(not(any(
        feature = "sched_test",
        feature = "user_hello_test",
        feature = "syscall_test",
        feature = "user_fault_test",
        feature = "ipc_test",
        feature = "shm_test",
    )))]
    {
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
