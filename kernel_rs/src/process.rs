// Compat app launch/finish flow for the real external-app lane.

use crate::*;

#[cfg(feature = "compat_real_test")]
pub(crate) unsafe fn compat_real_enter_current_app() -> ! {
    if COMPAT_REAL_APP_INDEX >= COMPAT_REAL_APPS.len() {
        serial_write(b"X1: suite ok\n");
        serial_write(b"RUGO: halt ok\n");
        qemu_exit(0x31);
        loop { core::arch::asm!("cli; hlt", options(nomem, nostack)); }
    }

    let app = COMPAT_REAL_APPS[COMPAT_REAL_APP_INDEX];
    serial_write(b"X1APP: launch ");
    serial_write(app.name);
    serial_write(b"\n");

    m3_reset_state();
    crate::net::r4_net_reset(crate::net::R4_NET_NIC_READY);
    for tid in 0..R4_MAX_TASKS {
        R4_TASKS[tid] = R4Task::EMPTY;
    }
    R4_CURRENT = 0;
    R4_NUM_TASKS = 1;
    R4_THREADS_CREATED = 0;

    let entry = match setup_user_elf_pages(app.image) {
        Some(v) => v,
        None => {
            serial_write(b"X1APP: load fail\n");
            qemu_exit(0x33);
            loop { core::arch::asm!("cli; hlt", options(nomem, nostack)); }
        }
    };

    r4_init_task(0, entry, USER_STACK_TOP, 0);
    R4_TASKS[0].state = R4State::Running;
    enter_ring3_at(entry, USER_STACK_TOP);
}

#[cfg(feature = "compat_real_test")]
pub(crate) unsafe fn compat_real_finish_current_app() -> ! {
    let app = COMPAT_REAL_APPS[COMPAT_REAL_APP_INDEX];
    serial_write(b"X1APP: done ");
    serial_write(app.name);
    serial_write(b"\n");
    COMPAT_REAL_APP_INDEX += 1;
    compat_real_enter_current_app();
}
