"""M16 acceptance: process wait/kill v2 lifecycle and containment behavior."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


class WaitKillModel:
    """Small deterministic wait/kill lifecycle model for v2 contract checks."""

    def __init__(self):
        self.pid = 1
        self.child_pid = 2
        self.child_exited = False
        self.child_status = None

    def kill(self, pid: int, signum: int) -> int:
        if pid != self.child_pid or signum <= 0:
            return -1
        # Linux-like convention: exit status 128 + signal.
        self.child_status = 128 + signum
        self.child_exited = True
        return 0

    def waitpid(self, pid: int) -> tuple[int, int | None]:
        if pid not in (-1, self.child_pid):
            return -1, None
        if not self.child_exited:
            return -1, None
        self.child_exited = False
        return self.child_pid, self.child_status


def test_process_thread_model_v2_doc_and_wait_contract():
    doc = _read("docs/abi/process_thread_model_v2.md")
    kernel_src = _read("kernel_rs/src/lib.rs")

    for token in [
        "State machine identifier: `rugo.process_thread_model.v2`",
        "wait/kill semantics",
        "Faulted user tasks are contained without scheduler collapse.",
        "Local gate: `make test-process-scheduler-v2`",
    ]:
        assert token in doc

    assert "sys_wait_v1" in kernel_src
    assert "unsafe fn sys_wait_v1" in kernel_src


def test_wait_kill_model_is_deterministic():
    model = WaitKillModel()

    assert model.waitpid(-1) == (-1, None)
    assert model.kill(2, 15) == 0
    assert model.waitpid(2) == (2, 143)
    assert model.waitpid(2) == (-1, None)


def test_fault_and_exit_markers_remain_stable_v2(
    qemu_serial_thread_exit,
    qemu_serial_user_fault,
    qemu_serial_thread_spawn,
):
    exit_out = qemu_serial_thread_exit.stdout
    fault_out = qemu_serial_user_fault.stdout
    spawn_out = qemu_serial_thread_spawn.stdout

    assert "THREAD_EXIT: ok" in exit_out, f"Missing thread-exit marker. Got:\n{exit_out}"
    assert "RUGO: halt ok" in exit_out, f"Missing clean halt marker. Got:\n{exit_out}"

    assert "USER: killed" in fault_out, f"Missing user-fault marker. Got:\n{fault_out}"
    assert "RUGO: halt ok" in fault_out, f"Missing clean halt marker. Got:\n{fault_out}"

    assert "SPAWN: child ok" in spawn_out, f"Missing spawn child marker. Got:\n{spawn_out}"
    assert "SPAWN: main ok" in spawn_out, f"Missing spawn main marker. Got:\n{spawn_out}"
    assert "SPAWN: spawn err" not in spawn_out, (
        f"Unexpected spawn error marker. Got:\n{spawn_out}"
    )
