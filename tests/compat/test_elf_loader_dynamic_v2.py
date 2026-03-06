"""M17 PR-1: dynamic ELF loader policy checks for v2 profile."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent))

from v2_model import (  # noqa: E402
    ElfImageV2,
    ElfLoaderV2Model,
    R_X86_64_RELATIVE,
    RelocationV2,
    SegmentV2,
)


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_loader_v2_accepts_static_exec_image():
    model = ElfLoaderV2Model()
    image = ElfImageV2(
        elf_type="ET_EXEC",
        entry=0x401000,
        segments=(
            SegmentV2("PT_LOAD", vaddr=0x400000, memsz=0x3000, filesz=0x2400),
        ),
    )
    assert model.validate(image) == (True, "OK")


def test_loader_v2_accepts_dynamic_image_with_relative_relocs():
    model = ElfLoaderV2Model()
    image = ElfImageV2(
        elf_type="ET_DYN",
        entry=0x1200,
        interpreter="/lib/rugo-ld.so.1",
        segments=(
            SegmentV2("PT_LOAD", vaddr=0x1000, memsz=0x4000, filesz=0x3000),
            SegmentV2("PT_DYNAMIC", vaddr=0x2C00, memsz=0x200, filesz=0x200),
            SegmentV2("PT_INTERP", vaddr=0x1800, memsz=0x40, filesz=0x20),
        ),
        relocations=(
            RelocationV2(R_X86_64_RELATIVE, offset=0x2100),
            RelocationV2(R_X86_64_RELATIVE, offset=0x2A10),
        ),
    )
    assert model.validate(image) == (True, "OK")


def test_loader_v2_rejects_dynamic_image_without_supported_interp():
    model = ElfLoaderV2Model()
    image = ElfImageV2(
        elf_type="ET_DYN",
        entry=0x1200,
        interpreter=None,
        segments=(
            SegmentV2("PT_LOAD", vaddr=0x1000, memsz=0x4000, filesz=0x3000),
            SegmentV2("PT_DYNAMIC", vaddr=0x2C00, memsz=0x200, filesz=0x200),
        ),
        relocations=(RelocationV2(R_X86_64_RELATIVE, offset=0x2100),),
    )
    assert model.validate(image) == (False, "E_UNSUP")


def test_loader_v2_rejects_unsupported_relocation_kind():
    model = ElfLoaderV2Model()
    image = ElfImageV2(
        elf_type="ET_DYN",
        entry=0x1200,
        interpreter="/lib/rugo-ld.so.1",
        segments=(
            SegmentV2("PT_LOAD", vaddr=0x1000, memsz=0x4000, filesz=0x3000),
            SegmentV2("PT_DYNAMIC", vaddr=0x2C00, memsz=0x200, filesz=0x200),
            SegmentV2("PT_INTERP", vaddr=0x1800, memsz=0x40, filesz=0x20),
        ),
        relocations=(RelocationV2(reloc_type=1, offset=0x2100),),
    )
    assert model.validate(image) == (False, "E_UNSUP")


def test_loader_contract_doc_declares_dynamic_policy():
    doc = _read("docs/abi/elf_loader_contract_v2.md")
    for token in [
        "Loader contract identifier: `rugo.elf_loader_contract.v2`.",
        "Dynamic ELF (`ET_DYN`) is accepted when interpreter and relocation constraints",
        "Only `R_X86_64_RELATIVE` relocations are supported.",
        "Unsupported relocation kinds must fail with deterministic unsupported error.",
    ]:
        assert token in doc

