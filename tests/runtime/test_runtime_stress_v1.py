"""M11 acceptance: runtime maturity stress baselines."""


def test_go_std_runtime_markers_v1(qemu_serial_go_std):
    """Stock-Go runtime marker path must remain deterministic."""
    out = qemu_serial_go_std.stdout
    assert "GOSTD: ok" in out, f"Missing GOSTD marker. Got:\n{out}"
    assert "GOSTD: time ok" in out, f"Missing time marker. Got:\n{out}"
    assert "GOSTD: yield ok" in out, f"Missing yield marker. Got:\n{out}"
    assert "GOSTD: vm ok" in out, f"Missing vm marker. Got:\n{out}"
    assert "GOSTD: spawn child ok" in out, f"Missing spawn-child marker. Got:\n{out}"
    assert "GOSTD: spawn main ok" in out, f"Missing spawn-main marker. Got:\n{out}"
    assert "THREAD_EXIT: ok" in out, f"Missing thread-exit marker. Got:\n{out}"
    assert "RUGO: halt ok" in out, f"Missing clean halt marker. Got:\n{out}"
    assert "GOSTD: spawn err" not in out, f"Unexpected spawn error marker. Got:\n{out}"


def test_runtime_syscall_and_pressure_baselines(
    qemu_serial_stress_syscall,
    qemu_serial_pressure_shm,
):
    """Runtime lane keeps stress syscall and pressure baselines green."""
    syscall_out = qemu_serial_stress_syscall.stdout
    pressure_out = qemu_serial_pressure_shm.stdout
    assert "STRESS: syscall ok" in syscall_out, (
        f"Missing stress-syscall marker. Got:\n{syscall_out}"
    )
    assert "PRESSURE: shm ok" in pressure_out, (
        f"Missing shm-pressure marker. Got:\n{pressure_out}"
    )


def test_runtime_thread_and_vm_baselines(qemu_serial_thread_spawn, qemu_serial_vm_map):
    """Runtime-facing thread/vm primitives remain stable."""
    spawn_out = qemu_serial_thread_spawn.stdout
    vm_out = qemu_serial_vm_map.stdout
    assert "SPAWN: child ok" in spawn_out, f"Missing spawn child marker. Got:\n{spawn_out}"
    assert "SPAWN: main ok" in spawn_out, f"Missing spawn main marker. Got:\n{spawn_out}"
    assert "SPAWN: spawn err" not in spawn_out, (
        f"Unexpected spawn error marker. Got:\n{spawn_out}"
    )
    assert "VM: map ok" in vm_out, f"Missing vm map marker. Got:\n{vm_out}"
    assert "VM: map err" not in vm_out, f"Unexpected vm map error marker. Got:\n{vm_out}"
