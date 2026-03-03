package main

// G2 spike user program.
// Emits deterministic markers and exercises core syscall bridges.

const (
	contractGOOS   = "rugo"
	contractGOARCH = "amd64"
)

func main() {
	_ = contractGOOS
	_ = contractGOARCH

	ok := [10]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 'o', 'k', '\n'}
	sysDebugWrite(&ok[0], 10)

	tick1 := sysTimeNow()
	tick2 := sysTimeNow()
	if tick1 == ^uintptr(0) || tick2 == ^uintptr(0) || tick2 <= tick1 {
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
