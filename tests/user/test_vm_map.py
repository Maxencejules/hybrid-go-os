"""M3 acceptance test: sys_vm_map/sys_vm_unmap map and unmap a user page."""


def test_vm_map(qemu_serial_vm_map):
    """vm_map/vm_unmap should pass aligned page map/unmap and reject bad args."""
    out = qemu_serial_vm_map.stdout
    assert "VM: map ok" in out, f"Missing 'VM: map ok'. Got:\n{out}"
    assert "VM: map err" not in out, f"Unexpected 'VM: map err'. Got:\n{out}"
