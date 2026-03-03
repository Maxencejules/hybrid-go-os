; G2 std-port spike assembly aggregator.
; Keep build entrypoint stable while splitting startup/syscall/runtime hooks.

%include "services/go_std/rt0.asm"
%include "services/go_std/syscalls.asm"
%include "services/go_std/runtime_stubs.asm"
