<!--
TEMPLATE: docs/VALIDATION.md — the done-evidence layer. SEED EMPTY at bootstrap.
Filled from config.json (project.name, id.prefix) and the Phase-A answers (BUILD_CMD, TEST_CMD,
SMOKE_CMD), which resolve inside the block template. NO feature blocks at bootstrap — the first
block is appended when the first behavior change lands. The read-back record (RUNBOOK Phase C,
step 5) is the one other entry this file holds.
The slots inside the two record templates are plain words with no marker around them. The Phase-C
sweep leaves no double brace in a rendered file, so a slot that is filled only when a block or a
record is appended cannot use the brace form. Leave every slot as it is.
Verification commands in each block are COPIED from AGENTS Development Commands, not reinvented.
Append-only: never rewrite a past block; a reversal APPENDS a new block referencing the old one.
Block ordering: newest at the bottom (matches iteration-history order).
Blocks and read-back records share that order.
Under the `light` co-op profile these blocks are encouraged, not required.
Harness-neutral: never name a specific agent product, model, or proprietary tool.
Template-Source: agentic-bootstrap/VALIDATION@v2  (@v2: the block template's slots are plain words,
so a rendered seed passes the Phase-C placeholder sweep; a read-back record template sits beside
the block template, and the opening paragraph gains a sentence about the record; no angle-bracket
token remains in the file; the ID example uses three digits; the record template's instructions
sit above its fill-in lines)
Rendered copies keep the Template-Source lines in a comment at the top of the file; the rest of this header is not rendered.
-->

# {{COMPONENT_NAME}} — Implementation Validation

Per-feature done evidence. One block per landed non-trivial change. A reviewer (human or agent) re-verifies any feature by running its Verification Commands. Each block cites the stable requirement IDs and the issue/MR/PR number so the ID trail stays followable. A read-back record (`agentic-mode/SELF-TEST.md`, section D) is appended at the bottom with the record template.

**Post-merge evidence clause.** Evidence that exists only after merge — deployments, live previews — may be backfilled into the same block's Status subsection via a small chore PR: limited to adding a post-merge entry or replacing that block's explicit "unverified / pending" wording, and it must cite the original PR/MR. Every other subsection stays append-only. This is the only declared exception to "never rewrite a past block."

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
- [ ] {{PREFIX}}-NNN one-line restatement copied verbatim from REQUIREMENTS

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
{{BUILD_CMD}}
{{TEST_CMD}}
{{SMOKE_CMD}}
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
