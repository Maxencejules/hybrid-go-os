package main

// Minimal Go user program for Rugo G1.
// Prints "GOUSR: ok\n" via sys_debug_write (syscall 0) and halts.

func main() {
	msg := [10]byte{'G', 'O', 'U', 'S', 'R', ':', ' ', 'o', 'k', '\n'}
	sysDebugWrite(&msg[0], 10)
}

// sysDebugWrite invokes syscall 0 (sys_debug_write).
// Defined in syscall_amd64.S.
func sysDebugWrite(buf *byte, n uintptr) uintptr

// sysIpcSend invokes syscall 8 (sys_ipc_send).
func sysIpcSend(ep uintptr, buf *byte, n uintptr) uintptr

// sysIpcRecv invokes syscall 9 (sys_ipc_recv).
func sysIpcRecv(ep uintptr, buf *byte, cap_ uintptr) uintptr

// sysSvcLookup invokes syscall 12 (sys_svc_lookup).
func sysSvcLookup(name *byte, n uintptr) uintptr
