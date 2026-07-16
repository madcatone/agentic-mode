---
name: agentic-bootstrap
description: Bootstrap or adopt the agentic-mode documentation pipeline in any repo — a layered, ID-joined, harness-neutral set of human/agent collaboration docs (AGENTS.md, REQUIREMENTS, USER_GUIDE/API_REFERENCE, VALIDATION, WORKFLOW) plus a config-driven checker and CI gate. Use when the user wants to make a repository legible to any collaborator (human or agent) with no chat history, or asks to set up / adopt agentic mode, doc contracts, or per-feature validation for a project.
---

# Agentic Bootstrap (Claude Code adapter)

This is the **Claude Code skill wrapper** around the harness-neutral agentic-mode
toolkit. It carries no doctrine of its own — the canonical protocol, doctrine,
templates, and checker live at the repo root and are the single source of truth.
The wrapper exists only to package that toolkit as a slash-invocable skill; keep
all method changes in the root files and let this adapter stay thin.

## How to package this repo as a Claude Code skill

Copy (or symlink) the agentic-mode repo into a skill directory so Claude Code can
discover it, and add this file as the skill's `SKILL.md`:

```
<plugin>/skills/agentic-bootstrap/
├── SKILL.md                     # this file
├── RUNBOOK.md                   # ← from the repo root
├── doctrine/BOOTSTRAP-CORE.md   # ← from the repo root
├── doctrine/FIELD-NOTES.md      # ← from the repo root
├── templates/                   # ← from the repo root
└── checker/check_agentic_docs.py
```

The simplest faithful packaging is to vendor the whole repo under the skill
directory (a git submodule or a subtree keeps it synced with upstream). Because
this repo is the **canonical source**, always sync downstream from it — never
hand-edit the vendored doctrine/templates/checker and let them drift.

## What to do when this skill is invoked

1. **Read `RUNBOOK.md`** (at the skill root). It is the full executable protocol,
   written for any executor. Its `TOOLKIT` is this skill directory; its `TARGET`
   is the repo the session is working in.
2. **Read `doctrine/BOOTSTRAP-CORE.md`** before Phase B — it is the doctrine
   behind every rule. Skim `doctrine/FIELD-NOTES.md` for the war stories.
3. **Follow the RUNBOOK exactly:** decide bootstrap vs adopt, run the Phase A
   repo scan + 10-question interview, produce the docs in dependency order with
   each gate passing, copy `checker/check_agentic_docs.py` into the target's
   `scripts/`, place the CI file, and run the checker until it exits clean.
4. **Resolve paths correctly:** `templates/…`, `doctrine/…`, `checker/…` resolve
   against this skill directory (TOOLKIT); generated files resolve against the
   working repo (TARGET). Nothing is ever written into TOOLKIT.

## Dispatch note (Claude Code specific — allowed only here)

*How/Who* — how to split the work across subagents, which model to use, how to
parallelize — is the executor's business and stays out of the generated contract.
If you run this under a commander/subagent operating model, dispatch the repo
scan and the read-back verification to fresh-context subagents, but keep every
*What/Done* fact in the target repo's docs, never in chat. The generated docs
must never name Claude Code, a model, or any harness — that neutrality is the
whole point of the contract.

## Hard rules (inherited from RUNBOOK.md)

- **Harness neutrality (iron rule).** Nothing generated may name a specific agent
  product, model, or proprietary tool. Harness-specific packaging lives only in
  adapters like this one.
- **Gate before advancing.** Every Phase-B doc passes its inline gate; Phase C
  exits the checker clean before Phase D.
- **The config is the single machine truth.** Every command/path/prefix/limit a
  doc references must match `agentic-mode/config.json`.
