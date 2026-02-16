# Hybrid Go OS — Top-level Makefile
# Targets: build, image, run, test-qemu, clean

.PHONY: build image run test-qemu clean docker-all

# Tools (override via environment, e.g. CC=x86_64-elf-gcc)
NASM    ?= nasm
CC      ?= gcc
GCCGO   ?= gccgo
LD      ?= ld
OBJCOPY ?= objcopy

# Flags
NASMFLAGS = -f elf64
CFLAGS    = -ffreestanding -nostdlib -mno-red-zone -mcmodel=kernel \
            -fno-stack-protector -fno-pic -fno-pie -mno-sse -mno-mmx -mno-sse2 \
            -Wall -Wextra -O2 -c
LDFLAGS   = -nostdlib -static -T boot/linker.ld

# Go flags (gccgo — produces standard ELF objects for kernel linking)
GOFLAGS   = -c -fno-split-stack -fno-pic -fno-pie -mcmodel=kernel -mno-red-zone \
            -mno-sse -mno-mmx -mno-sse2 -O2 -fgo-pkgpath=kernelgo

# User-space flags (no -mcmodel=kernel, freestanding)
USER_CFLAGS  = -ffreestanding -nostdlib -mno-red-zone \
               -fno-stack-protector -fno-pic -fno-pie -mno-sse -mno-mmx -mno-sse2 \
               -Wall -Wextra -O2 -c
USER_LDFLAGS = -nostdlib -static -T user/user.ld

# Output
OUT = out

# Object files
OBJS = $(OUT)/entry.o $(OUT)/isr.o $(OUT)/context.o \
       $(OUT)/main.o $(OUT)/serial.o $(OUT)/string.o \
       $(OUT)/gdt.o $(OUT)/idt.o $(OUT)/trap.o $(OUT)/pmm.o \
       $(OUT)/pic.o $(OUT)/pit.o $(OUT)/sched.o \
       $(OUT)/vmm.o $(OUT)/syscall.o $(OUT)/process.o $(OUT)/user_bins.o \
       $(OUT)/ipc.o $(OUT)/shm.o $(OUT)/service_registry.o \
       $(OUT)/go_entry.o $(OUT)/bridge.o $(OUT)/runtime_stubs.o \
       $(OUT)/pci.o $(OUT)/virtio_blk.o $(OUT)/virtio_net.o

# --- Targets ------------------------------------------------------------------

build: $(OUT)/kernel.elf $(OUT)/hello.bin

$(OUT):
	mkdir -p $(OUT)

# --- User programs ------------------------------------------------------------

$(OUT)/crt0.o: user/crt0.asm | $(OUT)
	$(NASM) $(NASMFLAGS) $< -o $@

$(OUT)/init_user.o: user/init.c user/syscall.h | $(OUT)
	$(CC) $(USER_CFLAGS) $< -o $@

$(OUT)/fault_user.o: user/fault.c | $(OUT)
	$(CC) $(USER_CFLAGS) $< -o $@

$(OUT)/ping_user.o: user/ping.c user/syscall.h | $(OUT)
	$(CC) $(USER_CFLAGS) $< -o $@

$(OUT)/pong_user.o: user/pong.c user/syscall.h | $(OUT)
	$(CC) $(USER_CFLAGS) $< -o $@

$(OUT)/shm_writer_user.o: user/shm_writer.c user/syscall.h | $(OUT)
	$(CC) $(USER_CFLAGS) $< -o $@

$(OUT)/shm_reader_user.o: user/shm_reader.c user/syscall.h | $(OUT)
	$(CC) $(USER_CFLAGS) $< -o $@

$(OUT)/blkdevd_user.o: user/blkdevd.c user/syscall.h | $(OUT)
	$(CC) $(USER_CFLAGS) $< -o $@

$(OUT)/fsd_user.o: user/fsd.c user/syscall.h user/fs_protocol.h | $(OUT)
	$(CC) $(USER_CFLAGS) $< -o $@

$(OUT)/pkg_user.o: user/pkg.c user/syscall.h user/fs_protocol.h | $(OUT)
	$(CC) $(USER_CFLAGS) $< -o $@

$(OUT)/sh_user.o: user/sh.c user/syscall.h user/fs_protocol.h | $(OUT)
	$(CC) $(USER_CFLAGS) $< -o $@

$(OUT)/hello_user.o: user/hello.c user/syscall.h | $(OUT)
	$(CC) $(USER_CFLAGS) $< -o $@

$(OUT)/netd_user.o: user/netd.c user/syscall.h | $(OUT)
	$(CC) $(USER_CFLAGS) $< -o $@

$(OUT)/init.elf: $(OUT)/crt0.o $(OUT)/init_user.o user/user.ld | $(OUT)
	$(LD) $(USER_LDFLAGS) -o $@ $(OUT)/crt0.o $(OUT)/init_user.o

$(OUT)/fault.elf: $(OUT)/crt0.o $(OUT)/fault_user.o user/user.ld | $(OUT)
	$(LD) $(USER_LDFLAGS) -o $@ $(OUT)/crt0.o $(OUT)/fault_user.o

$(OUT)/ping.elf: $(OUT)/crt0.o $(OUT)/ping_user.o user/user.ld | $(OUT)
	$(LD) $(USER_LDFLAGS) -o $@ $(OUT)/crt0.o $(OUT)/ping_user.o

$(OUT)/pong.elf: $(OUT)/crt0.o $(OUT)/pong_user.o user/user.ld | $(OUT)
	$(LD) $(USER_LDFLAGS) -o $@ $(OUT)/crt0.o $(OUT)/pong_user.o

$(OUT)/shm_writer.elf: $(OUT)/crt0.o $(OUT)/shm_writer_user.o user/user.ld | $(OUT)
	$(LD) $(USER_LDFLAGS) -o $@ $(OUT)/crt0.o $(OUT)/shm_writer_user.o

$(OUT)/shm_reader.elf: $(OUT)/crt0.o $(OUT)/shm_reader_user.o user/user.ld | $(OUT)
	$(LD) $(USER_LDFLAGS) -o $@ $(OUT)/crt0.o $(OUT)/shm_reader_user.o

$(OUT)/blkdevd.elf: $(OUT)/crt0.o $(OUT)/blkdevd_user.o user/user.ld | $(OUT)
	$(LD) $(USER_LDFLAGS) -o $@ $(OUT)/crt0.o $(OUT)/blkdevd_user.o

$(OUT)/fsd.elf: $(OUT)/crt0.o $(OUT)/fsd_user.o user/user.ld | $(OUT)
	$(LD) $(USER_LDFLAGS) -o $@ $(OUT)/crt0.o $(OUT)/fsd_user.o

$(OUT)/pkg.elf: $(OUT)/crt0.o $(OUT)/pkg_user.o user/user.ld | $(OUT)
	$(LD) $(USER_LDFLAGS) -o $@ $(OUT)/crt0.o $(OUT)/pkg_user.o

$(OUT)/sh.elf: $(OUT)/crt0.o $(OUT)/sh_user.o user/user.ld | $(OUT)
	$(LD) $(USER_LDFLAGS) -o $@ $(OUT)/crt0.o $(OUT)/sh_user.o

$(OUT)/hello.elf: $(OUT)/crt0.o $(OUT)/hello_user.o user/user.ld | $(OUT)
	$(LD) $(USER_LDFLAGS) -o $@ $(OUT)/crt0.o $(OUT)/hello_user.o

$(OUT)/netd.elf: $(OUT)/crt0.o $(OUT)/netd_user.o user/user.ld | $(OUT)
	$(LD) $(USER_LDFLAGS) -o $@ $(OUT)/crt0.o $(OUT)/netd_user.o

$(OUT)/init.bin: $(OUT)/init.elf
	$(OBJCOPY) -O binary $< $@

$(OUT)/fault.bin: $(OUT)/fault.elf
	$(OBJCOPY) -O binary $< $@

$(OUT)/ping.bin: $(OUT)/ping.elf
	$(OBJCOPY) -O binary $< $@

$(OUT)/pong.bin: $(OUT)/pong.elf
	$(OBJCOPY) -O binary $< $@

$(OUT)/shm_writer.bin: $(OUT)/shm_writer.elf
	$(OBJCOPY) -O binary $< $@

$(OUT)/shm_reader.bin: $(OUT)/shm_reader.elf
	$(OBJCOPY) -O binary $< $@

$(OUT)/blkdevd.bin: $(OUT)/blkdevd.elf
	$(OBJCOPY) -O binary $< $@

$(OUT)/fsd.bin: $(OUT)/fsd.elf
	$(OBJCOPY) -O binary $< $@

$(OUT)/pkg.bin: $(OUT)/pkg.elf
	$(OBJCOPY) -O binary $< $@

$(OUT)/sh.bin: $(OUT)/sh.elf
	$(OBJCOPY) -O binary $< $@

$(OUT)/hello.bin: $(OUT)/hello.elf
	$(OBJCOPY) -O binary $< $@

$(OUT)/netd.bin: $(OUT)/netd.elf
	$(OBJCOPY) -O binary $< $@

$(OUT)/user_bins.o: kernel/user_bins.asm $(OUT)/init.bin $(OUT)/fault.bin $(OUT)/ping.bin $(OUT)/pong.bin $(OUT)/shm_writer.bin $(OUT)/shm_reader.bin $(OUT)/blkdevd.bin $(OUT)/fsd.bin $(OUT)/pkg.bin $(OUT)/sh.bin $(OUT)/netd.bin | $(OUT)
	$(NASM) $(NASMFLAGS) -I$(OUT)/ $< -o $@

# --- Kernel assembly ----------------------------------------------------------

$(OUT)/entry.o: arch/x86_64/entry.asm | $(OUT)
	$(NASM) $(NASMFLAGS) $< -o $@

$(OUT)/isr.o: arch/x86_64/isr.asm | $(OUT)
	$(NASM) $(NASMFLAGS) $< -o $@

$(OUT)/context.o: arch/x86_64/context.asm | $(OUT)
	$(NASM) $(NASMFLAGS) $< -o $@

# --- Kernel C files -----------------------------------------------------------

$(OUT)/main.o: kernel/main.c kernel/serial.h kernel/limine.h kernel/pmm.h kernel/vmm.h kernel/process.h kernel/ipc.h kernel/shm.h kernel/service_registry.h kernel/pci.h kernel/virtio_blk.h kernel/virtio_net.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/serial.o: kernel/serial.c kernel/serial.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/string.o: kernel/string.c | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/pmm.o: kernel/pmm.c kernel/pmm.h kernel/limine.h kernel/serial.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/vmm.o: kernel/vmm.c kernel/vmm.h kernel/pmm.h kernel/limine.h kernel/serial.h kernel/string.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/syscall.o: kernel/syscall.c kernel/syscall.h kernel/serial.h kernel/sched.h kernel/ipc.h kernel/shm.h kernel/service_registry.h kernel/virtio_blk.h kernel/virtio_net.h kernel/process.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/process.o: kernel/process.c kernel/process.h kernel/vmm.h kernel/pmm.h kernel/sched.h kernel/serial.h kernel/string.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/ipc.o: kernel/ipc.c kernel/ipc.h kernel/sched.h kernel/serial.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/shm.o: kernel/shm.c kernel/shm.h kernel/pmm.h kernel/vmm.h kernel/sched.h kernel/serial.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/service_registry.o: kernel/service_registry.c kernel/service_registry.h kernel/serial.h kernel/string.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/pci.o: kernel/pci.c kernel/pci.h kernel/serial.h kernel/io.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/virtio_blk.o: kernel/virtio_blk.c kernel/virtio_blk.h kernel/pci.h kernel/pmm.h kernel/vmm.h kernel/serial.h kernel/io.h kernel/string.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/virtio_net.o: kernel/virtio_net.c kernel/virtio_net.h kernel/pci.h kernel/pmm.h kernel/vmm.h kernel/serial.h kernel/io.h kernel/string.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

# --- Arch C files -------------------------------------------------------------

$(OUT)/gdt.o: arch/x86_64/gdt.c kernel/serial.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/idt.o: arch/x86_64/idt.c kernel/serial.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/trap.o: arch/x86_64/trap.c arch/x86_64/idt.h arch/x86_64/trap.h arch/x86_64/pic.h kernel/serial.h kernel/sched.h kernel/syscall.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/pic.o: arch/x86_64/pic.c arch/x86_64/pic.h kernel/serial.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/pit.o: arch/x86_64/pit.c arch/x86_64/pit.h kernel/serial.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/sched.o: kernel/sched.c kernel/sched.h kernel/serial.h kernel/vmm.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

# --- Go kernel entry (gccgo) -------------------------------------------------

$(OUT)/go_entry.o: kernelgo/entry.go | $(OUT)
	$(GCCGO) $(GOFLAGS) $< -o $@

# --- rtshim (C bridge + runtime stubs) ---------------------------------------

$(OUT)/bridge.o: rtshim/bridge.c kernel/serial.h | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

$(OUT)/runtime_stubs.o: rtshim/runtime_stubs.c | $(OUT)
	$(CC) $(CFLAGS) $< -o $@

# --- Link ---------------------------------------------------------------------

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
