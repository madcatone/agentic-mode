<!--
TEMPLATE: docs/VALIDATION.md — the done-evidence layer. SEED EMPTY at bootstrap.
Filled from config.json (project.name). NO feature blocks at bootstrap — the first block is
appended when the first behavior change lands. Verification commands in each block are COPIED
from AGENTS Development Commands, not reinvented.
Append-only: never rewrite a past block; a reversal APPENDS a new block referencing the old one.
Block ordering: newest at the bottom (matches iteration-history order).
Under the `light` co-op profile these blocks are encouraged, not required.
Harness-neutral: never name a specific agent product, model, or proprietary tool.
-->

# {{COMPONENT_NAME}} — Implementation Validation

Per-feature done evidence. One block per landed non-trivial change. A reviewer (human or agent) re-verifies any feature by running its Verification Commands. Each block cites the stable requirement IDs and the issue/MR-PR number so the ID trail stays followable.

<!--
==== PER-FEATURE BLOCK TEMPLATE — copy below the line when a new feature lands ====

---

## {{FEATURE_NAME}} (issue #{{ISSUE_NUMBER}})   <!-- or (MR !N) / (PR #N) -->

### Code Implementation
- [ ] {{concrete bullet: function/class/module added or changed, with `path` references}}

### Integration Points
- [ ] {{which existing flows were touched; which invariants were preserved}}

### User Requirements Met
- [ ] {{PREFIX}}-0NN {{one-line restatement copied verbatim from REQUIREMENTS}}

### Documentation Updates
- [ ] REQUIREMENTS — {{iteration-history entry appended; which IDs added}}
- [ ] observable-surface doc (USER_GUIDE / API_REFERENCE) — {{command/flag/key/endpoint/API updated}}
- [ ] README — {{quick-start / components / verification updated, or "n/a — no user-visible surface change"}}
- [ ] VALIDATION — this block added

### Testing
- [ ] {{test file}} — {{one-line case description per added test}}
- [ ] {{fixture/example file}} — {{what scenario it captures}}

### Verification Commands
```bash
# Copied from AGENTS Development Commands — do NOT leave a <command> placeholder here.
{{BUILD_CMD}}
{{TEST_CMD}}
{{SMOKE_CMD}}
```

### Status
{{One paragraph: what is covered and any intentional exclusions. If a requirement is only partially met, say so here instead of checking the box.}}

==== END BLOCK TEMPLATE ====
-->
