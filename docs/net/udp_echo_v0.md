# UDP Echo v0

## Lane

Rugo (Rust no_std kernel). M7 milestone (optional).

## Overview

A minimal VirtIO net driver and kernel-side UDP echo demo. The guest
receives a UDP packet on port 7, echoes it back, and prints a
deterministic marker to serial.

## What is implemented

- **VirtIO net driver** (legacy transport, polling)
  - PCI scan for virtio-net device (vendor 0x1AF4, device 0x1000)
  - Two virtqueues: RX (queue 0) and TX (queue 1)
  - Single pre-posted RX buffer (4 KiB)
  - Single TX buffer (4 KiB) with polling completion
  - Reads MAC address from device config
  - No feature negotiation (no offloading, no MRG_RXBUF)

- **Protocol handling** (kernel-side, no user-mode netd)
  - ARP request → ARP reply (for guest IP only)
  - IPv4/UDP to port 7 → echo reply with swapped addresses/ports
  - IP header checksum recalculation (RFC 1071)
  - UDP checksum zeroed (valid for IPv4)

- **Net syscalls** (raw frame, documented for future user-mode use)
  - `sys_net_send` (syscall 15): send raw Ethernet frame
  - `sys_net_recv` (syscall 16): receive raw Ethernet frame (non-blocking)

## What is NOT implemented

- TCP or any transport protocol beyond UDP echo
- IP fragmentation or reassembly
- DHCP (guest IP is hardcoded to 10.0.2.15)
- ARP cache
- Multiple connections or sockets
- Interrupt-driven I/O (polling only)
- User-mode networking service (netd)
- Any form of routing

## Packet assumptions

- Ethernet II framing (no 802.1Q, no jumbo frames)
- IPv4 only, no options expected (but IHL is parsed correctly)
- UDP destination port 7 (echo service)
- Maximum frame size: 1514 bytes (no jumbo)
- Guest IP: 10.0.2.15 (QEMU SLIRP default)
- Guest MAC: read from VirtIO device config

## QEMU configuration

```
-netdev user,id=n0,hostfwd=udp::PORT-10.0.2.15:7
-device virtio-net-pci,netdev=n0,disable-modern=on
```

## Test

`tests/net/test_udp_echo.py` boots `out/os-net.iso`, sends a UDP
packet from the host to the forwarded port, and asserts `NET: udp echo`
appears in serial output.
