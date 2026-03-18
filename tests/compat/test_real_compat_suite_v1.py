"""Runtime-backed compatibility corpus v1 serial checks."""


def _assert_in_order(out: str, markers: list[str]) -> None:
    pos = -1
    for marker in markers:
        idx = out.find(marker, pos + 1)
        assert idx != -1, f"missing marker {marker!r}. Got:\n{out}"
        pos = idx


def test_runtime_corpus_executes_real_elf_apps(qemu_serial_compat_real):
    out = qemu_serial_compat_real.stdout
    _assert_in_order(
        out,
        [
            "X1APP: launch x1-cli-file",
            "X1CLI: start",
            "X1CLI: file ok",
            "X1APP: done x1-cli-file",
            "X1APP: launch x1-proc-sock",
            "X1PROC: start",
            "X1PROC: child ok",
            "X1PROC: wait ok",
            "X1SOCK: ok",
            "X1DEFER: ok",
            "X1APP: done x1-proc-sock",
            "X1: suite ok",
            "RUGO: halt ok",
        ],
    )

    for marker in [
        "X1CLI: fail",
        "X1PROC: fail",
        "X1APP: load fail",
        "R4: deadlock",
    ]:
        assert marker not in out, f"unexpected failure marker {marker!r}. Got:\n{out}"
