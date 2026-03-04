"""Deterministic reference model for M8 PR-2 compatibility semantics."""

from dataclasses import dataclass


ELF64_MAGIC = b"\x7fELF"
USER_LIMIT = 0x0000_8000_0000_0000


def _u16_le(buf, off):
    return int.from_bytes(buf[off : off + 2], "little")


def _u32_le(buf, off):
    return int.from_bytes(buf[off : off + 4], "little")


def _u64_le(buf, off):
    return int.from_bytes(buf[off : off + 8], "little")


def validate_elf64_image(image):
    if len(image) < 64:
        return False
    if image[:4] != ELF64_MAGIC:
        return False
    if image[4] != 2 or image[5] != 1 or image[6] != 1:
        return False

    entry = _u64_le(image, 24)
    phoff = _u64_le(image, 32)
    phentsize = _u16_le(image, 54)
    phnum = _u16_le(image, 56)

    if entry == 0 or entry >= USER_LIMIT:
        return False
    if phnum == 0 or phnum > 32:
        return False
    if phentsize < 56:
        return False
    if phoff + phentsize * phnum > len(image):
        return False

    load_count = 0
    for i in range(phnum):
        base = phoff + i * phentsize
        p_type = _u32_le(image, base + 0)
        if p_type != 1:
            continue
        load_count += 1
        p_offset = _u64_le(image, base + 8)
        p_vaddr = _u64_le(image, base + 16)
        p_filesz = _u64_le(image, base + 32)
        p_memsz = _u64_le(image, base + 40)
        p_align = _u64_le(image, base + 48)

        if p_memsz < p_filesz:
            return False
        if p_align != 0 and (p_align & (p_align - 1)) != 0:
            return False
        if p_offset + p_filesz > len(image):
            return False
        if p_vaddr >= USER_LIMIT:
            return False
        if p_vaddr + p_memsz > USER_LIMIT:
            return False

    return load_count > 0


@dataclass
class ProcessImage:
    argv: list
    envp: list
    exited: bool = False
    exit_status: int = 0
    pid: int = 1


class ProcessModel:
    def __init__(self):
        self.proc = ProcessImage(argv=[], envp=[])

    def execve(self, argv, envp):
        if not argv or argv[0] == "":
            return -1
        self.proc = ProcessImage(argv=list(argv), envp=list(envp))
        return 0

    def startup_contract(self):
        argv = self.proc.argv + [None]
        envp = self.proc.envp + [None]
        auxv = [
            ("AT_PHDR", 0x400040),
            ("AT_PHENT", 56),
            ("AT_PHNUM", 1),
            ("AT_PAGESZ", 4096),
            ("AT_ENTRY", 0x400000),
            ("AT_NULL", 0),
        ]
        return {"argv": argv, "envp": envp, "auxv": auxv}

    def exit(self, status):
        self.proc.exited = True
        self.proc.exit_status = status & 0xFF
        return 0

    def waitpid(self, pid, options=0):
        if options != 0:
            return -1, None
        if pid not in (-1, self.proc.pid):
            return -1, None
        if not self.proc.exited:
            return -1, None
        self.proc.exited = False
        return self.proc.pid, self.proc.exit_status


@dataclass
class FdEntry:
    kind: str
    offset: int = 0


class FdTableModel:
    def __init__(self):
        self.entries = {
            0: FdEntry("console"),
            1: FdEntry("console"),
            2: FdEntry("console"),
        }
        self.next_fd = 3
        self.compat_data = b"compat v1 hello\n"
        self.console_log = bytearray()

    def _alloc(self, kind):
        fd = self.next_fd
        while fd in self.entries:
            fd += 1
        if fd >= 16:
            return -1
        self.entries[fd] = FdEntry(kind=kind)
        self.next_fd = fd + 1
        return fd

    def open(self, path):
        if path == "/dev/console":
            return self._alloc("console")
        if path == "/compat/hello.txt":
            return self._alloc("compat_file")
        return -1

    def read(self, fd, length):
        ent = self.entries.get(fd)
        if ent is None or length < 0:
            return -1, b""
        if ent.kind != "compat_file":
            return -1, b""
        data = self.compat_data[ent.offset : ent.offset + length]
        ent.offset += len(data)
        return len(data), data

    def write(self, fd, data):
        ent = self.entries.get(fd)
        if ent is None:
            return -1
        if ent.kind != "console":
            return -1
        self.console_log.extend(data)
        return len(data)

    def close(self, fd):
        if fd < 3:
            return -1
        if fd not in self.entries:
            return -1
        del self.entries[fd]
        return 0

    def poll(self, pollfds):
        ready = 0
        out = []
        for fd, events in pollfds:
            ent = self.entries.get(fd)
            revents = 0
            if ent is None:
                revents = 0x0008  # POLLERR
            elif ent.kind == "console" and events & 0x0004:
                revents = 0x0004  # POLLOUT
            elif (
                ent.kind == "compat_file"
                and events & 0x0001
                and ent.offset < len(self.compat_data)
            ):
                revents = 0x0001  # POLLIN
            if revents:
                ready += 1
            out.append((fd, events, revents))
        return ready, out
