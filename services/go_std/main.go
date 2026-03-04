package main

import "unsafe"

// G2 spike user program.
// Emits deterministic markers and exercises core syscall bridges.

const (
	contractGOOS   = "rugo"
	contractGOARCH = "amd64"
	sysErr         = ^uintptr(0)
	vmTestAddr     = uintptr(0x500000)
	vmTestSize     = uintptr(0x1000)
)

func main() {
	_ = contractGOOS
	_ = contractGOARCH

	ok := [10]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 'o', 'k', '\n'}
	sysDebugWrite(&ok[0], 10)

	tick1 := sysTimeNow()
	tick2 := sysTimeNow()
	if tick1 == sysErr || tick2 == sysErr || tick2 <= tick1 {
		errMsg := [16]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 't', 'i', 'm', 'e', ' ', 'e', 'r', 'r', '\n'}
		sysDebugWrite(&errMsg[0], 16)
		return
	}

	timeOK := [15]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 't', 'i', 'm', 'e', ' ', 'o', 'k', '\n'}
	sysDebugWrite(&timeOK[0], 15)

	if sysYield() != 0 {
		errMsg := [17]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 'y', 'i', 'e', 'l', 'd', ' ', 'e', 'r', 'r', '\n'}
		sysDebugWrite(&errMsg[0], 17)
		return
	}

	yieldOK := [16]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 'y', 'i', 'e', 'l', 'd', ' ', 'o', 'k', '\n'}
	sysDebugWrite(&yieldOK[0], 16)

	if sysVmMap(vmTestAddr, vmTestSize) == sysErr {
		errMsg := [14]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 'v', 'm', ' ', 'e', 'r', 'r', '\n'}
		sysDebugWrite(&errMsg[0], 14)
		return
	}
	*(*byte)(unsafe.Pointer(vmTestAddr)) = 0x5A
	if sysVmUnmap(vmTestAddr, vmTestSize) == sysErr {
		errMsg := [14]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 'v', 'm', ' ', 'e', 'r', 'r', '\n'}
		sysDebugWrite(&errMsg[0], 14)
		return
	}
	if sysVmMap(vmTestAddr+1, vmTestSize) != sysErr {
		errMsg := [14]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 'v', 'm', ' ', 'e', 'r', 'r', '\n'}
		sysDebugWrite(&errMsg[0], 14)
		return
	}
	if sysVmMap(vmTestAddr, vmTestSize) == sysErr {
		errMsg := [14]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 'v', 'm', ' ', 'e', 'r', 'r', '\n'}
		sysDebugWrite(&errMsg[0], 14)
		return
	}
	*(*byte)(unsafe.Pointer(vmTestAddr)) = 0x6B
	if sysVmUnmap(vmTestAddr, vmTestSize) == sysErr {
		errMsg := [14]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 'v', 'm', ' ', 'e', 'r', 'r', '\n'}
		sysDebugWrite(&errMsg[0], 14)
		return
	}

	vmOK := [13]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 'v', 'm', ' ', 'o', 'k', '\n'}
	sysDebugWrite(&vmOK[0], 13)

	entry := sysSpawnEntry()
	if entry == 0 || sysThreadSpawn(entry) == sysErr {
		errMsg := [17]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 's', 'p', 'a', 'w', 'n', ' ', 'e', 'r', 'r', '\n'}
		sysDebugWrite(&errMsg[0], 17)
		return
	}
	if sysYield() != 0 {
		errMsg := [17]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 'y', 'i', 'e', 'l', 'd', ' ', 'e', 'r', 'r', '\n'}
		sysDebugWrite(&errMsg[0], 17)
		return
	}

	spawnMainOK := [21]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 's', 'p', 'a', 'w', 'n', ' ', 'm', 'a', 'i', 'n', ' ', 'o', 'k', '\n'}
	sysDebugWrite(&spawnMainOK[0], 21)

	// Expected to terminate the task and not return.
	sysThreadExit()
	exitErr := [16]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 'e', 'x', 'i', 't', ' ', 'e', 'r', 'r', '\n'}
	sysDebugWrite(&exitErr[0], 16)
}

// sysDebugWrite invokes syscall 0 (sys_debug_write).
func sysDebugWrite(buf *byte, n uintptr) uintptr

// sysTimeNow invokes syscall 10 (sys_time_now).
func sysTimeNow() uintptr

// sysYield invokes syscall 3 (sys_yield).
func sysYield() uintptr

// sysThreadExit invokes syscall 2 (sys_thread_exit).
func sysThreadExit() uintptr

// sysThreadSpawn invokes syscall 1 (sys_thread_spawn).
func sysThreadSpawn(entry uintptr) uintptr

// sysVmMap invokes syscall 4 (sys_vm_map).
func sysVmMap(vaddr uintptr, size uintptr) uintptr

// sysVmUnmap invokes syscall 5 (sys_vm_unmap).
func sysVmUnmap(vaddr uintptr, size uintptr) uintptr

// sysSpawnEntry returns the entry address for the spawned thread trampoline.
func sysSpawnEntry() uintptr
