# Rugo — Top-level Makefile
# Default target: Rust M0 kernel
# Legacy C kernel: make -C legacy build

.PHONY: build image build-panic image-panic build-pf image-pf build-idt image-idt \
       run test-qemu clean legacy docker-all

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

# --- Assembly -----------------------------------------------------------------

$(OUT)/entry.o: arch/x86_64/entry.asm | $(OUT)
	$(NASM) $(NASMFLAGS) $< -o $@

# --- Rust kernel --------------------------------------------------------------

$(KERNEL_LIB): kernel_rs/src/lib.rs kernel_rs/Cargo.toml kernel_rs/.cargo/config.toml
	cd kernel_rs && cargo build --release

# --- Link ---------------------------------------------------------------------

$(OUT)/kernel.elf: $(OUT)/entry.o $(KERNEL_LIB) boot/linker.ld
	$(LD) $(LDFLAGS) -o $@ $(OUT)/entry.o $(KERNEL_LIB)

# --- Panic-test kernel (feature-gated) ----------------------------------------

build-panic: $(OUT)/entry.o boot/linker.ld
	cd kernel_rs && cargo build --release --features panic_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-panic.elf $(OUT)/entry.o $(KERNEL_LIB)

# --- Page-fault-test kernel ---------------------------------------------------

build-pf: $(OUT)/entry.o boot/linker.ld
	cd kernel_rs && cargo build --release --features pf_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-pf.elf $(OUT)/entry.o $(KERNEL_LIB)

# --- IDT-smoke-test kernel ---------------------------------------------------

build-idt: $(OUT)/entry.o boot/linker.ld
	cd kernel_rs && cargo build --release --features idt_smoke_test
	$(LD) $(LDFLAGS) -o $(OUT)/kernel-idt.elf $(OUT)/entry.o $(KERNEL_LIB)

# --- Image / Run / Test -------------------------------------------------------

image: build
	bash tools/mkimage.sh

image-panic: build-panic
	KERNEL_ELF=kernel-panic.elf ISO_NAME=os-panic.iso bash tools/mkimage.sh

image-pf: build-pf
	KERNEL_ELF=kernel-pf.elf ISO_NAME=os-pf.iso bash tools/mkimage.sh

image-idt: build-idt
	KERNEL_ELF=kernel-idt.elf ISO_NAME=os-idt.iso bash tools/mkimage.sh

run: image
	./tools/run_qemu.sh

test-qemu: image image-panic image-pf image-idt
	python3 -m pytest tests/ -v

clean:
	rm -rf $(OUT)
	cd kernel_rs && cargo clean 2>/dev/null || true

# --- Legacy C kernel ----------------------------------------------------------

legacy:
	$(MAKE) -C legacy build

# --- Docker (cross-platform) --------------------------------------------------
DOCKER_IMAGE = rugo-builder

docker-all:
	docker build -t $(DOCKER_IMAGE) .
	docker run --rm -v "$(CURDIR):/src" $(DOCKER_IMAGE) bash -c '\
		find /src -maxdepth 5 -type f \( -name Makefile -o -name "*.c" -o -name "*.h" \
		  -o -name "*.asm" -o -name "*.ld" -o -name "*.sh" -o -name "*.py" \
		  -o -name "*.cfg" -o -name "*.conf" -o -name "*.rs" -o -name "*.toml" \) \
		  -exec sed -i "s/\r$$//" {} + \
		&& make clean build image test-qemu'
