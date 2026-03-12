package main

// sysDebugWrite invokes syscall 0 (sys_debug_write).
func sysDebugWrite(buf *byte, n uintptr) uintptr

// sysThreadSpawn invokes syscall 1 (sys_thread_spawn).
func sysThreadSpawn(entry uintptr) uintptr

// sysThreadExit invokes syscall 2 (sys_thread_exit).
func sysThreadExit() uintptr

// sysYield invokes syscall 3 (sys_yield).
func sysYield() uintptr

// sysIpcSend invokes syscall 8 (sys_ipc_send).
func sysIpcSend(ep uintptr, buf *byte, n uintptr) uintptr

// sysIpcRecv invokes syscall 9 (sys_ipc_recv).
func sysIpcRecv(ep uintptr, buf *byte, cap uintptr) uintptr

// sysTimeNow invokes syscall 10 (sys_time_now).
func sysTimeNow() uintptr

// sysWait invokes syscall 22 (sys_wait).
func sysWait(pid uintptr, status *uintptr, options uintptr) uintptr

// sysSvcRegister invokes syscall 11 (sys_svc_register).
func sysSvcRegister(name *byte, n uintptr, ep uintptr) uintptr

// sysSvcLookup invokes syscall 12 (sys_svc_lookup).
func sysSvcLookup(name *byte, n uintptr) uintptr

// sysIpcEndpointCreate invokes syscall 17 (sys_ipc_endpoint_create).
func sysIpcEndpointCreate() uintptr

// sysSpawnEntry returns the user-mode trampoline for spawned threads.
func sysSpawnEntry() uintptr

// haltForever never returns and is implemented in start.asm.
func haltForever()
