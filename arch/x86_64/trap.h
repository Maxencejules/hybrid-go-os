#ifndef TRAP_H
#define TRAP_H

#include "idt.h"

void trap_handler(struct interrupt_frame *frame);

/* Set by test_trigger_page_fault before faulting; PF handler uses it to recover. */
extern uint64_t pf_recovery_rip;

/* Assembly function that triggers a controlled page fault for testing. */
void test_trigger_page_fault(void);

#endif
