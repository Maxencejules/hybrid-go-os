# Hybrid Go OS — Top-level Makefile
# Targets: build, image, run, test-qemu, clean

.PHONY: build image run test-qemu clean

build:
	@echo "TODO: build kernel + userland"
	@echo "  - Compile arch/x86_64 ASM stubs"
	@echo "  - Build Go kernel"
	@echo "  - Build freestanding C userland"

image: build
	@echo "TODO: produce out/os.iso"
	@echo "  - Package kernel ELF with Limine bootloader"
	@echo "  - Generate ISO image at out/os.iso"

run: image
	./tools/run_qemu.sh

test-qemu: image
	@echo "TODO: run QEMU test harness"
	@echo "  - Boot QEMU headless"
	@echo "  - Parse serial output for expected markers"
	@echo "  - Exit with non-zero on failure"

clean:
	rm -rf out/
