# Postmortem Triage Playbook v1

Status: draft  
Version: v1

## Workflow

1. Capture panic dump artifact.
2. Symbolize with release symbol map.
3. Attach triage summary and root-cause classification.
4. Link remediation and regression test IDs.

## Retention

- Dumps and symbol maps are retained per release policy.
- Triage bundles must be reproducible from stored artifacts.

## Evidence

- Gate: `test-crash-dump-v1`.

