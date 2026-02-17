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

// --------------- Limine HHDM request (needed for M3 page table setup) --------
//
// Limine writes the response pointer at boot before our code runs.
// The statics must be mutable (or use UnsafeCell) so the compiler doesn't
// fold reads to the initial null value.

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

// --------------- Limine kernel address request (M3) --------------------------

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

// 7 entries: null, kcode, kdata, udata, ucode, tss_lo, tss_hi
static mut GDT: [u64; 7] = [
    0x0000_0000_0000_0000, // 0x00 Null
    0x00AF_9A00_0000_FFFF, // 0x08 Kernel code 64-bit (DPL=0)
    0x00CF_9200_0000_FFFF, // 0x10 Kernel data (DPL=0)
    0x00CF_F200_0000_FFFF, // 0x18 User data (DPL=3)
    0x00AF_FA00_0000_FFFF, // 0x20 User code 64-bit (DPL=3)
    0,                      // 0x28 TSS descriptor low  (filled at runtime)
    0,                      // 0x30 TSS descriptor high (filled at runtime)
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

// --------------- TSS (M3: needed for ring 3 -> ring 0 transitions) -----------

cfg_m3! {
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

        // TSS descriptor low (GDT[5], selector 0x28)
        GDT[5] = (103u64)                                   // limit = sizeof(Tss) - 1
                | ((tss_addr & 0xFFFF) << 16)                // base[15:0]
                | (((tss_addr >> 16) & 0xFF) << 32)          // base[23:16]
                | (0x89u64 << 40)                            // access: present, DPL=0, type=9
                | (((tss_addr >> 24) & 0xFF) << 56);         // base[31:24]

        // TSS descriptor high (GDT[6])
        GDT[6] = tss_addr >> 32;

        // Reload GDT with TSS entries now filled
        let limit = (core::mem::size_of_val(&GDT) - 1) as u16;
        let base = GDT.as_ptr() as u64;
        let gdt_ptr = DtPtr { limit, base };
        core::arch::asm!("lgdt [{}]", in(reg) &gdt_ptr);

        // Load Task Registe
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
        fn isr_stub_32();
        fn isr_stub_128();
    }

    idt_set_gate(0,  isr_stub_0  as *const () as u64);
    idt_set_gate(3,  isr_stub_3  as *const () as u64);
    idt_set_gate(8,  isr_stub_8  as *const () as u64);
    idt_set_gate(13, isr_stub_13 as *const () as u64);
    idt_set_gate(14, isr_stub_14 as *const () as u64);
    idt_set_gate(32, isr_stub_32 as *const () as u64);

    // int 0x80 syscall gate: DPL=3 so ring 3 can invoke it
    let handler = isr_stub_128 as *const () as u64;
    IDT[128] = IdtEntry {
        offset_low: handler as u16,
        selector: 0x08,
        ist: 0,
        type_attr: 0xEE, // Present, DPL=3, 64-bit interrupt gate
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
// Frame layout from RSP (after isr_common pushes 15 GPRs):
//   [0]  r15   [1] r14   [2] r13   [3] r12   [4] r11   [5] r10
//   [6]  r9    [7] r8    [8] rbp   [9] rdi   [10] rsi  [11] rdx
//   [12] rcx   [13] rbx  [14] rax
//   [15] int_num   [16] error_code
//   [17] rip   [18] cs   [19] rflags   [20] rsp   [21] ss

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
                // Check if fault came from ring 3
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
                // Check if fault came from ring 3
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
                // Timer IRQ (IRQ0)
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
            // int 0x80 syscall handle
            128 => {
                syscall_dispatch(frame);
            }
            _ => {}
        }
    }
}

// --------------- User fault containment --------------------------------------
//
// When a GPF or PF occurs in ring 3, kill the user task and redirect
// execution back to kernel code via frame modification.

extern "C" fn user_fault_return() -> ! {
    serial_write(b"RUGO: halt ok\n");
    qemu_exit(0x31);
    loop {
        unsafe { core::arch::asm!("cli; hlt", options(nomem, nostack)); }
    }
}

// Kernel stack top (defined in entry.asm)
extern "C" { static stack_top: u8; }

unsafe fn handle_user_fault(frame: *mut u64) {
    serial_write(b"USER: killed\n");

    // Modify interrupt frame so iretq returns to kernel continuation
    let kstack = &stack_top as *const u8 as u64;
    *frame.add(17) = user_fault_return as *const () as u64; // RIP
    *frame.add(18) = 0x08;                                  // CS = kernel code
    *frame.add(19) = 0x02;                                  // RFLAGS (IF=0, bit1 set)
    *frame.add(20) = kstack;                                // RSP = kernel stack
    *frame.add(21) = 0x10;                                  // SS = kernel data
}

// --------------- Syscall dispatch (int 0x80) ---------------------------------
//
// Register convention (see docs/abi/syscall_v0.md):
//   rax = syscall number (frame[14])
//   rdi = arg1 (frame[9]),  rsi = arg2 (frame[10])
//   rdx = arg3 (frame[11]), r10 = arg4 (frame[5])
//   Return value written to rax (frame[14])

cfg_m3! {
    static mut MONOTONIC_TICK: u64 = 1;
    static mut HHDM_OFFSET: u64 = 0;
}

unsafe fn syscall_dispatch(frame: *mut u64) {
    let nr  = *frame.add(14); // rax
    let arg1 = *frame.add(9);  // rdi
    let arg2 = *frame.add(10); // rsi

    let ret: u64 = match nr {
        // sys_debug_write(buf, len)
        0 => sys_debug_write(arg1, arg2),
        // sys_time_now()
        10 => sys_time_now(),
        // Stubs: return -1
        1..=9 => 0xFFFF_FFFF_FFFF_FFFF,
        _ => 0xFFFF_FFFF_FFFF_FFFF,
    };

    // Write return value to rax in the frame
    *frame.add(14) = ret;
}

unsafe fn sys_debug_write(buf: u64, len: u64) -> u64 {
    // Validate user pointe
    let max_len = 256u64;
    let actual_len = if len > max_len { max_len } else { len };

    if actual_len == 0 {
        return 0;
    }

    // Check pointer is in user range
    if buf >= 0x0000_8000_0000_0000 {
        return 0xFFFF_FFFF_FFFF_FFFF;
    }
    if buf.checked_add(actual_len).is_none() || buf + actual_len > 0x0000_8000_0000_0000 {
        return 0xFFFF_FFFF_FFFF_FFFF;
    }

    // Walk page tables to verify user pages are present and accessible
    #[cfg(any(feature = "user_hello_test", feature = "syscall_test", feature = "user_fault_test"))]
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

    // Copy to kernel buffer and print
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

#[cfg(any(feature = "user_hello_test", feature = "syscall_test", feature = "user_fault_test"))]
unsafe fn check_page_user_accessible(va: u64, hhdm: u64) -> bool {
    let cr3: u64;
    core::arch::asm!("mov {}, cr3", out(reg) cr3, options(nomem, nostack));
    let pml4_phys = cr3 & 0x000F_FFFF_FFFF_F000;

    // PML4
    let pml4 = (pml4_phys + hhdm) as *const u64;
    let pml4e = *pml4.add(((va >> 39) & 0x1FF) as usize);
    if pml4e & 1 == 0 || pml4e & 4 == 0 { return false; }

    // PDPT
    let pdpt = ((pml4e & 0x000F_FFFF_FFFF_F000) + hhdm) as *const u64;
    let pdpte = *pdpt.add(((va >> 30) & 0x1FF) as usize);
    if pdpte & 1 == 0 || pdpte & 4 == 0 { return false; }
    if pdpte & 0x80 != 0 { return true; } // 1GB huge page with user bit

    // PD
    let pd = ((pdpte & 0x000F_FFFF_FFFF_F000) + hhdm) as *const u64;
    let pde = *pd.add(((va >> 21) & 0x1FF) as usize);
    if pde & 1 == 0 || pde & 4 == 0 { return false; }
    if pde & 0x80 != 0 { return true; } // 2MB huge page with user bit

    // PT
    let pt = ((pde & 0x000F_FFFF_FFFF_F000) + hhdm) as *const u64;
    let pte = *pt.add(((va >> 12) & 0x1FF) as usize);
    pte & 1 != 0 && pte & 4 != 0
}

// --------------- M3: User page table setup -----------------------------------

cfg_m3! {
    const USER_CODE_VA: u64  = 0x40_0000;
    const USER_STACK_TOP: u64 = 0x80_0000;
    const USER_STACK_VA: u64  = 0x7F_F000; // page just below stack top

    #[repr(C, align(4096))]
    struct Page([u8; 4096]);

    static mut USER_PML4:      Page = Page([0; 4096]);
    static mut USER_PDPT:      Page = Page([0; 4096]);
    static mut USER_PD:        Page = Page([0; 4096]);
    static mut USER_PT_CODE:   Page = Page([0; 4096]);
    static mut USER_PT_STACK:  Page = Page([0; 4096]);
    static mut USER_CODE_PAGE: Page = Page([0; 4096]);
    static mut USER_STACK_PAGE: Page = Page([0; 4096]);

    unsafe fn setup_user_pages(user_code: &[u8]) {
        // Read Limine responses
        // Use volatile reads: Limine wrote these pointers before our code ran,
        // and the compiler must not fold them to the initial null.
        let hhdm_resp_ptr = core::ptr::read_volatile(
            core::ptr::addr_of!(HHDM_REQUEST.response));
        let kaddr_resp_ptr = core::ptr::read_volatile(
            core::ptr::addr_of!(KADDR_REQUEST.response));
        let hhdm = (*hhdm_resp_ptr).offset;
        let kphys = (*kaddr_resp_ptr).physical_base;
        let kvirt = (*kaddr_resp_ptr).virtual_base;

        HHDM_OFFSET = hhdm;

        // Kernel VA -> physical address
        let kv2p = |va: u64| -> u64 { va - kvirt + kphys };

        // Read current PML4 via HHDM
        let cr3: u64;
        core::arch::asm!("mov {}, cr3", out(reg) cr3, options(nomem, nostack));
        let old_pml4_phys = cr3 & 0x000F_FFFF_FFFF_F000;
        let old_pml4 = (old_pml4_phys + hhdm) as *const u64;

        // New PML4: copy all entries from current (preserves kernel mappings)
        let new_pml4 = USER_PML4.0.as_mut_ptr() as *mut u64;
        for i in 0..512 {
            *new_pml4.add(i) = *old_pml4.add(i);
        }

        // User PDPT: entry 0 -> PD
        let pdpt = USER_PDPT.0.as_mut_ptr() as *mut u64;
        let pd_phys = kv2p(USER_PD.0.as_ptr() as u64);
        *pdpt = pd_phys | 0x07; // Present | Writable | Use

        // User PD: entry 2 -> PT for code, entry 3 -> PT for stack
        let pd = USER_PD.0.as_mut_ptr() as *mut u64;
        let pt_code_phys = kv2p(USER_PT_CODE.0.as_ptr() as u64);
        let pt_stack_phys = kv2p(USER_PT_STACK.0.as_ptr() as u64);
        // PD index for 0x400000: (0x400000 >> 21) & 0x1FF = 2
        *pd.add(2) = pt_code_phys | 0x07;
        // PD index for 0x7FF000: (0x7FF000 >> 21) & 0x1FF = 3
        *pd.add(3) = pt_stack_phys | 0x07;

        // Code PT: map one 4K page (RX, User)
        let pt_code = USER_PT_CODE.0.as_mut_ptr() as *mut u64;
        let code_page_phys = kv2p(USER_CODE_PAGE.0.as_ptr() as u64);
        // PT index for 0x400000: (0x400000 >> 12) & 0x1FF = 0
        *pt_code = code_page_phys | 0x05; // Present | User (read-execute)

        // Stack PT: map one 4K page (RW, User)
        let pt_stack = USER_PT_STACK.0.as_mut_ptr() as *mut u64;
        let stack_page_phys = kv2p(USER_STACK_PAGE.0.as_ptr() as u64);
        // PT index for 0x7FF000: (0x7FF000 >> 12) & 0x1FF = 511
        *pt_stack.add(511) = stack_page_phys | 0x07; // Present | Writable | Use

        // Override PML4 entry 0 with our user PDPT
        let pdpt_phys = kv2p(USER_PDPT.0.as_ptr() as u64);
        *new_pml4 = pdpt_phys | 0x07; // Present | Writable | Use

        // Copy user code blob to the code page
        core::ptr::copy_nonoverlapping(
            user_code.as_ptr(),
            USER_CODE_PAGE.0.as_mut_ptr(),
            user_code.len(),
        );

        // Switch CR3 to new page tables
        let new_pml4_phys = kv2p(new_pml4 as u64);
        core::arch::asm!("mov cr3, {}", in(reg) new_pml4_phys, options(nostack));
    }

    unsafe fn enter_ring3() -> ! {
        core::arch::asm!(
            "push 0x1B",       // SS = user data selector (0x18 | RPL=3)
            "push {stack}",    // RSP = user stack top
            "push 0x002",      // RFLAGS: IF=0, bit1 set (interrupts off in M3)
            "push 0x23",       // CS = user code selector (0x20 | RPL=3)
            "push {code}",     // RIP = user code entry
            "iretq",
            stack = in(reg) USER_STACK_TOP,
            code = in(reg) USER_CODE_VA,
            options(noreturn),
        );
    }
}

// --------------- M3: User program blobs (x86-64 machine code) ----------------
//
// Each blob is tiny freestanding assembly, assembled by hand.
// Programs run at VA 0x400000, stack at 0x800000 (growing down).

cfg_m3! {
    // user_hello: writes "USER: hello\n" via sys_debug_write, then halts (GPF in ring3)
    //
    //   lea rdi, [rip+0x0d]   ; 48 8d 3d 0d 00 00 00   -> buf = &msg
    //   mov rsi, 12           ; 48 c7 c6 0c 00 00 00   -> len = 12
    //   xor eax, eax          ; 31 c0                   -> syscall 0
    //   int 0x80              ; cd 80
    //   hlt                   ; f4   (GPF in ring3 -> kernel exits)
    //   msg: "USER: hello\n"
    static USER_HELLO_BLOB: [u8; 32] = [
        0x48, 0x8d, 0x3d, 0x0d, 0x00, 0x00, 0x00, // lea rdi, [rip+13]
        0x48, 0xc7, 0xc6, 0x0c, 0x00, 0x00, 0x00, // mov rsi, 12
        0x31, 0xc0,                                 // xor eax, eax
        0xcd, 0x80,                                 // int 0x80
        0xf4,                                       // hlt
        0x00,                                       // padding
        b'U', b'S', b'E', b'R', b':', b' ',
        b'h', b'e', b'l', b'l', b'o', b'\n',
    ];

    // user_syscall: calls sys_time_now then sys_debug_write("SYSCALL: ok\n"), then halts
    //
    // offset 0:  mov eax, 10           ; b8 0a 00 00 00   (5 bytes)
    // offset 5:  int 0x80              ; cd 80             (2 bytes)
    // offset 7:  lea rdi, [rip+0x0f]   ; 48 8d 3d 0f ..   (7 bytes, RIP@14, msg@29)
    // offset 14: mov rsi, 12           ; 48 c7 c6 0c ..   (7 bytes)
    // offset 21: xor eax, eax          ; 31 c0             (2 bytes)
    // offset 23: int 0x80              ; cd 80             (2 bytes)
    // offset 25: hlt                   ; f4                (1 byte)
    // offset 26: padding               ; 00 00 00          (3 bytes)
    // offset 29: msg "SYSCALL: ok\n"                       (12 bytes)
    static USER_SYSCALL_BLOB: [u8; 41] = [
        0xb8, 0x0a, 0x00, 0x00, 0x00,               // mov eax, 10
        0xcd, 0x80,                                   // int 0x80
        0x48, 0x8d, 0x3d, 0x0f, 0x00, 0x00, 0x00,   // lea rdi, [rip+15]
        0x48, 0xc7, 0xc6, 0x0c, 0x00, 0x00, 0x00,   // mov rsi, 12
        0x31, 0xc0,                                   // xor eax, eax
        0xcd, 0x80,                                   // int 0x80
        0xf4,                                         // hlt
        0x00, 0x00, 0x00,                             // padding
        b'S', b'Y', b'S', b'C', b'A', b'L', b'L',
        b':', b' ', b'o', b'k', b'\n',
    ];

    // user_fault: writes to unmapped address -> PF in ring3
    //
    //   mov eax, 0xDEAD0000   ; b8 00 00 ad de
    //   mov byte [rax], 0x42  ; c6 00 42
    //   hlt                   ; f4
    static USER_FAULT_BLOB: [u8; 9] = [
        0xb8, 0x00, 0x00, 0xad, 0xde,   // mov eax, 0xDEAD0000
        0xc6, 0x00, 0x42,               // mov byte [rax], 0x42
        0xf4,                            // hlt
    ];
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
    // ICW1: init + ICW4
    outb(PIC1_CMD, 0x11);
    outb(PIC2_CMD, 0x11);
    // ICW2: vector offsets (IRQ 0-7 -> 32-39, IRQ 8-15 -> 40-47)
    outb(PIC1_DATA, 32);
    outb(PIC2_DATA, 40);
    // ICW3: cascade wiring
    outb(PIC1_DATA, 0x04);
    outb(PIC2_DATA, 0x02);
    // ICW4: 8086 mode
    outb(PIC1_DATA, 0x01);
    outb(PIC2_DATA, 0x01);
    // Mask all except IRQ0 (timer)
    outb(PIC1_DATA, 0xFE);
    outb(PIC2_DATA, 0xFF);
}

#[cfg(feature = "sched_test")]
unsafe fn pic_send_eoi(irq: u8) {
    if irq >= 8 {
        outb(PIC2_CMD, 0x20);
    }
    outb(PIC1_CMD, 0x20);
}

// --------------- PIT (8254) ---------------

#[cfg(feature = "sched_test")]
unsafe fn pit_init(freq: u32) {
    let divisor = 1_193_182u32 / freq;
    outb(0x43, 0x34); // Channel 0, lo/hi byte, mode 2 (rate generator)
    outb(0x40, (divisor & 0xFF) as u8);
    outb(0x40, ((divisor >> 8) & 0xFF) as u8);
}

// --------------- Scheduler ---------------

#[cfg(feature = "sched_test")]
static mut TICK_COUNT: u64 = 0;

#[cfg(feature = "sched_test")]
const MAX_THREADS: usize = 4;
#[cfg(feature = "sched_test")]
const THREAD_STACK_SIZE: usize = 16384;

#[cfg(feature = "sched_test")]
#[derive(Clone, Copy, PartialEq)]
#[repr(u8)]
enum ThreadState {
    Dead = 0,
    Ready = 1,
    Running = 2,
}

#[cfg(feature = "sched_test")]
#[derive(Clone, Copy)]
#[repr(C)]
struct Thread {
    rsp: u64,
    state: ThreadState,
}

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

    // Build initial stack frame for context_switch
    sp -= 8; *(sp as *mut u64) = thread_exit as *const () as u64;              // return from func
    sp -= 8; *(sp as *mut u64) = func as *const () as u64;                     // return from trampoline
    sp -= 8; *(sp as *mut u64) = thread_entry_trampoline as *const () as u64;  // return from context_switch
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

    // Find next ready thread (round-robin)
    let start = next;
    loop {
        if THREADS[next].state == ThreadState::Ready {
            break;
        }
        next = (next + 1) % NUM_THREADS;
        if next == start {
            return; // No other ready thread
        }
    }

    if next == cur {
        return;
    }

    if THREADS[cur].state == ThreadState::Running {
        THREADS[cur].state = ThreadState::Ready;
    }
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
    loop {
        unsafe { core::arch::asm!("cli; hlt", options(nomem, nostack)); }
    }
}

// --------------- Thread functions ---------------

#[cfg(feature = "sched_test")]
extern "C" fn thread_a() {
    loop {
        serial_write(b"A\n");
    }
}

#[cfg(feature = "sched_test")]
extern "C" fn thread_b() {
    loop {
        serial_write(b"B\n");
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

    // Feature-gated test paths (each triggers an exception -> handler exits QEMU)
    #[cfg(feature = "pf_test")]
    unsafe {
        let p = 0x0000_0040_0000_0000u64 as *const u8;
        core::ptr::read_volatile(p);
    }

    #[cfg(feature = "idt_smoke_test")]
    unsafe {
        core::arch::asm!("int3", options(nomem, nostack));
    }

    // M2: scheduler demo (sched_test feature)
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
        loop {
            unsafe { core::arch::asm!("hlt", options(nomem, nostack)); }
        }
    }

    // M3: user_hello_test — enter ring 3, print "USER: hello" via syscall
    #[cfg(feature = "user_hello_test")]
    unsafe {
        let kstack = &stack_top as *const u8 as u64;
        tss_init(kstack);
        setup_user_pages(&USER_HELLO_BLOB);
        enter_ring3();
    }

    // M3: syscall_test — enter ring 3, invoke time_now + debug_write
    #[cfg(feature = "syscall_test")]
    unsafe {
        let kstack = &stack_top as *const u8 as u64;
        tss_init(kstack);
        setup_user_pages(&USER_SYSCALL_BLOB);
        enter_ring3();
    }

    // M3: user_fault_test — enter ring 3, write to bad address -> kernel kills + continues
    #[cfg(feature = "user_fault_test")]
    unsafe {
        let kstack = &stack_top as *const u8 as u64;
        tss_init(kstack);
        setup_user_pages(&USER_FAULT_BLOB);
        enter_ring3();
    }

    // Normal boot path (M0/M1)
    #[cfg(not(any(
        feature = "sched_test",
        feature = "user_hello_test",
        feature = "syscall_test",
        feature = "user_fault_test",
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
