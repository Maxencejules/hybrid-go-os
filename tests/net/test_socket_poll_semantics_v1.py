"""M12 acceptance: socket poll and blocking baseline semantics."""

import importlib.util
from pathlib import Path


_COMPAT_MODEL_PATH = Path(__file__).resolve().parents[1] / "compat" / "v1_model.py"
_SPEC = importlib.util.spec_from_file_location("compat_v1_model", _COMPAT_MODEL_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)
SocketModel = _MOD.SocketModel


def test_stream_poll_read_write_readiness():
    model = SocketModel()
    srv = model.socket("AF_INET", "SOCK_STREAM")
    cli = model.socket("AF_INET", "SOCK_STREAM")
    assert model.bind(srv, ("10.0.2.15", 7101)) == 0
    assert model.listen(srv, backlog=2) == 0
    assert model.connect(cli, ("10.0.2.15", 7101)) == 0
    acc_fd, _peer = model.accept(srv)
    assert acc_fd >= 3

    ready0, events0 = model.poll([(cli, 0x0004), (acc_fd, 0x0004)])
    assert ready0 == 2
    assert events0[0][2] == 0x0004
    assert events0[1][2] == 0x0004

    assert model.send(cli, b"abc") == 3
    ready1, events1 = model.poll([(acc_fd, 0x0001)])
    assert ready1 == 1
    assert events1[0][2] == 0x0001


def test_invalid_fd_sets_pollerr():
    model = SocketModel()
    ready, events = model.poll([(1234, 0x0001)])
    assert ready == 1
    assert events[0][2] == 0x0008


def test_shutdown_write_clears_pollout():
    model = SocketModel()
    fd = model.socket("AF_INET", "SOCK_DGRAM")
    peer = model.socket("AF_INET", "SOCK_DGRAM")
    assert model.bind(fd, ("10.0.2.15", 7201)) == 0
    assert model.bind(peer, ("10.0.2.15", 7202)) == 0
    assert model.shutdown(fd, 1) == 0
    ready, events = model.poll([(fd, 0x0004)])
    assert ready == 0
    assert events[0][2] == 0
