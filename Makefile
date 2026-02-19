# Rugo — Top-level Makefile
# Default target: Rust M0 kernel
# Legacy C kernel: make -C legacy build

.PHONY: build image build-panic image-panic build-pf image-pf build-idt image-idt \
       build-sched image-sched \
       build-user-hello image-user-hello build-syscall image-syscall \
       build-syscall-invalid image-syscall-invalid \
       build-user-fault image-user-fault \
       build-ipc image-ipc build-ipc-badptr-send image-ipc-badptr-send \
       build-ipc-badptr-svc image-ipc-badptr-svc \
       build-ipc-buffer-full image-ipc-buffer-full \
       build-ipc-svc-overwrite image-ipc-svc-overwrite \
       build-shm image-shm \
       build-blk image-blk \
       build-blk-invariants image-blk-invariants \
       build-fs image-fs \
       build-net image-net \
       build-go image-go \
       run test-qemu clean legacy docker-all docker-legacy

# Tools
NASM    ?= nasm
LD      ?= ld

# Flags
NASMFLAGS = -f elf64
LDFLAGS   = -nostdlib -static -T boot/linker.ld

# Output
OUT = out

# Rust kernel staticlib
CARGO_TARGET = x86_64-unknown-none
KERNEL_LIB   = kernel_rs/target/$(CARGO_TARGET)/release/librugo_kernel.a

# --- Targets ------------------------------------------------------------------

build: $(OUT)/kernel.elf

$(OUT):
	mkdir -p $(OUT)

# Assembly objects
ASM_OBJS = $(OUT)/entry.o $(OUT)/isr.o $(OUT)/context.o

# --- Assembly -----------------------------------------------------------------

$(OUT)/entry.o: arch/x86_64/entry.asm | $(OUT)
	$(NASM) $(NASMFLAGS) $< -o $@

$(OUT)/isr.o: arch/x86_64/isr.asm | $(OUT)
	$(NASM) $(NASMFLAGS) $< -o $@

$(OUT)/context.o: arch/x86_64/context.asm | $(OUT)
	$(NASM) $(NASMFLAGS) $< -o $@

# --- Rust kernel --------------------------------------------------------------

$(KERNEL_LIB): kernel_rs/src/lib.rs kernel_rs/Cargo.toml kernel_rs/.cargo/config.toml
	cd kernel_rs && cargo build --release

# --- Link ---------------------------------------------------------------------

$(OUT)/kernel.elf: $(ASM_OBJS) $(KERNEL_LIB) boot/linker.ld
	$(LD) $(LDFLAGS) -o $@ $(ASM_OBJS) $(KERNEL_LIB)

# --- Panic-test kernel (feature-gated) ----------------------------------------

build-panic: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features panic_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-panic.elf $(ASM_OBJS) $(KERNEL_LIB)

# --- Page-fault-test kernel ---------------------------------------------------

build-pf: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features pf_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-pf.elf $(ASM_OBJS) $(KERNEL_LIB)

# --- IDT-smoke-test kernel ---------------------------------------------------

build-idt: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features idt_smoke_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-idt.elf $(ASM_OBJS) $(KERNEL_LIB)

# --- Scheduler-test kernel ----------------------------------------------------

build-sched: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features sched_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-sched.elf $(ASM_OBJS) $(KERNEL_LIB)

# --- M3: User-hello-test kernel -----------------------------------------------

build-user-hello: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features user_hello_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-user-hello.elf $(ASM_OBJS) $(KERNEL_LIB)

# --- M3: Syscall-test kernel --------------------------------------------------

build-syscall: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features syscall_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-syscall.elf $(ASM_OBJS) $(KERNEL_LIB)

# --- M3: Invalid-syscall-test kernel ------------------------------------------

build-syscall-invalid: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features syscall_invalid_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-syscall-invalid.elf $(ASM_OBJS) $(KERNEL_LIB)

# --- M3: User-fault-test kernel -----------------------------------------------

build-user-fault: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features user_fault_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-user-fault.elf $(ASM_OBJS) $(KERNEL_LIB)

# --- R4: IPC ping-pong test kernel -------------------------------------------

build-ipc: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features ipc_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-ipc.elf $(ASM_OBJS) $(KERNEL_LIB)

# --- R4: IPC bad-pointer send test kernel ------------------------------------

build-ipc-badptr-send: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features ipc_badptr_send_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-ipc-badptr-send.elf $(ASM_OBJS) $(KERNEL_LIB)

# --- R4: IPC bad-pointer service registry test kernel ------------------------

build-ipc-badptr-svc: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features ipc_badptr_svc_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-ipc-badptr-svc.elf $(ASM_OBJS) $(KERNEL_LIB)

# --- R4: IPC buffer-full test kernel ------------------------------------------

build-ipc-buffer-full: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features ipc_buffer_full_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-ipc-buffer-full.elf $(ASM_OBJS) $(KERNEL_LIB)

# --- R4: SVC overwrite test kernel -------------------------------------------

build-ipc-svc-overwrite: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features svc_overwrite_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-ipc-svc-overwrite.elf $(ASM_OBJS) $(KERNEL_LIB)

# --- R4: SHM bulk test kernel ------------------------------------------------

build-shm: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features shm_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-shm.elf $(ASM_OBJS) $(KERNEL_LIB)

# --- M5: VirtIO block test kernel ---------------------------------------------

build-blk: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features blk_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-blk.elf $(ASM_OBJS) $(KERNEL_LIB)

# --- Image / Run / Test -------------------------------------------------------

image: build
	bash tools/mkimage.sh

image-panic: build-panic
	KERNEL_ELF=kernel-panic.elf ISO_NAME=os-panic.iso bash tools/mkimage.sh

image-pf: build-pf
	KERNEL_ELF=kernel-pf.elf ISO_NAME=os-pf.iso bash tools/mkimage.sh

image-idt: build-idt
	KERNEL_ELF=kernel-idt.elf ISO_NAME=os-idt.iso bash tools/mkimage.sh

image-sched: build-sched
	KERNEL_ELF=kernel-sched.elf ISO_NAME=os-sched.iso bash tools/mkimage.sh

image-user-hello: build-user-hello
	KERNEL_ELF=kernel-user-hello.elf ISO_NAME=os-user-hello.iso bash tools/mkimage.sh

image-syscall: build-syscall
	KERNEL_ELF=kernel-syscall.elf ISO_NAME=os-syscall.iso bash tools/mkimage.sh

image-syscall-invalid: build-syscall-invalid
	KERNEL_ELF=kernel-syscall-invalid.elf ISO_NAME=os-syscall-invalid.iso bash tools/mkimage.sh

image-user-fault: build-user-fault
	KERNEL_ELF=kernel-user-fault.elf ISO_NAME=os-user-fault.iso bash tools/mkimage.sh

image-ipc: build-ipc
	KERNEL_ELF=kernel-ipc.elf ISO_NAME=os-ipc.iso bash tools/mkimage.sh

image-shm: build-shm
	KERNEL_ELF=kernel-shm.elf ISO_NAME=os-shm.iso bash tools/mkimage.sh

image-ipc-badptr-send: build-ipc-badptr-send
	KERNEL_ELF=kernel-ipc-badptr-send.elf ISO_NAME=os-ipc-badptr-send.iso bash tools/mkimage.sh

image-ipc-badptr-svc: build-ipc-badptr-svc
	KERNEL_ELF=kernel-ipc-badptr-svc.elf ISO_NAME=os-ipc-badptr-svc.iso bash tools/mkimage.sh

image-ipc-buffer-full: build-ipc-buffer-full
	KERNEL_ELF=kernel-ipc-buffer-full.elf ISO_NAME=os-ipc-buffer-full.iso bash tools/mkimage.sh

image-ipc-svc-overwrite: build-ipc-svc-overwrite
	KERNEL_ELF=kernel-ipc-svc-overwrite.elf ISO_NAME=os-ipc-svc-overwrite.iso bash tools/mkimage.sh

image-blk: build-blk
	KERNEL_ELF=kernel-blk.elf ISO_NAME=os-blk.iso bash tools/mkimage.sh

# --- M5: VirtIO block init invariants test kernel -----------------------------

build-blk-invariants: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features blk_invariants_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-blk-invariants.elf $(ASM_OBJS) $(KERNEL_LIB)

image-blk-invariants: build-blk-invariants
	KERNEL_ELF=kernel-blk-invariants.elf ISO_NAME=os-blk-invariants.iso bash tools/mkimage.sh

# --- M6: Filesystem test kernel + disk image ---------------------------------

build-fs: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features fs_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-fs.elf $(ASM_OBJS) $(KERNEL_LIB)

image-fs: build-fs
	python3 tools/mkfs.py $(OUT)/fs-test.img
	KERNEL_ELF=kernel-fs.elf ISO_NAME=os-fs.iso bash tools/mkimage.sh

# --- M7: VirtIO net test kernel -----------------------------------------------

build-net: $(ASM_OBJS) boot/linker.ld
	cd kernel_rs && cargo build --release --features net_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-net.elf $(ASM_OBJS) $(KERNEL_LIB)

image-net: build-net
	KERNEL_ELF=kernel-net.elf ISO_NAME=os-net.iso bash tools/mkimage.sh

# --- G1: TinyGo user-space test kernel ----------------------------------------

build-go: $(ASM_OBJS) boot/linker.ld
	bash tools/build_go.sh
	cd kernel_rs && cargo build --release --features go_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-go.elf $(ASM_OBJS) $(KERNEL_LIB)

image-go: build-go
	KERNEL_ELF=kernel-go.elf ISO_NAME=os-go.iso bash tools/mkimage.sh

run: image
	./tools/run_qemu.sh

test-qemu: image image-panic image-pf image-idt image-sched image-user-hello image-syscall image-syscall-invalid image-user-fault image-ipc image-ipc-badptr-send image-ipc-badptr-svc image-ipc-buffer-full image-ipc-svc-overwrite image-shm image-blk image-blk-invariants image-fs image-net image-go
	python3 -m pytest tests/ -v

clean:
	rm -rf $(OUT)
	cd kernel_rs && cargo clean 2>/dev/null || true

# --- Legacy C kernel ----------------------------------------------------------

legacy:
	$(MAKE) -C legacy build

# --- Docker (cross-platform) --------------------------------------------------
DOCKER_IMAGE = rugo-builde

docker-all:
	docker build -t $(DOCKER_IMAGE) .
	docker run --rm -v "$(CURDIR):/src" $(DOCKER_IMAGE) bash -c '\
		find /src -maxdepth 5 -type f \( -name Makefile -o -name "*.c" -o -name "*.h" \
		  -o -name "*.asm" -o -name "*.ld" -o -name "*.sh" -o -name "*.py" \
		  -o -name "*.cfg" -o -name "*.conf" -o -name "*.rs" -o -name "*.toml" \) \
		  -exec sed -i "s/\r$$//" {} + \
		&& make clean build image test-qemu'

docker-legacy:
	docker build -t $(DOCKER_IMAGE) .
	docker run --rm -v "$(CURDIR):/src" $(DOCKER_IMAGE) bash -c '\
		find /src -maxdepth 5 -type f \( -name Makefile -o -name "*.c" -o -name "*.h" \
		  -o -name "*.asm" -o -name "*.ld" -o -name "*.sh" -o -name "*.py" \
		  -o -name "*.cfg" -o -name "*.conf" -o -name "*.go" \) \
		  -exec sed -i "s/\r$$//" {} + \
		&& make -C legacy clean build image test-qemu'
