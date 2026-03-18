"""Runtime-backed compatibility corpus v1 doc and wiring checks."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def test_runtime_corpus_artifacts_exist():
    required = [
        "docs/abi/compat_runtime_corpus_v1.md",
        "docs/abi/compat_profile_v2.md",
        "docs/abi/compat_profile_v3.md",
        "docs/abi/compat_profile_v4.md",
        "docs/abi/compat_profile_v5.md",
        "docs/M8_EXECUTION_BACKLOG.md",
        "docs/M17_EXECUTION_BACKLOG.md",
        "docs/M27_EXECUTION_BACKLOG.md",
        "docs/M36_EXECUTION_BACKLOG.md",
        "docs/M41_EXECUTION_BACKLOG.md",
        "tests/compat/test_real_compat_docs_v1.py",
        "tests/compat/test_real_compat_suite_v1.py",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), f"missing runtime corpus artifact: {rel}"


def test_runtime_corpus_doc_declares_required_tokens():
    doc = _read("docs/abi/compat_runtime_corpus_v1.md")
    for token in [
        "Runtime compatibility corpus ID: `rugo.compat_runtime_corpus.v1`.",
        "Image: `out/os-compat-real.iso`",
        "Local gate: `make test-real-compat-runtime-v1`",
        "`x1-cli-file`",
        "`x1-proc-sock`",
        "`sys_thread_spawn` + `sys_wait`",
        "`fork` syscall slot `43` returns `-1`",
        "`clone` syscall slot `44` returns `-1`",
        "`epoll` syscall slot `45` returns `-1`",
        "`PKG: elf ok`",
    ]:
        assert token in doc


def test_runtime_corpus_is_wired_into_makefile_and_profiles():
    makefile = _read("Makefile")
    for token in [
        "test-real-compat-runtime-v1",
        "image-compat-real",
        "tests/compat/test_real_compat_docs_v1.py",
        "tests/compat/test_real_compat_suite_v1.py",
    ]:
        assert token in makefile

    for relpath in [
        "docs/abi/compat_profile_v2.md",
        "docs/abi/compat_profile_v3.md",
        "docs/abi/compat_profile_v4.md",
        "docs/abi/compat_profile_v5.md",
    ]:
        doc = _read(relpath)
        assert "docs/abi/compat_runtime_corpus_v1.md" in doc
        assert "test-real-compat-runtime-v1" in doc


def test_runtime_corpus_backlog_docs_record_the_addendum():
    for relpath in [
        "docs/M8_EXECUTION_BACKLOG.md",
        "docs/M17_EXECUTION_BACKLOG.md",
        "docs/M27_EXECUTION_BACKLOG.md",
        "docs/M36_EXECUTION_BACKLOG.md",
        "docs/M41_EXECUTION_BACKLOG.md",
    ]:
        doc = _read(relpath)
        assert "X1 runtime-backed closure addendum (2026-03-18)" in doc
        assert "runtime-backed compatibility corpus" in doc
