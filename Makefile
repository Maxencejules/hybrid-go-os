# Hybrid Go OS — Top-level Makefile
# Targets: build, image, run, test-qemu, clean

.PHONY: build image run test-qemu clean docker-all

# Tools (override via environment, e.g. CC=x86_64-elf-gcc)
NASM  ?= nasm
CC    ?= gcc
LD    ?= ld

# Flags
NASMFLAGS = -f elf64
CFLAGS    = -ffreestanding -nostdlib -mno-red-zone -mcmodel=kernel \
            -fno-stack-protector -fno-pic -fno-pie -mno-sse -mno-mmx -mno-sse2 \
            -Wall -Wextra -O2 -c
LDFLAGS   = -nostdlib -static -T boot/linker.ld

# Output
OUT = out

# Object files
OBJS = $(OUT)/entry.o $(OUT)/isr.o \
       $(OUT)/main.o $(OUT)/serial.o $(OUT)/string.o \
       $(OUT)/gdt.o $(OUT)/idt.o $(OUT)/trap.o $(OUT)/pmm.o

# --- Targets ------------------------------------------------------------------

build: $(OUT)/kernel.elf

$(OUT):
	mkdir -p $(OUT)

# Assembly
$(OUT)/entry.o: arch/x86_64/entry.asm | $(OUT)
	$(NASM) $(NASMFLAGS) $< -o $@

$(OUT)/isr.o: arch/x86_64/isr.asm | $(OUT)
	$(NASM) $(NASMFLAGS) $< -o $@

# Kernel C files
$(OUT)/main.o: kernel/main.c kernel/serial.h kernel/limine.h kernel/pmm.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/serial.o: kernel/serial.c kernel/serial.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/string.o: kernel/string.c | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/pmm.o: kernel/pmm.c kernel/pmm.h kernel/limine.h kernel/serial.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

# Arch C files
$(OUT)/gdt.o: arch/x86_64/gdt.c kernel/serial.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/idt.o: arch/x86_64/idt.c kernel/serial.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/trap.o: arch/x86_64/trap.c arch/x86_64/idt.h arch/x86_64/trap.h kernel/serial.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

# Link
$(OUT)/kernel.elf: $(OBJS) boot/linker.ld
	$(LD) $(LDFLAGS) -o $@ $(OBJS)

image: build
	bash tools/mkimage.sh

run: image
	./tools/run_qemu.sh

test-qemu: image
	python3 -m pytest tests/ -v

clean:
	rm -rf $(OUT)

# --- Docker (Windows / cross-platform) ---------------------------------------
DOCKER_IMAGE = hybrid-go-os-builder

docker-all:
	docker build -t $(DOCKER_IMAGE) .
	docker run --rm -v "$(CURDIR):/src" $(DOCKER_IMAGE) bash -c '\
		find /src -maxdepth 4 -type f \( -name Makefile -o -name "*.c" -o -name "*.h" \
		  -o -name "*.asm" -o -name "*.ld" -o -name "*.sh" -o -name "*.py" \
		  -o -name "*.cfg" -o -name "*.conf" \) -exec sed -i "s/\r$$//" {} + \
		&& make clean build image test-qemu'
