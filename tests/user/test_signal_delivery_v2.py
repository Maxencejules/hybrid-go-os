"""M16 acceptance: deterministic signal delivery model checks."""

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

SIGTERM = 15
SIGKILL = 9
SIGUSR1 = 10


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


@dataclass
class SignalEvent:
    pid: int
    signum: int
    seq: int


class SignalDeliveryModel:
    def __init__(self, max_pending: int = 8):
        self.max_pending = max_pending
        self.pending: list[SignalEvent] = []
        self.seq = 0

    def send(self, pid: int, signum: int) -> int:
        if pid <= 0:
            return -1
        if signum not in (SIGTERM, SIGKILL, SIGUSR1):
            return -1
        if len(self.pending) >= self.max_pending:
            return -1
        self.seq += 1
        self.pending.append(SignalEvent(pid=pid, signum=signum, seq=self.seq))
        return 0

    def deliver_next(self) -> SignalEvent | None:
        if not self.pending:
            return None
        # SIGKILL is terminal and highest priority. Other signals are FIFO.
        kill_idx = next(
            (idx for idx, evt in enumerate(self.pending) if evt.signum == SIGKILL),
            None,
        )
        idx = kill_idx if kill_idx is not None else 0
        return self.pending.pop(idx)


def test_process_thread_model_v2_signal_rules_are_documented():
    doc = _read("docs/abi/process_thread_model_v2.md")
    for token in [
        "Delivery order for normal queued signals is FIFO.",
        "`SIGKILL` is terminal and cannot be masked or deferred.",
        "Queue overflow returns deterministic failure (`-1`)",
    ]:
        assert token in doc


def test_signal_delivery_model_fifo_with_sigkill_override():
    model = SignalDeliveryModel(max_pending=8)
    assert model.send(2, SIGUSR1) == 0
    assert model.send(2, SIGTERM) == 0
    assert model.send(2, SIGKILL) == 0

    first = model.deliver_next()
    second = model.deliver_next()
    third = model.deliver_next()

    assert first is not None and first.signum == SIGKILL
    assert second is not None and second.signum == SIGUSR1
    assert third is not None and third.signum == SIGTERM


def test_signal_delivery_queue_boundaries_and_rejections():
    model = SignalDeliveryModel(max_pending=2)
    assert model.send(2, SIGTERM) == 0
    assert model.send(2, SIGUSR1) == 0
    assert model.send(2, SIGKILL) == -1
    assert model.send(2, 999) == -1
