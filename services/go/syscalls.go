package main

import "unsafe"

const (
	taskStateReady = iota
	taskStateRunning
	taskStateBlocked
	taskStateExited
	taskStateDead
)

const (
	schedClassBestEffort = iota
	schedClassCritical
)

type taskInfo struct {
	TID           uint64
	ParentTID     uint64
	State         uint64
	SchedClass    uint64
	DispatchCount uint64
	YieldCount    uint64
	BlockCount    uint64
	IpcSendCount  uint64
	IpcRecvCount  uint64
	EndpointCount uint64
	ShmCount      uint64
	ThreadCount   uint64
	ExitStatus    uint64
}

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

// sysSchedSetRaw invokes syscall 29 (sys_sched_set).
func sysSchedSetRaw(tid uintptr, class uintptr) uintptr

// sysProcInfoRaw invokes syscall 28 (sys_proc_info).
func sysProcInfoRaw(tid uintptr, buf *byte, n uintptr) uintptr

func sysSchedSet(tid uintptr, class uintptr) uintptr {
	return sysSchedSetRaw(tid, class)
}

func sysProcInfo(tid uintptr, info *taskInfo) uintptr {
	return sysProcInfoRaw(
		tid,
		(*byte)(unsafe.Pointer(info)),
		unsafe.Sizeof(*info),
	)
}

// sysSpawnEntry returns the user-mode trampoline for spawned threads.
func sysSpawnEntry() uintptr

// haltForever never returns and is implemented in start.asm.
func haltForever()
