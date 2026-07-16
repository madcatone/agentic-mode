# todo — Implementation Validation

Per-feature done evidence. One block per landed non-trivial change. A reviewer
(human or agent) re-verifies any feature by running its Verification Commands.
Each block cites the stable `TODO-NNN` IDs and the issue/PR number so the ID
trail stays followable. Append-only: never rewrite a past block.

---

## Core task verbs (PR #1)

### Code Implementation
- [x] `todo.py` — `cmd_add`, `cmd_list`, `cmd_done`, `cmd_remove`, and the
  `_store_path` / `_load` / `_save` helpers.

### Integration Points
- [x] Single JSON store shared by every subcommand; store resolution centralized
  in `_store_path` so all verbs agree on the target file.

### User Requirements Met
- [x] TODO-001 store path from `--store`, else `TODO_STORE`, else `tasks.json`.
- [x] TODO-002 `add` appends a task with an increasing id and prints it.
- [x] TODO-003 `list` shows open tasks, or all with `--all`.
- [x] TODO-004 `done` marks a task complete or reports a missing id.
- [x] TODO-005 `remove` deletes a task or reports a missing id.

### Documentation Updates
- [x] REQUIREMENTS — iteration history entries 1–2 appended; TODO-001..TODO-005 added.
- [x] USER_GUIDE — command reference and output format documented.
- [x] README — quick start covers add / list / done / remove.
- [x] VALIDATION — this block added.

### Verification Commands
```bash
python3 -m py_compile todo.py
python3 todo.py add "smoke task" && python3 todo.py list
```

### Status
All five requirements are covered by the current entry point. Due dates,
priorities, and tags are intentionally out of scope (see REQUIREMENTS Non-Goals).

### Read-back
- 2026-07-16 — cold-reader read-back of the five canonical questions passed
  against the committed docs alone; no doc gaps found.

<!--
==== PER-FEATURE BLOCK TEMPLATE — copy below the line when a new feature lands ====

---

## FEATURE_NAME (PR #N)

### Code Implementation
- [ ] concrete bullet: function/class/module added or changed, with `path` references

### User Requirements Met
- [ ] TODO-0NN one-line restatement copied from REQUIREMENTS

### Documentation Updates
- [ ] REQUIREMENTS — iteration-history entry appended; which IDs added
- [ ] USER_GUIDE — command / flag / output updated
- [ ] README — quick start / verification updated, or "n/a"
- [ ] VALIDATION — this block added

### Verification Commands
```bash
python3 -m py_compile todo.py
python3 todo.py list
```

### Status
One paragraph: what is covered and any intentional exclusions.

==== END BLOCK TEMPLATE ====
-->
