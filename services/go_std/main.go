package main

// G2 spike user program.
// Emits "GOSTD: ok" so the acceptance path can exercise a std-port candidate lane.

const (
	contractGOOS   = "rugo"
	contractGOARCH = "amd64"
)

func main() {
	_ = contractGOOS
	_ = contractGOARCH
	msg := [10]byte{'G', 'O', 'S', 'T', 'D', ':', ' ', 'o', 'k', '\n'}
	sysDebugWrite(&msg[0], 10)
}

// sysDebugWrite invokes syscall 0 (sys_debug_write).
func sysDebugWrite(buf *byte, n uintptr) uintptr
