<!--
Template-Source: agentic-bootstrap/REQUIREMENTS@v3  (@v2: the Event Model heading is one
descriptive slot; the two Iteration History entries are samples and the history starts empty;
the superseded-row note shows a three-digit ID; the rule that superseded rows stay is a
rendered sentence.
@v3: the no-surface stand-in also allows a page in place of a command, and the header states
what a target with no entry point does; the IF branches are unchanged, so a copy rendered
with a surface doc needs no port)
-->

# todo — Requirements and Evolution

The behavior contract for the `todo` example CLI. Every functional requirement
carries a stable `TODO-NNN` ID; the observable-surface doc, the validation
blocks, and commit/PR notes cite those IDs. IDs are never renumbered.

## Problem

Small personal task lists live in scattered notes and shell history, so they are
easy to lose and impossible to script against. `todo` gives a single, plain-text
JSON store with a tiny, predictable command surface — nothing to install beyond
a Python 3 interpreter.

## Goals

- Track a flat list of tasks in one JSON file chosen by the caller.
- Cover the four verbs a task list actually needs: add, list, done, remove.
- Stay standard-library only, so the tool runs anywhere Python 3 does.

## Non-Goals

- No due dates, priorities, tags, or sub-tasks (a later component may add them).
- No sync, server, or multi-user access — the store is a local file.
- No interactive UI; the surface is one-shot subcommands.

## Current User Flows

```bash
python3 todo.py add "write the requirements doc"
python3 todo.py list
python3 todo.py done 1
python3 todo.py list --all
python3 todo.py remove 1
```

## Functional Requirements

Each row states one behavior. Its observable surface is documented in
`docs/USER_GUIDE.md`, which cites the row's ID.

| ID | Requirement |
| --- | --- |
| TODO-001 | The tool shall persist tasks as a JSON array in a store path taken from `--store`, else the `TODO_STORE` environment variable, else `tasks.json`. |
| TODO-002 | The `add` command shall append a task with a monotonically increasing integer id and print the assigned id. |
| TODO-003 | The `list` command shall print open tasks by default and all tasks (including completed) when given `--all`. |
| TODO-004 | The `done` command shall mark the task with the given id complete, or report that no such task exists. |
| TODO-005 | The `remove` command shall delete the task with the given id, or report that no such task exists. |

Rows are never deleted. A superseded row stays, marked for example as "(superseded by TODO-NNN)".

## Task Store Model

```text
tasks.json := [ {id: int, text: str, done: bool}, ... ]
add    -> append {next_id, text, done=false}
done   -> set done=true where id matches
remove -> drop the entry where id matches
```

## Iteration History
<!-- APPEND-ONLY. Newest entry has the highest number. Never edit a past entry. -->
1. Seeded the contract with the four core verbs and the store-resolution rule (TODO-001..TODO-005). Store format frozen as a flat JSON array so `jq` can read it without a schema. Establishes the behavior baseline (PR #1).
2. Confirmed `list` hides completed tasks unless `--all` is passed, matching the "open work first" default; verified against the fixture flows above (TODO-003, PR #2).

## Acceptance Criteria

- `todo.py` byte-compiles.
- The command flows under Current User Flows produce the expected output on a fresh store.
- Documentation is updated when a command, flag, or output changes.

## Verification Commands

```bash
python3 -m py_compile todo.py
python3 todo.py add "smoke task" && python3 todo.py list
```
