package kernelgo

// GoKmain is the first Go function called by the kernel.
// Returns a magic value (42) so the C bridge can verify Go executed.
func GoKmain() int64 {
	return 42
}
