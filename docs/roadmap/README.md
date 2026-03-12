# Roadmap Summary

This is the architecture-first roadmap view. Use it to understand direction.
Use [../../MILESTONES.md](../../MILESTONES.md) for the exhaustive completion
matrix and [../archive/README.md](../archive/README.md) for historical
execution records. Use
[MILESTONE_FRAMEWORK.md](MILESTONE_FRAMEWORK.md) for the full three-track
taxonomy, old-to-new mapping, rename guidance, and archive/foreground rules.
Use
[implementation_closure/README.md](implementation_closure/README.md) for the
"what would literal implementation still require?" companion set covering the
completed execution backlogs.

## Current Phase

The active framing is now three tracks rather than one flat milestone ladder.

| Track | Role | Current phase |
|---|---|---|
| Core Hybrid OS | Main scoreboard. Measures the default Rust-kernel plus Go-service runtime itself. | `C5` complete; next is `C6 Runtime Quality Under Load`. |
| Tooling / Validation / Release Infrastructure | Secondary scoreboard. Measures confidence, qualification, release, and lifecycle discipline around the core lane. | `T4` complete; next is `T5 Advanced Trust and Compliance Infrastructure`. |
| Expansion / Research / Platform Breadth | Secondary scoreboard. Measures compatibility breadth, hardware breadth, desktop breadth, and ecosystem growth. | `X4` complete; next is `X5 Next-Wave Breadth Research`. |

## Implementation Closure Docs

These companion docs cover every backlog-bearing milestone already marked
`done` or `completed` in the flat ledger and translate those closures into a
literal implementation bar:

- [implementation_closure/README.md](implementation_closure/README.md)
- [implementation_closure/core_runtime.md](implementation_closure/core_runtime.md)
- [implementation_closure/tooling_and_release.md](implementation_closure/tooling_and_release.md)
- [implementation_closure/expansion_breadth.md](implementation_closure/expansion_breadth.md)
- [implementation_closure/next_wave_native.md](implementation_closure/next_wave_native.md)

## Observable Core Progress

The repo is closer to its goal only when the default lane can do more of the
following on declared baseline platforms:

- boot from firmware into the Rust kernel and enter Go user space
- run the default Go init/service/shell stack on native kernel primitives
- persist data and perform network I/O through the default service lane
- enforce the process, rights, and isolation model that those services depend on
- survive bounded soak, restart, and containment tests tied to that same lane

## Track Summary

### Core Hybrid OS

- `C1` Kernel Mechanisms Baseline: `M0-M5`
- `C2` Default Go Service Bring-up: `M6`, `M7`, `G1`
- `C3` Contracted Service OS Runtime: `M10`, `M16`, `M25`
- `C4` Durable and Connected Runtime: `M12`, `M13`, `M18`, `M19`
- `C5` Reliable and Isolated Service OS: `M22`, `M42`
- `C6` Runtime Quality Under Load: future core target, likely fed by `M78`,
  `M79`

### Tooling / Validation / Release Infrastructure

- `T1` Experimental Go Port and ABI Qualification: `G2`, `M11`, `M21`
- `T2` Observability, Performance, and Evidence Discipline: `M24`, `M29`,
  `M40`
- `T3` Release and Recovery Infrastructure: `M14`, `M20`, `M30`, `M31`
- `T4` Hardening, Qualification, and Fleet Operations: `M28`, `M32`, `M33`,
  `M34`

### Expansion / Research / Platform Breadth

- `X1` Compatibility Surface Expansion: `M8`, `M17`, `M27`, `M36`, `M41`
- `X2` Hardware, Firmware, and Driver Breadth: `M9`, `M15`, `M23`, `M37`,
  `M43`, `M45-M47`
- `X3` Platform and Ecosystem Feature Breadth: `M26`, `M38`, `M39`
- `X4` Desktop and Workflow Breadth: `M35`, `M44`, `M48-M52`

## Foreground vs Archive

Foreground:

- the three-track scoreboard
- the default Rust-kernel plus Go-service demo path
- the next unfinished core-runtime phase

Archive or de-emphasize:

- flat `M0-M52 done` headlines
- repeated checkpoint strings and latest-GUI callouts
- detailed execution backlogs and closure ledgers as the first impression

Experimental but preserved:

- stock-Go porting work
- extended research roadmap details in `docs/POST_G2_EXTENDED_MILESTONES.md`
