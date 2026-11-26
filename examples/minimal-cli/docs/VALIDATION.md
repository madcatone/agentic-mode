<!--
Template-Source: agentic-bootstrap/VALIDATION@v2  (@v2: the block template's slots are plain words,
so a rendered seed passes the Phase-C placeholder sweep; a read-back record template sits beside
the block template, and the opening paragraph gains a sentence about the record; no angle-bracket
token remains in the file; the ID example uses three digits; the record template's instructions
sit above its fill-in lines)
-->

# todo — Implementation Validation

Per-feature done evidence. One block per landed non-trivial change. A reviewer
(human or agent) re-verifies any feature by running its Verification Commands.
Each block cites the stable `TODO-NNN` IDs and the issue/PR number so the ID
trail stays followable. A read-back record (`agentic-mode/SELF-TEST.md`, section
D) is appended at the bottom with the record template. Append-only: never
rewrite a past block.

**Post-merge evidence clause.** Evidence that exists only after merge — deployments,
live previews — may be backfilled into the same block's Status subsection via a small
chore PR: limited to adding a post-merge entry or replacing that block's explicit
"unverified / pending" wording, and it must cite the original PR/MR. Every other
subsection stays append-only. This is the only declared exception to "never rewrite
a past block."

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
The heading cites the issue/MR/PR number. Use exactly one of (issue #N), (MR !N), or (PR #N). A doc-set upgrade that no issue or MR/PR covers cites its commit instead, as (commit 1a2b3c4).
A slot in this template is a plain word or phrase with no marker around it. Replace each slot when you copy the block, and check a box that holds.

---

## FEATURE_NAME (issue #ISSUE_NUMBER)

### Code Implementation
- [ ] concrete bullet: function, class, or module added or changed, with `path` references

### Integration Points
- [ ] which existing flows were touched; which invariants were preserved

### User Requirements Met
- [ ] TODO-NNN one-line restatement copied verbatim from REQUIREMENTS

### Documentation Updates
- [ ] REQUIREMENTS — iteration-history entry appended; which IDs added
- [ ] Observable surface — command / flag / key / endpoint / API updated wherever the surface is documented, in its doc's subsection or in the requirement row while no surface doc is seeded
- [ ] README — quick-start / components / verification updated, or "n/a — no user-visible surface change"
- [ ] VALIDATION — this block added

### Testing
- [ ] test file — one-line case description per added test
- [ ] fixture or example file — what scenario it captures

### Verification Commands
```bash
# Copied from AGENTS Development Commands.
python3 -m py_compile todo.py
python3 todo.py add "smoke task" && python3 todo.py list
```

### Status
One paragraph: what is covered and any intentional exclusions. If a requirement is only partially met, say so here instead of checking the box. Post-merge evidence entries land here, per the post-merge clause in the header.

==== END BLOCK TEMPLATE ====

==== READ-BACK RECORD TEMPLATE — append at the bottom when a read-back runs (SELF-TEST §D) ====

Replace every slot below. DATE is the ISO date. SCOPE is `bootstrap`, `adoption`, `doc-set upgrade`,
or the name of the change that was read back. There is one Question line per question, and a failure
names the gap instead of a citation. A probe that could not run gets the Probe line alone.
## Read-back — DATE (SCOPE)

- Reader: who or what read back, with no chat history.
- Question 1: pass, answered from file:section.
- Probe not run: the reason.

==== END READ-BACK RECORD TEMPLATE ====
-->

## Read-back — 2026-11-27 (template re-port)

- Reader: a fresh-context reader with no chat history, from the docs alone.
- Question 1: pass, answered from `README.md` opening paragraph and `README.md:Quick Start` (Add and list tasks).
- Question 2: pass, answered from `AGENTS.md:Stop-and-Ask (do NOT proceed silently)` and `docs/WORKFLOW.md:0. Iron Rules (apply in every context)`.
- Question 3: pass, answered from `docs/REQUIREMENTS.md:Functional Requirements`, row TODO-001.
- Question 4: pass, answered from `docs/USER_GUIDE.md:Command Reference` (TODO-003).
- Question 5: pass, answered from `AGENTS.md:Change Flow (What "Done" Requires)` and `AGENTS.md:Sign-Off Points`; review in `docs/WORKFLOW.md:5. Push and PR`.
