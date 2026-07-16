---
trigger: manual
---

# Agentic Bootstrap (Devin IDE adapter)

This is the **Devin IDE rule** that lands the agentic-mode toolkit as a
repo-local, manually-triggered workflow. It carries no doctrine of its own — the
canonical protocol, doctrine, templates, and checker live in the agentic-mode
repo and are the single source of truth. Keep this adapter thin; sync any method
change from upstream rather than editing it here.

## How to install this in a Devin-driven repo

Devin IDE reads loose Markdown under `.devin/`. Vendor the agentic-mode repo into
the target (a submodule or subtree keeps it synced with upstream), then place this
file as a rule:

```
.devin/
├── rules/agentic-mode.md        # this file (trigger: manual)
└── workflows/review.md          # the review workflow adapter
<vendored>/agentic-mode/         # RUNBOOK.md, doctrine/, templates/, checker/
```

Because the agentic-mode repo is the **canonical source**, always sync downstream
from it — never hand-edit the vendored doctrine/templates/checker and let them
drift.

## What to do when this rule is triggered

1. **Read `RUNBOOK.md`** from the vendored agentic-mode repo. It is the full
   executable protocol. Its `TOOLKIT` is the vendored repo; its `TARGET` is the
   repo you are working in.
2. **Read `doctrine/BOOTSTRAP-CORE.md`** before Phase B; skim
   `doctrine/FIELD-NOTES.md`.
3. **Follow the RUNBOOK exactly:** decide bootstrap vs adopt; run the Phase A
   repo scan + 10-question interview; produce docs in dependency order with each
   gate passing; copy `checker/check_agentic_docs.py` into `scripts/`; place the
   CI file; run the checker until it exits clean; do the placeholder sweep.
4. **Resolve paths correctly:** `templates/…`, `doctrine/…`, `checker/…` resolve
   against the vendored repo (TOOLKIT); generated files resolve against the
   working repo (TARGET). Nothing is written into TOOLKIT.

## Ground rules (inherited from RUNBOOK.md)

- **Harness neutrality (iron rule).** Nothing generated may name a specific agent
  product, model, or proprietary tool — including this IDE. Harness-specific
  packaging lives only in adapters like this one.
- **Never advance past a failed gate.** If the same check fails after two fix
  attempts, stop and escalate with the failure trail.
- **The config is the single machine truth.** Every command/path/prefix/limit a
  doc references must match `agentic-mode/config.json`.
- **Verification is not self-assessment.** Completion is proven by the checker's
  objective output or a fresh-context read-back, never by "looks fine."

## Done means

The checker exits 0 in the target repo, the placeholder sweep finds nothing, and
the hand-off summary states the daily loop: edit code → update the requirement ID
in REQUIREMENTS → update the surface doc citing that ID → append a VALIDATION
block → run the checker → follow `docs/WORKFLOW.md`.
