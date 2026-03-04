"""M8 PR-2 loader compatibility checks."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from v1_model import validate_elf64_image


def _minimal_valid_elf64():
    image = bytearray(64 + 56)
    image[0:4] = b"\x7fELF"
    image[4] = 2  # ELFCLASS64
    image[5] = 1  # little-endian
    image[6] = 1  # ELF version
    image[16:18] = (2).to_bytes(2, "little")  # ET_EXEC
    image[18:20] = (62).to_bytes(2, "little")  # EM_X86_64
    image[20:24] = (1).to_bytes(4, "little")
    image[24:32] = (0x400000).to_bytes(8, "little")  # e_entry
    image[32:40] = (64).to_bytes(8, "little")  # e_phoff
    image[52:54] = (64).to_bytes(2, "little")  # e_ehsize
    image[54:56] = (56).to_bytes(2, "little")  # e_phentsize
    image[56:58] = (1).to_bytes(2, "little")  # e_phnum

    # PT_LOAD phdr
    ph = 64
    image[ph + 0 : ph + 4] = (1).to_bytes(4, "little")  # p_type
    image[ph + 4 : ph + 8] = (5).to_bytes(4, "little")  # p_flags
    image[ph + 8 : ph + 16] = (0).to_bytes(8, "little")  # p_offset
    image[ph + 16 : ph + 24] = (0x400000).to_bytes(8, "little")  # p_vaddr
    image[ph + 24 : ph + 32] = (0x400000).to_bytes(8, "little")  # p_paddr
    image[ph + 32 : ph + 40] = (64).to_bytes(8, "little")  # p_filesz
    image[ph + 40 : ph + 48] = (64).to_bytes(8, "little")  # p_memsz
    image[ph + 48 : ph + 56] = (0x1000).to_bytes(8, "little")  # p_align
    return bytes(image)


def test_loader_model_accepts_valid_elf64():
    assert validate_elf64_image(_minimal_valid_elf64()) is True


def test_loader_model_rejects_bad_segment_shape():
    image = bytearray(_minimal_valid_elf64())
    ph = 64
    image[ph + 32 : ph + 40] = (128).to_bytes(8, "little")  # p_filesz
    image[ph + 40 : ph + 48] = (64).to_bytes(8, "little")  # p_memsz (invalid)
    assert validate_elf64_image(bytes(image)) is False


def test_loader_doc_and_kernel_contract(read_repo_file):
    process_doc = read_repo_file("docs/abi/process_thread_model_v1.md")
    kernel_src = read_repo_file("kernel_rs/src/lib.rs")

    assert "## ELF loader policy v1" in process_doc
    assert "AT_PHDR" in process_doc
    assert "AT_ENTRY" in process_doc
    assert "fn elf_v1_validate_image" in kernel_src
    assert "ELF_V1_MAX_PHNUM" in kernel_src
