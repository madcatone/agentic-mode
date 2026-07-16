---
name: agentic-bootstrap
description: Bootstrap or adopt the agentic-mode documentation pipeline in any repo — a layered, ID-joined, harness-neutral set of human/agent collaboration docs (AGENTS.md, REQUIREMENTS, USER_GUIDE/API_REFERENCE, VALIDATION, WORKFLOW) plus a config-driven checker and CI gate. Use when the user wants to make a repository legible to any collaborator (human or agent) with no chat history, or asks to set up / adopt agentic mode, doc contracts, or per-feature validation for a project.
---

# Agentic Bootstrap (Claude Code plugin)

This is the **Claude Code plugin wrapper** around the harness-neutral
agentic-mode toolkit. It carries no doctrine of its own — the canonical
protocol, doctrine, templates, and checker are **vendored into this skill
directory** so the skill is fully self-contained (a skill can only read files
under its own directory). The single source of truth remains the agentic-mode
repository; these vendored copies are kept byte-for-byte in sync by
`scripts/sync_plugins.py` in that repo. Never hand-edit the vendored files here
— change the canon upstream and re-sync.

## What ships in this skill directory

```
skills/agentic-bootstrap/
├── SKILL.md                        # this file (the wrapper)
├── RUNBOOK.md                      # the full executable protocol (vendored)
├── reference/BOOTSTRAP-CORE.md     # the doctrine behind every rule (vendored)
├── checker/check_agentic_docs.py   # the config-driven gate (vendored)
├── checker/config.example.json     # annotated config with every knob (vendored)
└── templates/                      # fill-in skeletons for every doc + CI files (vendored)
```

All resources live **inside this directory** — resolve them relative to this
`SKILL.md`, and never reach outside the skill directory with a parent-directory
path. A skill can only read what it vendors.

## What to do when this skill is invoked

1. **Read `RUNBOOK.md`** (in this directory). It is the full executable
   protocol, written for any executor. Its `TOOLKIT` is this skill directory;
   its `TARGET` is the repo the session is working in.
2. **Read `reference/BOOTSTRAP-CORE.md`** before Phase B — it is the doctrine
   behind every rule.
3. **Follow the RUNBOOK exactly:** decide bootstrap vs adopt, run the Phase A
   repo scan + 10-question interview, produce the docs in dependency order with
   each gate passing, copy `checker/check_agentic_docs.py` into the target's
   `scripts/`, place the CI file, and run the checker until it exits clean.
4. **Resolve paths correctly.** The RUNBOOK was authored in the canonical repo,
   so its internal links use the repo's own layout. In this vendored skill the
   mapping is:
   - RUNBOOK's `doctrine/BOOTSTRAP-CORE.md`  →  `reference/BOOTSTRAP-CORE.md` here.
   - RUNBOOK's `checker/…` and `templates/…`  →  same names, in this directory.
   - `doctrine/FIELD-NOTES.md` (war stories) is **not** vendored; read it in the
     canonical agentic-mode repo if you want the origin lessons.
   Generated files always resolve against the working repo (TARGET); nothing is
   ever written into this skill directory (TOOLKIT).

## Dispatch note (Claude Code specific — allowed only here)

*How/Who* — how to split the work across subagents, which model to use, how to
parallelize — is the executor's business and stays out of the generated
contract. If you run this under a commander/subagent operating model, dispatch
the repo scan and the read-back verification to fresh-context subagents, but
keep every *What/Done* fact in the target repo's docs, never in chat. The
generated docs must never name Claude Code, a model, or any harness — that
neutrality is the whole point of the contract.

## Hard rules (inherited from RUNBOOK.md)

- **Harness neutrality (iron rule).** Nothing generated may name a specific
  agent product, model, or proprietary tool. Harness-specific packaging lives
  only in adapters/plugins like this one.
- **Gate before advancing.** Every Phase-B doc passes its inline gate; Phase C
  exits the checker clean before Phase D.
- **The config is the single machine truth.** Every command/path/prefix/limit a
  doc references must match `agentic-mode/config.json`.
