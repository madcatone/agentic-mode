# todo

A tiny standard-library task tracker. It is the worked example for the
agentic-mode documentation contract: a small but complete repo whose docs pass
the coherence gate, so you can read a real filled-in contract end to end.

**Requirements:** Python 3.8+ — no third-party packages.

## Pick a Tool / Entry Point

| Want | Use | Install |
| --- | --- | --- |
| Track tasks from the shell | `todo.py` | none — standard library |

## What This Repository Contains

- `todo.py`: the CLI entry point (add / list / done / remove).
- `docs/`: the behavior contract, user guide, validation evidence, and workflow.
- `agentic-mode/`: the machine config and the cross-layer self-test.

This example is project-neutral: no hardcoded brands, hosts, IPs, or absolute
machine paths. The store path is supplied at runtime via `--store` or `TODO_STORE`.

## Quick Start

### Add and list tasks

```bash
python3 todo.py add "write the docs"
python3 todo.py list
```

### Complete and remove

```bash
python3 todo.py done 1
python3 todo.py remove 1
```

## Agent Onboarding Guide

A cold-start collaborator (human or agent, no chat history) reads in this order:
this README → `AGENTS.md` → `docs/REQUIREMENTS.md` → `docs/USER_GUIDE.md` →
`docs/VALIDATION.md` → `docs/WORKFLOW.md`. Questions to answer before editing
command behavior: which `TODO-XXX` requirement governs the command? does the
store format change (TODO-001)? which user-guide table row and validation block
must move with it? Safe-change pattern: edit code → update the requirement ID +
iteration history → update the user guide → append a validation block → run the
docs gate.

## Verification

```bash
python3 -m py_compile todo.py
python3 todo.py list
# Docs coherence gate (ID continuity, command-surface consistency, neutrality)
python3 ../../checker/check_agentic_docs.py --config agentic-mode/config.json
```

## Project-Neutrality Checklist

- No brand names / codenames / hardcoded packages / serials / IPs / machine paths.
- Runtime inputs (the store path) are supplied via `--store` or `TODO_STORE`.

## Doc Cross-Links

- Behavior contract: `docs/REQUIREMENTS.md`
- Observable surface: `docs/USER_GUIDE.md`
- Validation: `docs/VALIDATION.md`
- Workflow: `docs/WORKFLOW.md`
- Resident index: `AGENTIC-MODE.md`
